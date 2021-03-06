import abc
import frontends
import logging
from protocol.clientprotocol.ttypes import RedirectionInfo
from protocol.clientprotocol import Redirection
from protocol import Proxy
from protocol.ttypes import Identity, Annotated, IdentityType, IdentityAttribute, IdentityAttributeType, StateVar, StateVarsAttribute, CallSiteSetAttribute, PortConfiguration
from protocol.ttypes import CallSite as TCallSite
from util import thriftutil
from util import lrustore
import datetime
from util import serialization
#from util.js import Unknown, unwrap
from util.eval import Unknown, unwrap
#from pyv8 import PyV8
import socket

logger = logging.getLogger(__name__)

network_bytes = open('bytes', 'w')
network_bytes.truncate()

class ProxyApplication(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, redirector):
        self.terminal = Terminal()
        #self.client_proxies = []
        #self.server_proxies = []
        self.redirector = redirector
        self.bytesperop = {}
        self.timeperop = {}
        self.services = lrustore.LruStore()
        self.ghostsperop = {}
        self.interpreters = {}
        self.client_actuals = []
        self.name = None
        self.proxy_ports = {}

    def register_interpreter(self, nm, config):
        self.terminal.register_interpreter(nm, config)

    def lookup_proxy_port(self, proxy_port):
        return self.proxy_ports.get(proxy_port, None)

    def lookup_service(self, identifier):
        # bl = identifier.partition('?')[0]
        res = self.services.get(identifier, [])
        if len(res) == 0:
            return (False, None)
        if len([s for s in res if s.service_name == res[0].service_name]) != len(res):
            return (False, res)
        candidate = res[0]
        #res += self.services.get(identifier.partition('?')[0], [])
        for s in res:
            if s.proxy_type == 'server':
                candidate = s
        if not candidate.proxy_endpoint:
            prime = self.services.get(identifier.partition('?')[0], [])
            if len(prime) > 0:
                candidate.proxy_endpoint = prime[0].proxy_endpoint
        return (True, candidate)

    def in_conflict(self, identifier):
        (is_ok, _) = self.lookup_service(identifier)
        return not is_ok

    def register_proxy(self, proxy_config):
        if proxy_config['type'] == 'client':
            if proxy_config['actual'] in self.client_actuals:
                return
            else:
                self.client_actuals.append(proxy_config['actual'])
        (s, terminus) = self.terminal.generate_terminus(proxy_config)
        if s.is_proxied():
            self.proxy_ports[s.actual_endpoint] = s.proxy_endpoint
        s.proxy_type = proxy_config['type']
        return self.register_service(s, terminus)

    def register_service(self, s, terminus):
        if s.proxy_type == 'server':
            proxy = ServerProxy(self, s, terminus)
            #self.server_proxies.append(proxy)
            terminus.set_proxy(proxy)
            proxy.accept_proxied_requests()
            return proxy
        elif s.proxy_type == 'client':
            proxy = ClientProxy(self, s, terminus)
            #self.client_proxies.append(proxy)
            terminus.set_proxy(proxy)
            proxy.accept_unproxied_requests()
            return proxy
        else:
            raise ValueError("unknown proxy type: %s" % proxy_config['type'])

    @abc.abstractmethod
    def before_client(self, callsite):
        logger.debug("before_client %s" % callsite)
        return []

    @abc.abstractmethod
    def before_server(self, callsite, client_attributes, proxies=[]):
        logger.debug("before_server %s %s" % (callsite, client_attributes))
        pass

    @abc.abstractmethod
    def after_server(self, callsite):
        logger.debug("after_server %s" % callsite)
        return []

    @abc.abstractmethod
    def after_client(self, callsite, server_attributes, proxies=[]):
        logger.debug("after_client %s %s" % (callsite, server_attributes))
        pass

class Attribute(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, identity, dependencies = []):
        self.identity = identity
        self.dependencies = dependencies

    def add_dep(self, dep):
        found = False
        for mydep in self.dependencies:
            if mydep == dep:
                found = True
        if not found:
            self.dependencies.append(dep)

    @abc.abstractmethod
    def get_attribute_type(self):
        pass

    @abc.abstractmethod
    def merge(self, attribute):
        pass

    @abc.abstractmethod
    def to_thrift_object(self):
        pass

class CallSiteSet(Attribute):
    def __init__(self, id, cs):
        super(CallSiteSet, self).__init__(id)
        if cs:
            self.dependencies = [cs.receiver]
        self.callsites = [cs]

    def to_js(self):
        return self

    def add_callsite(self, cs):
        self.deps += cs.receiver
        self.callsites += [cs]

    def merge(self, attribute):
        for ocs in attribute.callsites:
            found = False
            for cs in self.callsites:
                if cs == ocs:
                    found = True
            if not found:
                self.callsites.append(ocs)

    def __eq__(self, other):
        if other == None:
            return False
        return self.identity == other.identity

    def __ne__(self, other):
        if other == None:
            return False
        return self.identity != other.identity


    def prettyprint(self, cs):
        args = ", ".join([str(serialization.deserialize_python(arg)) for arg in cs.arguments])
        return "%s %s :: %s(%s)" % (cs.receiver.name, cs.receiver.identifier, cs.op_name, args) 

    def __repr__(self):
        return "%s seen initially at %s" % (self.identity, [self.prettyprint(x) for x in self.callsites])

    def get_attribute_type(self):
        return IdentityAttributeType.CALLSITE_SET

    def to_thrift_object(self):
        return CallSiteSetAttribute(callsite_set=self.callsites)


class StateVars(Attribute):
    def __init__(self, name, identifier):
        super(StateVars, self).__init__(Identity(id_type=IdentityType.TOKEN, name=name, identifier=str(identifier)), [])
        self.state = {}
        self.fresh = False

    def set(self, name, val, cs):
        self.state[name] = (val, cs)
        self.add_dep(cs.receiver)

    def get(self, name):
        (val, cs) = self.state[name]
        return val

    def to_js(self):
        #class Ghost(PyV8.JSClass):
        class Ghost(object):
            def __init__(self, state, fresh):
                self.state = state
                self.fresh = fresh

            def __getattr__(self,nm):
                if nm == 'fresh':
                    return self.fresh
                if nm == 'orig':
                    if 'orig' in self.__dict__.keys():
                        return self.orig
                    else:
                        return None

                if nm in self.state.keys():
                    #print "looking up %s which is %s" % (nm, self.state[nm][0])
                    v = self.state[nm][0] # Property(lambda self: True) #self.state[nm][0])
                    if v == None:
                        return Unknown()
                    else:
                        return unwrap(v)

        return Ghost(self.state, self.fresh)

    def deserialize(self):
        self.state = dict([(k,(serialization.deserialize_python(v),o)) for (k,(v,o)) in self.state.items()])

    def merge(self, attribute):
        #for k,(v,o) in attribute.state.items():
        #    if self.state[k][0] != v:
        #        raise ValueError("merge failure on %s=%s (conflicted with %s)" % (k,v, self.state[k][0]))
        self.state = attribute.state

    def get_attribute_type(self):
        return IdentityAttributeType.STATE_VARS

    def __repr__(self):
        return "Ghost %s<%s> %s" % (self.identity.name, self.identity.identifier, dict([(k,v) for k,(v,o) in self.state.items()]))

    def to_thrift_object(self):
        items = []
        for k,(v,cs) in self.state.items():
            items.append(StateVar(name=k, value=serialization.serialize_python(v), where_set=cs))
        return StateVarsAttribute(state_vars=items)


def generate_proxy_client(proxy_endpoint):
    return thriftutil.get_client_with_defaults(Proxy.Client, proxy_endpoint[0], proxy_endpoint[1])

class Service(object):
    def __init__(self, proxy_endpoint, actual_endpoint, service_name = 'generic-service'):
        self.proxy_endpoint = proxy_endpoint
        self.actual_endpoint = actual_endpoint
        self.service_name = service_name
        self.overridden_id = "%s:%s" % self.actual_endpoint
        self.knownbyport = None

    def is_proxied(self):
        return self.proxy_endpoint != None

    def get_proxy_client(self):
        assert self.is_proxied()
        return generate_proxy_client(self.proxy_endpoint)

    def get_actual_endpoint(self):
        return self.actual_endpoint

    def get_identity(self):
        return Identity(id_type=IdentityType.SERVICE, name=self.service_name, identifier='%s' % self.overridden_id)

    def to_thrift_object(self):
        (proxy_host, proxy_port) = self.proxy_endpoint if self.is_proxied() else (None, None)
        if proxy_port:
            proxy_port = int(proxy_port)
        blame_labels = self.blame_labels if hasattr(self, 'blame_labels') else None
        return PortConfiguration(
            identifier=self.overridden_id, 
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            blame_labels=blame_labels,
        )

    def __str__(self):
        if self.is_proxied():
            return '%s proxiedby %s' % (self.overridden_id, self.proxy_endpoint)
        else:
            return 'unproxied %s' % (self.overridden_id,)

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self.proxy_endpoint, self.actual_endpoint))


class Terminal(object):
    def __init__(self):
        self.ends = {}
        self.interpreters = {}
    
    def get_terminus(self, s):
        if s not in self.ends:
            raise ValueError('no terminus for service at %s' % s)
        else:
            return self.ends(s)

    def register_interpreter(self, nm, config):
        self.interpreters[nm] = config
        generator = frontends.protocols[config[0]]
        if hasattr(generator, 'setup_config'):
            generator.setup_config(nm, config[1])

    def generate_terminus(self, config):
        s = Service(config.get('proxiedby', None), config['actual'])
        if 'identifier' in config:
            s.overridden_id = config['identifier']
        if 'knownbyport' in config:
            s.knownbyport = config['knownbyport']
        if s not in self.ends:
            if 'using' in config:
                interpreter = config['using'][0]
            elif 'mapsto' in config:
                if config['mapsto'] in self.interpreters:
                    interpreter = self.interpreters[config['mapsto']]
                else:
                    raise ValueError('unknown way to interpret service %s' % config['mapsto'])
            else:
                raise ValueError("unknown way to interpret connection %s" % str(config['actual']))
            protocol = interpreter[0]
            generator = frontends.protocols[protocol]
            blah = generator(interpreter[1], self, config)
            #self.ends[s] = blah
            return (s, blah)
        return (s, self.ends[s])


class CallSite(object):
    def __init__(self, service, opname, args, result = None):
        self.service = service
        self.opname = opname
        self.args = args
        self.result = result
        self.extra = {}
        self.from_proxy_name = 'unknown'

    def __str__(self):
        return "%s :: %s(%s) %s" % (self.service, self.opname, self.args, ("-> %s" % self.result if self.result else ""))

    def __eq__(self, other):
        return self.service == other.service and self.opname == self.opname and self.args == self.args

    def deserialize_args(self):
        self.args = [serialization.deserialize_python(arg) for arg in self.args]
        self.extra = serialization.deserialize_python(self.extra)

    def to_thrift_object(self):
        serialized = [serialization.serialize_python(arg) for arg in self.args]
        serialized_extra = serialization.serialize_python(self.extra)
        return TCallSite(receiver=self.service.get_identity(), op_name=self.opname, arguments=serialized, extra=serialized_extra)


class Redirector(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def register_redirection_port(self, actual_endpoint, proxy_endpoint):
        pass

    @abc.abstractmethod
    def get_redirection_port(self, endpoint):
        pass


class RedirectorHandler(object):
    def __init__(self, redirector):
        self.redirector = redirector

    def get_redirection_info(self, address, port):
        logger.debug("servicing redirection request for %s:%d" % (address, port))
        try:
            (host, rport) = self.redirector.get_redirection_port((address, str(port)))
            logger.debug("redirection rule found: %s:%d ==> %s:%d" % (address, port, host, rport))
            return RedirectionInfo(True, host, rport)
        except ValueError, e:
            logger.debug("no redirection found for %s:%d" % (address, port))
            return RedirectionInfo(False, None, 0)


class LocalRedirector(Redirector):
    def __init__(self, listen_port):
        self.redirections = {}
        self.requests = 0
        self.accept_redirector_requests(listen_port)

    def accept_redirector_requests(self, port):
        processor = Redirection.Processor(RedirectorHandler(self))
        self.server = thriftutil.start_daemon_with_defaults(processor, port)
        logger.debug("redirector accepting requests on port %d" % port)
        
    def register_redirection_port(self, actual_endpoint, proxy_endpoint):
        # removed to support sharding on a single IP endpoint
        #if actual_endpoint in self.redirections:
        #    raise ValueError("already redirecting %s" % (actual_endpoint,))
        actual_ip = socket.gethostbyname(actual_endpoint[0])
        actual_endpoint = (actual_ip, actual_endpoint[1])
        #logger.info("Registering proxy endpoint %s for actual endpoint %s" % (proxy_endpoint, actual_endpoint))
        if '*' in actual_endpoint[0]:
            p = actual_endpoint[1]
            for i in xrange(0,255):
                h = actual_endpoint[0].replace('*', str(i))
                self.redirections[(h,p)] = proxy_endpoint
        else:
            self.redirections[actual_endpoint] = proxy_endpoint

    def get_redirection_port(self, endpoint):
        self.requests += 1
        if endpoint not in self.redirections:
            raise ValueError("endpoint for redirection not found")
        return self.redirections[endpoint]

def identities_to_thrift_map(attributes):
    identities = []
    for attribute in attributes:
        assert isinstance(attribute, Attribute)
        data = serialization.SerializeThriftMsg(attribute.to_thrift_object())
        referenced = attribute.dependencies
        ainfo = IdentityAttribute(identity=attribute.identity, \
            value_type=attribute.get_attribute_type(), attribute_data=data, \
            referenced_identities=referenced)
        identities.append(ainfo)
    return identities

def thrift_map_to_identities(mapping):
    attributes = []
    for data in mapping:
        identity = data.identity
        if data.value_type == IdentityAttributeType.STATE_VARS:
            attr = serialization.DeserializeThriftMsg(StateVarsAttribute(), data.attribute_data)
            statevars = StateVars(identity.name, identity.identifier)
            for statevar in attr.state_vars:
                statevars.set(statevar.name, statevar.value, statevar.where_set)
            statevars.dependencies = data.referenced_identities
            statevars.deserialize()
            attributes.append(statevars)
        elif data.value_type == IdentityAttributeType.CALLSITE_SET:
            attr = serialization.DeserializeThriftMsg(CallSiteSetAttribute(), data.attribute_data)
            callsites = CallSiteSet(data.identity, None)
            callsites.callsites = attr.callsite_set
            callsites.dependencies = data.referenced_identities
            attributes.append(callsites)
        else:
            raise ValueError("unknown attribute type: %s" % attribute.value_type)
    return attributes

def proxies_to_thrift(proxies):
    return [s.to_thrift_object() for s in proxies]


class UsageTracker:
    def __init__(self):
        self.bytestx = 0
        self.bytesrx = 0
    def __repr__(self):
        return "Bytes Sent: %d Bytes Received: %d" % (self.bytestx, self.bytesrx)

def track_traffic(client, tracker = None):
    orig_write = client._oprot.trans.write
    orig_read = client._iprot.trans.read
    if not tracker:
        tracker = UsageTracker()
    def mywrite(b):
        tracker.bytestx += len(b)
        return orig_write(b)
    def myread(a):
        r = orig_read(a)
        tracker.bytesrx += len(r)
        return r
    client._oprot.trans.write = mywrite
    client._iprot.trans.read = myread
    return tracker

class ClientProxy(object):
    def __init__(self, app, service, terminus):
        self.app = app
        self.service = service
        self.terminus = terminus

    def get_terminus(self):
        return self.terminus

    def accept_unproxied_requests(self):
        if self.service.knownbyport:
            proxy_ep = ('0.0.0.0', self.service.knownbyport)
        else:
            proxy_ep = None
        self.app.redirector.register_redirection_port( \
            self.service.get_actual_endpoint(), \
            self.terminus.serve_requests(self, proxy_ep))

    def on_unproxied_request(self, opname, args, extra={}):
        '''returns only the result'''
        start = datetime.datetime.now()
        callsite = CallSite(self.service, opname, args)
        callsite.extra = extra
        if self.app.in_conflict(self.service.overridden_id):
            logger.warn("%s is in conflict with %s; short-circuiting", self.service, self.app.lookup_service(self.service.overridden_id)[1])
            return self.terminus.execute_request(callsite)
        
        identities = self.app.before_client(callsite)
        proxies = []
        if isinstance(identities, tuple):
            (identities, proxies) = identities
        proxies = proxies_to_thrift(proxies)
        proxy = self.app.lookup_proxy_port(self.service.actual_endpoint)
        if callsite.service.is_proxied() or proxy:
            proxy = callsite.service.get_proxy_client() if not proxy else generate_proxy_client(proxy)
            tracker = track_traffic(proxy)
            payload = serialization.SerializeThriftMsg(callsite.to_thrift_object())
            c = Annotated(port_configurations=proxies, from_proxy_name=self.app.name)
            blah = serialization.SerializeThriftMsg(c)
            idlen = len(blah)
            v1 = len(identities) + len(proxies)
            request = Annotated(original_payload=payload, identity_attributes=identities_to_thrift_map(identities), port_configurations=proxies, from_proxy_name=self.app.name)
            pause = datetime.datetime.now()
            annotated_res = proxy.execute(request)
            resume = datetime.datetime.now()
            c = Annotated(port_configurations=annotated_res.port_configurations, from_proxy_name=annotated_res.from_proxy_name)
            blah = ''.join([serialization.SerializeThriftMsg(ar) for ar in annotated_res.port_configurations])
            #print "--%s-- --" % blah.encode('utf-8')
            idlen += len(blah)
            #print "%s--" % idlen 
            network_bytes.write("%s\n" % idlen)
            network_bytes.flush()
            identity_attributes = annotated_res.identity_attributes
            identities = thrift_map_to_identities(identity_attributes)
            proxies = annotated_res.port_configurations
            callsite.result = serialization.deserialize_python(annotated_res.original_payload)
            traffic = self.app.bytesperop.get(opname, [])
            ###traffic.append(tracker.bytesrx + tracker.bytestx)
            ###self.app.bytesperop[opname] = traffic
            ghosts = self.app.ghostsperop.get(opname, [])
            ###ghosts.append(len(identities) + len(proxies) + v1)
            ###self.app.ghostsperop[opname] = ghosts
        else:
            callsite.from_proxy_name = 'unknown' if self.service.knownbyport else '_'
            self.app.before_server(callsite, identities, proxies=proxies)
            pause = datetime.datetime.now()
            callsite.result = self.terminus.execute_request(callsite)
            resume = datetime.datetime.now()
            identities = self.app.after_server(callsite)
            proxies = []
            if isinstance(identities, tuple):
                (identities, proxies) = identities
            proxies = proxies_to_thrift(proxies)
        
        #print "ghosts sent = %d" % len(identities)
        self.app.after_client(callsite, identities, proxies=proxies)
        stop = datetime.datetime.now()
        timing = self.app.timeperop.get((opname, "client"), [])
        ###timing.append((stop - start - (resume - pause)).total_seconds() * 1000)
        ###self.app.timeperop[(opname, "client")] = timing
        return callsite.result


class ServerProxyHandler(object):
    def __init__(self, server_proxy):
        self.server_proxy = server_proxy

    def get_this_identity(self):
        raise ValueError("XXX todo")

    def execute(self, request):
        start = datetime.datetime.now()
        payload = request.original_payload
        identity_attributes = request.identity_attributes
        callsite = serialization.DeserializeThriftMsg(TCallSite(), payload)
        callsite.from_proxy_name = request.from_proxy_name
        identities = thrift_map_to_identities(identity_attributes)
        (callsite, identities) = self.server_proxy.on_proxied_request(callsite, identities, start, proxies=request.port_configurations)
        proxies = []
        if isinstance(identities, tuple):
            (identities, proxies) = identities
        proxies = proxies_to_thrift(proxies)
        payload = serialization.serialize_python(callsite.result) # serialization.SerializeThriftMsg(callsite.to_thrift_object())
        s = Annotated(original_payload=payload, identity_attributes=identities_to_thrift_map(identities), port_configurations=proxies, from_proxy_name=self.server_proxy.app.name)
        #print s
        return s

    def get_identity_attributes(self, id):
        raise ValueError("XXX")


class ServerProxy(object):
    def __init__(self, app, service, terminus):
        self.app = app
        self.service = service
        self.terminus = terminus
        

    def accept_proxied_requests(self):
        assert self.service.is_proxied()
        processor = Proxy.Processor(ServerProxyHandler(self))
        self.server = thriftutil.start_daemon_with_defaults(processor, self.service.proxy_endpoint[1])

    def on_proxied_request(self, tcallsite, identities, start=None, proxies=[]):
        if not start:
            start = datetime.datetime.now()
        opname = tcallsite.op_name
        cs = CallSite(self.service, tcallsite.op_name, tcallsite.arguments)
        cs.extra = tcallsite.extra
        cs.from_proxy_name=tcallsite.from_proxy_name
        cs.deserialize_args()
        self.app.before_server(cs, identities, proxies=proxies)
        pause = datetime.datetime.now()
        cs.result = self.terminus.execute_request(cs)
        resume = datetime.datetime.now()
        identities = self.app.after_server(cs)
        #print "ghosts sent = %d" % len(identities)
        stop = datetime.datetime.now()
        timing = self.app.timeperop.get((opname, "server"), [])
        ###timing.append((stop - start - (resume - pause)).total_seconds() * 1000)
        ###self.app.timeperop[(opname, "server")] = timing
        return (cs, identities)

