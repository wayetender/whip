import abc
import frontends
import logging
from protocol.clientprotocol.ttypes import RedirectionInfo
from protocol.clientprotocol import Redirection
from protocol import Proxy
from protocol.ttypes import Identity, Annotated, IdentityType, IdentityAttribute, IdentityAttributeType, StateVar, StateVarsAttribute, CallSiteSetAttribute
from protocol.ttypes import CallSite as TCallSite
from util import thriftutil
from util import serialization
#from util.js import Unknown, unwrap
from util.eval import Unknown, unwrap
#from pyv8 import PyV8

logger = logging.getLogger(__name__)

class ProxyApplication(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, redirector):
        self.terminal = Terminal()
        self.client_proxies = []
        self.server_proxies = []
        self.redirector = redirector

    def register_proxy(self, proxy_config):
        (s, terminus) = self.terminal.generate_terminus(proxy_config)
        if proxy_config['type'] == 'server':
            proxy = ServerProxy(self, s, terminus)
            self.server_proxies.append(proxy)
            proxy.accept_proxied_requests()
            return proxy
        elif proxy_config['type'] == 'client':
            proxy = ClientProxy(self, s, terminus)
            self.client_proxies.append(proxy)
            proxy.accept_unproxied_requests()
            return proxy
        else:
            raise ValueError("unknown proxy type: %s" % proxy_config['type'])

    @abc.abstractmethod
    def before_client(self, callsite):
        logger.warn("before_client %s" % callsite)
        return []

    @abc.abstractmethod
    def before_server(self, callsite, client_attributes):
        logger.warn("before_server %s %s" % (callsite, client_attributes))
        pass

    @abc.abstractmethod
    def after_server(self, callsite):
        logger.warn("after_server %s" % callsite)
        return []

    @abc.abstractmethod
    def after_client(self, callsite, server_attributes):
        logger.warn("after_client %s %s" % (callsite, server_attributes))
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

    def prettyprint(self, cs):
        args = ", ".join([str(serialization.deserialize_python(arg)) for arg in cs.arguments])
        return "%s %s :: %s(%s)" % (cs.receiver.name, cs.receiver.identifier, cs.op_name, args) 

    def __repr__(self):
        return str([self.prettyprint(x) for x in self.callsites])

    def get_attribute_type(self):
        return IdentityAttributeType.CALLSITE_SET

    def to_thrift_object(self):
        return CallSiteSetAttribute(callsite_set=self.callsites)


class StateVars(Attribute):
    def __init__(self, name, identifier):
        super(StateVars, self).__init__(Identity(id_type=IdentityType.TOKEN, name=name, identifier=identifier), [])
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
                    return self.orig

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


class Service(object):
    def __init__(self, proxy_endpoint, actual_endpoint, service_name = 'generic-service'):
        self.proxy_endpoint = proxy_endpoint
        self.actual_endpoint = actual_endpoint
        self.service_name = service_name

    def is_proxied(self):
        return self.proxy_endpoint != None

    def get_proxy_client(self):
        assert self.is_proxied()
        return thriftutil.get_client_with_defaults(Proxy.Client, self.proxy_endpoint[0], self.proxy_endpoint[1])

    def get_actual_endpoint(self):
        return self.actual_endpoint

    def get_identity(self):
        return Identity(id_type=IdentityType.SERVICE, name=self.service_name, identifier='%s:%s' % self.actual_endpoint)

    def __str__(self):
        if self.is_proxied():
            return '%s proxiedby %s' % (self.actual_endpoint, self.proxy_endpoint)
        else:
            return 'unproxied %s' % (self.actual_endpoint,)

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self.proxy_endpoint, self.actual_endpoint))


class Terminal(object):
    def __init__(self):
        self.ends = {}

    def get_terminus(self, s):
        if s not in self.ends:
            raise ValueError('no terminus for service at %s' % s)
        else:
            return self.ends(s)

    def generate_terminus(self, config):
        s = Service(config.get('proxiedby', None), config['actual'])
        if s not in self.ends:
            protocol = config['using'][0]
            generator = frontends.protocols[protocol]
            self.ends[s] = generator(config['using'][1], self)
        return (s, self.ends[s])


class CallSite(object):
    def __init__(self, service, opname, args, result = None):
        self.service = service
        self.opname = opname
        self.args = args
        self.result = result

    def __str__(self):
        return "%s :: %s(%s) %s" % (self.service, self.opname, self.args, ("-> %s" % self.result if self.result else ""))

    def __eq__(self, other):
        return self.service == other.service and self.opname == self.opname and self.args == self.args

    def deserialize_args(self):
        self.args = [serialization.deserialize_python(arg) for arg in self.args]

    def to_thrift_object(self):
        serialized = [serialization.serialize_python(arg) for arg in self.args]
        return TCallSite(receiver=self.service.get_identity(), op_name=self.opname, arguments=serialized)


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
        self.accept_redirector_requests(listen_port)

    def accept_redirector_requests(self, port):
        processor = Redirection.Processor(RedirectorHandler(self))
        self.server = thriftutil.start_daemon_with_defaults(processor, port)
        logger.warn("redirector accepting requests on port %d" % port)
        
    def register_redirection_port(self, actual_endpoint, proxy_endpoint):
        if actual_endpoint in self.redirections:
            raise ValueError("already redirecting %s" % (actual_endpoint,))
        logger.warn("Registering proxy endpoint %s for actual endpoint %s" % (proxy_endpoint, actual_endpoint))
        self.redirections[actual_endpoint] = proxy_endpoint

    def get_redirection_port(self, endpoint):
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

class ClientProxy(object):
    def __init__(self, app, service, terminus):
        self.app = app
        self.service = service
        self.terminus = terminus

    def get_terminus(self):
        return self.terminus

    def accept_unproxied_requests(self):
        self.app.redirector.register_redirection_port( \
            self.service.get_actual_endpoint(), \
            self.terminus.serve_requests(self))

    def on_unproxied_request(self, opname, args):
        '''returns only the result'''
        callsite = CallSite(self.service, opname, args)
        identities = self.app.before_client(callsite)
        if callsite.service.is_proxied():
            proxy = callsite.service.get_proxy_client()
            payload = serialization.SerializeThriftMsg(callsite.to_thrift_object())
            request = Annotated(original_payload=payload, identity_attributes=identities_to_thrift_map(identities))
            annotated_res = proxy.execute(request)
            identity_attributes = annotated_res.identity_attributes
            identities = thrift_map_to_identities(identity_attributes)
            callsite.result = serialization.deserialize_python(annotated_res.original_payload)
        else:
            self.app.before_server(callsite, identities)
            callsite.result = self.terminus.execute_request(callsite)
            identities = self.app.after_server(callsite)
        
        print "ghosts sent = %d" % len(identities)
        self.app.after_client(callsite, identities)
        return callsite.result


class ServerProxyHandler(object):
    def __init__(self, server_proxy):
        self.server_proxy = server_proxy

    def get_this_identity(self):
        raise ValueError("XXX todo")

    def execute(self, request):
        payload = request.original_payload
        identity_attributes = request.identity_attributes
        callsite = serialization.DeserializeThriftMsg(TCallSite(), payload)
        identities = thrift_map_to_identities(identity_attributes)
        (callsite, identities) = self.server_proxy.on_proxied_request(callsite, identities)
        payload = serialization.serialize_python(callsite.result) # serialization.SerializeThriftMsg(callsite.to_thrift_object())
        return Annotated(original_payload=payload, identity_attributes=identities_to_thrift_map(identities))

    def get_identity_attributes(self, id):
        raise ValueError("XXX todo")


class ServerProxy(object):
    def __init__(self, app, service, terminus):
        self.app = app
        self.service = service
        self.terminus = terminus

    def accept_proxied_requests(self):
        assert self.service.is_proxied()
        processor = Proxy.Processor(ServerProxyHandler(self))
        self.server = thriftutil.start_daemon_with_defaults(processor, self.service.proxy_endpoint[1])

    def on_proxied_request(self, tcallsite, identities):
        cs = CallSite(self.service, tcallsite.op_name, tcallsite.arguments)
        cs.deserialize_args()
        self.app.before_server(cs, identities)
        cs.result = self.terminus.execute_request(cs)
        identities = self.app.after_server(cs)
        print "ghosts sent = %d" % len(identities)
        return (cs, identities)

