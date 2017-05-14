import proxy
from parser import GhostDecl, ServiceContractDecl, JSTag, IdentifiesTag, InitializesTag, UpdatesTag, GenericUpdatesTag, GenericInitializesTag, parse, WhereTag
import logging
from proxy import StateVars, ClientProxy
from protocol.ttypes import Identity, IdentityType
#from util.js import eval_code, is_unknown, AssertionFailure, rewrite_for_unknown_ops
from util.eval import eval_code, is_unknown, AssertionFailure, rewrite_for_unknown_ops
#from pyv8 import PyV8
import suds
import datetime
import socket
import types

logger = logging.getLogger(__name__)

timings = {}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

WhipMsg = "[" + bcolors.OKGREEN + bcolors.BOLD + "Whip" + bcolors.ENDC + "] "

class SpecResolver(object):
    def __init__(self, spec_file):
        self.spec_file = spec_file
        self.services = {}
        self.ghosts = {}
        with open(spec_file) as f:
            parsed = parse(f.read())
        for item in parsed:
            if isinstance(item, GhostDecl):
                self.add_ghost_decl(item)
            elif isinstance(item, ServiceContractDecl):
                self.add_service(item)
            else:
                raise ValueError("unknown declaration %s" % item)

    def add_ghost_decl(self, ghost):
        self.ghosts[ghost.name] = ghost

    def create_default_ghost(self, type, name, cs):
        ghostdecl = self.ghosts[type]
        sv = proxy.StateVars(type, name)
        for (k,(ft, v)) in ghostdecl.fields.items():
            if ft == 'identifier':
                continue
            if v != None:
                v = eval_code({}, v)
            sv.set(k, v, cs)
        sv.fresh = True
        return sv

    def create_default_service(self, type, name, cs):
        ident = Identity(id_type=IdentityType.SERVICE, name=type, identifier=name)
        servicedecl = proxy.CallSiteSet(ident, cs)
        return servicedecl

    def add_service(self, service):
        self.services[service.name] = service
        for g in service.ghosts:
            g.service_owner = service
            self.add_ghost_decl(g)

    def resolve_service(self, name):
        return self.services[name]

class Registry(object):
    def __init__(self, app):
        self.app = app
        self.identities = {}

    def lookup_or_create(self, identity, default):
        return default
        #key = (identity.name, identity.identifier)
        #if key not in self.identities:
        #    self.identities[key] = default
        #return self.identities[key]

    def lookup(self, identity):
        key = (identity.name, identity.identifier)
        return self.identities.get(key, None)

    def update(self, identity, v):
        key = (identity.name, identity.identifier)
        #self.identities[key] = v

    def lookup_or_create_id(self, name, identifier, cs, resolver, my_id = None):
        if name in resolver.services:
            return self.lookup_or_create_service(name, identifier, cs, resolver)
        elif name in resolver.ghosts:
            return self.lookup_or_create_ghost(name, identifier, cs, resolver, my_id)
        else:
            raise ValueError("unknown identity type: %s" % name)

    def lookup_or_create_service(self, name, identifier, cs, resolver):
        #identifier2 = identifier
        identifier2 = identifier.partition('?')[0]
        key = (name, identifier2)
        endpoint = (identifier.rpartition(':')[0], identifier.rpartition(':')[2])
        fromhttppath = None
        if 'http' in identifier:
            from urlparse import urlparse
            o = urlparse(identifier)
            h = o.netloc.split(':')[0]
            ip = socket.gethostbyname_ex(h)[2][0]
            port = o.port
            if not port:
                if o.scheme == 'https':
                    port = 443
                else:
                    port = 80
            endpoint = (ip, str(port))
            fromhttppath = o.path
            identifier = "%s://%s:%d%s" % (o.scheme, str(ip), port, o.path)
        default = resolver.create_default_service(name, identifier, cs)
        #return default
        if key not in self.identities:
            self.identities[key] = default
        #print "service lookup on %s resulted in %s (is default = %r)" % (key, self.identities[key], is_default)
        return self.identities[key]

    def lookup_or_create_ghost(self, name, identifier, cs, resolver, my_id):
        key = (name, my_id.identifier + ':' + identifier if my_id else identifier)
        #if my_id:
        #    logger.info("[debug-passthru] ID is %s", key)
        default = resolver.create_default_ghost(name, identifier, cs)
        return default
        #if key not in self.identities:
        #    self.identities[key] = default
        #return self.identities[key]

def report_error(registry, msg, identities, env={}, callsite = None):
    msg = WhipMsg + bcolors.FAIL + "Contract Failure: " + bcolors.ENDC + msg
    msg += bcolors.WARNING
    if callsite:
        msg += "\n\t Occurring at: " + bcolors.ENDC + str(callsite.service.friendly_name())
    if len(env) > 0:
        msg += bcolors.WARNING + "\n\t Variables: \n" + bcolors.ENDC
        for k, v in env.items():
            if k.startswith('_') or type(v) == types.FunctionType:
                continue
            if k == 'StringIO':
                continue
            if hasattr(v, 'state'):
                msg += " - %s = Ghost {\n" % k
                for k1,v1 in v.state.items():
                    msg += "    - %s = %s (set in %s)\n" % (k1,v1[0], v1[1].op_name)
                msg += "    }\n" 
            else:
                msg += "\t   - %s%s%s = %s%s%s\n" % (bcolors.UNDERLINE, k, bcolors.ENDC, bcolors.OKBLUE, v, bcolors.ENDC)
    #for identity in dict(identities).values():
    #    msg += print_trace("", registry, identity, {})
    msg += bcolors.ENDC
    print msg
    
def print_trace(depth, registry, identity, seen):
    if (identity.identity.identifier) not in seen:
        seen = {identity.identity.identifier}.union(seen)
        msg = "\n ^--" + depth + "--> referenced: " + str(identity)
        for dep in identity.dependencies:
            msg += print_trace("----" + depth, registry, registry.lookup(dep), seen)
        return msg
    return ''

def check_precondition(proc, env):
    start = datetime.datetime.now()
    for tag in proc.tags:
        if isinstance(tag, JSTag) and tag.tag_type == 'precondition':
            js = rewrite_for_unknown_ops(tag.js)
            #print js
            #logger.debug("checking precondition %s with %s", tag.js, env)
            try:
                result = eval_code(env, js)
            except AssertionFailure:
                result = False
            #if is_unknown(result):
            #    print "UNKNOWN!!!"
            if not is_unknown(result) and not result:
                return (False, "Failed precondition for RPC %s (%s)" % (proc.name, tag.js))
    stop = datetime.datetime.now()
    global timings
    t = timings.get((proc.name, "pre"), [])
    ###t.append((stop - start).total_seconds() * 1000)
    ###timings[(proc.name, "pre")] = t
    #print "contract time = %f" % ((stop - start).total_seconds() * 1000)
    return (True, "")

def check_postcondition(proc, env):
    start = datetime.datetime.now()
    for tag in proc.tags:
        if isinstance(tag, JSTag) and tag.tag_type == 'postcondition':
            #logger.debug("checking postcondition %s with %s", tag.js, env)
            js = rewrite_for_unknown_ops(tag.js)
            #print js
            try:
                result = eval_code(env, js)
            except AssertionFailure:
                result = False
            if not is_unknown(result) and not result:
                return (False, "Failed postcondition %s" % tag.js)
    stop = datetime.datetime.now()
    global timings
    t = timings.get((proc.name, "post"), [])
    #t.append((stop - start).total_seconds() * 1000)
    ###timings[(proc.name, "post")] = t
    #print "contract time = %f" % ((stop - start).total_seconds() * 1000)
    return (True, "")

class ContractService(proxy.Service):
    def __init__(self, proxy_endpoint, actual_endpoint, service_decl, blame_label):
        super(ContractService, self).__init__(proxy_endpoint, actual_endpoint, service_decl.name)
        self.decl = service_decl
        if type(blame_label) != list:
            blame_label = [blame_label]
        self.blame_labels = blame_label

    def __repr__(self):
        return str(self)


    def friendly_name(self):
        if '?' in self.overridden_id:
            return 'service %s with index %s at %s vouched for by %s' % (self.decl.name, self.overridden_id.partition('?')[2], self.overridden_id.partition('?')[0], ', '.join(self.blame_labels))
        else:
            return 'service %s with default index at %s vouched for by %s' % (self.decl.name, self.overridden_id, ', '.join(self.blame_labels))

    def __str__(self):
        if self.is_proxied():
            return '%s {%s} proxiedby %s' % (self.overridden_id, self.blame_labels, self.proxy_endpoint)
        else:
            return 'unproxied %s {%s}' % (self.overridden_id,self.blame_labels)


class ContractsTerminal(proxy.Terminal):
    def __init__(self, resolver):
        super(ContractsTerminal, self).__init__()
        self.resolver = resolver
        self.endpoint_to_services = {}

    def generate_terminus(self, config, blame_label):
        (service, terminus) = super(ContractsTerminal, self).generate_terminus(config)
        assert 'mapsto' in config
        service_decl = self.resolver.resolve_service(config['mapsto'])
        s = ContractService(service.proxy_endpoint, service.actual_endpoint, service_decl, blame_label)
        s.knownbyport = service.knownbyport
        self.endpoint_to_services[config['actual']] = s
        if hasattr(service, 'overridden_id'):
            s.overridden_id = service.overridden_id
        return (s, terminus)


class StrDict:
    def __init__(self):
        self._items = {}
    def __getitem__(self, key):
        return self._items[str(key)]
    def items(self):
        return self._items.items()

class ContractsProxyApplication(proxy.ProxyApplication):
    def __init__(self, config, redirector):
        super(ContractsProxyApplication, self).__init__(redirector)
        if 'spec' not in config.keys():
            raise ValueError("spec must be in proxy config")
        self.resolver = SpecResolver(config['spec'])
        self.terminal = ContractsTerminal(self.resolver)
        self.registry = Registry(self)
        self.name = config['proxy_name']

    def register_proxy(self, proxy_config, blame_label):
        if type(blame_label) != list:
            blame_label = [blame_label]
        #actual = socket.gethostbyname(proxy_config['actual'][0])
        #proxy_config['actual'] = (actual, proxy_config['actual'][1])
        identifier = "%s:%s" % (proxy_config['actual']) if 'identifier' not in proxy_config else proxy_config['identifier']
        (_,s) = self.lookup_service(identifier)
        if s:
            if proxy_config['type'] == 'client':
                (s2, terminus) = self.terminal.generate_terminus(proxy_config, blame_label)
                s2.proxy_type = proxy_config['type']
                if proxy_config['actual'] not in self.client_actuals:
                    self.client_actuals.append(proxy_config['actual'])
                    final = self.register_service(s2, terminus)
            
            if type(s) != list and s.service_name == proxy_config['mapsto']:
                if set(blame_label + s.blame_labels) != set(s.blame_labels):
                    #print "--- merging blame label %s in with %s" % (blame_label, s)
                    s.blame_labels = list(set(s.blame_labels + blame_label))
            else:
                logger.warn("--- conflict merge on %s" % (proxy_config,))
                (sp, _) = self.terminal.generate_terminus(proxy_config, blame_label)
                servicelist = self.services.get(sp.overridden_id, [])
                servicelist.append(sp)
                self.services[sp.overridden_id] = servicelist
                #--self.services.append(sp)
                #--self.services = list(set(self.services[0:10] + self.services[-10:]))
                return
        else:
            (s, terminus) = self.terminal.generate_terminus(proxy_config, blame_label)
            s.proxy_type = proxy_config['type']
            if 'fromhttppath' in proxy_config:
                s.fromhttppath = proxy_config['fromhttppath']
            if 'identifier' in proxy_config:
                s.overridden_id = proxy_config['identifier']

            #print "store-- adding %s" % s.overridden_id
            #--self.services.append(s)
            #--self.services = list(set(self.services[0:10] + self.services[-10:]))
            if proxy_config['type'] == 'client':
                if proxy_config['actual'] in self.client_actuals:
                    proxy = ClientProxy(self, s, terminus)
                    terminus.set_proxy(proxy)
                    final = None
                else:
                    self.client_actuals.append(proxy_config['actual'])
                    final = self.register_service(s, terminus)
            else:
                final = self.register_service(s, terminus)
            servicelist = self.services.get(s.overridden_id, [])
            #print s.overridden_id
            servicelist.append(s)
            self.services[s.overridden_id] = servicelist
            return final

    def compute_references(self, callsite, rpc):
        identity = callsite.service.get_identity()
        #service = self.registry.lookup_or_create(identity, proxy.CallSiteSet(identity, callsite.to_thrift_object()))
        #items = [('receiver', service)]
        items = []
        env = dict(zip(rpc.formals, callsite.args) + [('result', callsite.result)])
        for tag in rpc.tags:
            if isinstance(tag, IdentifiesTag):
                if 'result' in tag.expr and callsite.result == None:
                    continue

                if tag.multiple: 
                    inner_items = StrDict()
                    def y(identifier, higher=None):
                        identifier = str(identifier).encode('ascii', 'ignore')
                        if higher:
                            identifier += "?" + str(higher).encode('ascii', 'ignore')
                        ghost = self.registry.lookup_or_create_id(tag.type, identifier, callsite.to_thrift_object(), self.resolver, identity)
                        if higher:
                            ghost.identity.identifier = identifier
                        inner_items._items[identifier] = ghost
                    nenv = dict(env.items() + [('yield', y)])
                    eval_code(nenv, tag.expr)
                    items.append((tag.name, inner_items))
                else:
                    identifier = str(eval_code(env, tag.expr))
                    ghost = self.registry.lookup_or_create_id(tag.type, identifier, callsite.to_thrift_object(), self.resolver, identity)
                    items.append((tag.name, ghost))
        return items

    def mark_this_service(self, env, callsite, rpc, blame_label):
        found = False
        identifier = callsite.service.overridden_id
        s = None
        for tag in rpc.tags:
            if isinstance(tag, WhereTag):
                found = True
                index = eval_code(env, tag.expr)
                identifier = "%s?%s" % (callsite.service.overridden_id.partition('?')[0], index)
                identifier = str(identifier).encode('ascii', 'ignore')
                (_, s) = self.lookup_service(identifier)
        if not found:
            (_, s) = self.lookup_service(callsite.service.overridden_id)
        if not s:

            proxy_config = self.generate_proxy_config(callsite.service.decl.name, identifier)
            proxy_config['identifier'] = identifier
            #print "--- registering locally this= %s %s" % (identifier, proxy_config)
            self.register_proxy(proxy_config, blame_label)
            (_,s) = self.lookup_service(callsite.service.overridden_id)
            return ([blame_label], s)
        return (s.blame_labels, s)


         

    def process_updates(self, env, ghosts, callsite, rpc):
        for tag in rpc.tags:
            if isinstance(tag, UpdatesTag) or isinstance(tag, InitializesTag):
                if tag.ifexpr:
                    if not eval_code(env, tag.ifexpr):
                        continue
                val = eval_code(env, tag.val)
                v_old = ghosts[tag.name].get(tag.field)
                if is_unknown(val):
                    if v_old != None:
                        raise ValueError("attempting to convert actual ghost state to unknown")
                    else:
                        val = None
                if isinstance(tag, InitializesTag):
                    if v_old == None:
                        logger.debug( "initializing %s to %s for %s" % (tag.field, val, ghosts[tag.name]))
                        ghosts[tag.name].set(tag.field, val, callsite.to_thrift_object())
                    elif v_old != val:
                        raise ValueError("attempting to intialize already intialized ghost %s.%s (%s) to different value (%s)" % (tag.name, tag.field, v_old, val))
                    else:
                        logger.debug("ignoring initialization %s for %s (already set)" % (tag.field, ghosts[tag.name]))
                else:
                    logger.debug("updating %s to %s for %s" % (tag.field, val, ghosts[tag.name]))
                    ghosts[tag.name].set(tag.field, val, callsite.to_thrift_object())
            if isinstance(tag, GenericUpdatesTag):
                def updater(ghost, field, val):
                    if is_unknown(val):
                        v_old = ghost.orig.get(field)
                        if v_old != None:
                            raise ValueError("attempting to convert actual ghost state to unknown")
                        else:
                            val = None
                    logger.debug( "updating %s to %s" % (field, val))
                    ghost.orig.set(field, val, callsite.to_thrift_object())
                eval_code(dict(env.items() + [('update', updater)]), tag.val)
            if isinstance(tag, GenericInitializesTag):
                def initializer(ghost, field, val):
                    v_old = ghost.orig.get(field)
                    if v_old != None and v_old != val:
                        raise ValueError("attempting to intialize already intialized %s.%s (%s) to different value (%s)" % (ghost.orig, field, v_old, val))
                    logger.debug( "initializing %s to %s" % (field, val))
                    ghost.orig.set(field, val, callsite.to_thrift_object())
                eval_code(dict(env.items() + [('initialize', initializer)]), tag.val)



    def merge_attributes(self, attributes):
        for attribute in attributes:
            my_version = self.registry.lookup(attribute.identity)
            if my_version:
                my_version.merge(attribute)
            else:
                self.registry.update(attribute.identity, attribute)

    def generate_proxy_config(self, name, identifier):
        fromhttppath = None
        index = identifier.partition('?')[2]
        (host, port) = (identifier.rpartition(':')[0], identifier.rpartition(':')[2])
        port = port.partition('?')[0]
        endpoint = (host, port)
        if len(index) > 0: index = '?%s' % (index,)
        if 'http' in identifier:
            from urlparse import urlparse
            o = urlparse(identifier)
            h = o.netloc.split(':')[0]
            ip = socket.gethostbyname_ex(h)[2][0]
            port = o.port
            if not port:
                if o.scheme == 'https':
                    port = 443
                else:
                    port = 80
            endpoint = (ip, str(port))
            fromhttppath = o.path
            identifier = "%s://%s:%d%s%s" % (o.scheme, str(ip), port, o.path, index)
        return {
            'mapsto': name,
            'actual': endpoint,
            'type': 'client',
            'fromhttppath': fromhttppath,
            'identifier': identifier
        } 

    def to_js(self, refs):
        items = []
        for (k, v) in refs:
            if isinstance(v, StrDict):
                item2 = StrDict()
                for k2 in v._items.keys():
                    item2._items[k2] = v._items[k2].to_js()
                    item2._items[k2].orig = v._items[k2]
                items.append((k, item2))
            elif isinstance(v, dict):
                item2 = {}
                for k2 in v.keys():
                    item2[k2] = v[k2].to_js()
                    item2[k2].orig = v[k2]
                items.append((k, item2))
            else:
                va = v.to_js()
                va.orig = v
                items.append((k, va))
        return items

    def flatten(self, items):
        aitems = []
        for item in items:
            if isinstance(item, StrDict):
                item = item._items
            if isinstance(item, dict):
                for v in item.values():
                    aitems.append(v)
            else:
                aitems.append(item)
        return aitems

    def unfreshen(self, items):
        for item in items:
            if isinstance(item, StrDict):
                v = item._items
            if isinstance(item, dict):
                for v in item.values():
                    v.fresh = False
            else:
                item.fresh = False

    def before_client(self, callsite):
        #print "before client %s" % callsite.opname
        #logger.debug("before client: %s", callsite)
        if callsite.opname in callsite.service.decl.rpcs:
            rpc = callsite.service.decl.rpcs[callsite.opname]
            bl = 'unknown' if callsite.service.knownbyport else self.name
            #print 'the blame label is %s' % bl
            assert len(rpc.formals) == len(callsite.args)
            references = self.compute_references(callsite, rpc)
            env = dict(zip(rpc.formals, callsite.args))
            (blame_label, this_service) = self.mark_this_service(env, callsite, rpc, self.name)
            #print "--> client: blame label: %s" % blame_label
            proxies = self.handle_references(references, bl)
            self.unfreshen([v for (k, v) in references])
            references2 = self.to_js(references)  # [(k, v.to_js()) for (k,v) in references]
            env = dict(zip(rpc.formals, callsite.args) + references2)
            #(res, msg) = check_precondition(rpc, env)
            #if not res:
            #    report_error(self.registry, msg, references)
            return ([], proxies)
        else:
            #logger.warn("unknown op: %s" % callsite.opname)
            return super(ContractsProxyApplication, self).before_client(callsite)

    def before_server(self, callsite, client_attributes, proxies=[]):
        #print "before server %s" % callsite.opname
        #logger.debug("before server: %s", callsite)
        self.merge_attributes(client_attributes)
        if callsite.opname not in callsite.service.decl.rpcs:
            logger.debug("unknown rpc %s", callsite.opname)
            return
        rpc = callsite.service.decl.rpcs[callsite.opname]
        bl = callsite.from_proxy_name if callsite.from_proxy_name != '_' else self.name
        references = self.compute_references(callsite, rpc)
        env = dict(zip(rpc.formals, callsite.args))
        #print "i'm getting this from %s" % (callsite.from_proxy_name,)
        (blame_label, this_service) = self.mark_this_service(env, callsite, rpc, callsite.from_proxy_name)
        #print "--> server: blame label: %s" % blame_label
        self.handle_references(references,blame_label,proxies)
        references2 = self.to_js(references)  # [(k, v.to_js()) for (k,v) in references]
        assert len(rpc.formals) == len(callsite.args)
        references = self.compute_references(callsite, rpc)
        env = dict(zip(rpc.formals, callsite.args) + references2)
        (res, msg) = check_precondition(rpc, env)
        msg += "\n\t %sBlaming:%s %s (precondition failure)" % (bcolors.WARNING, bcolors.ENDC, bl)
        if not res:
            callsite.service = this_service
            report_error(self.registry, msg, references, env, callsite)

    def handle_references(self, references, blame_label, incoming_proxies=[]):
        proxies = []
        computed = []
        for r in references:
            if isinstance(r[1], proxy.Attribute):
                computed.append(r)
            else:
                computed.extend(r[1].items())
        for r in computed:
            if isinstance(r[1], proxy.Attribute):
                (_, s) = self.lookup_service(r[1].identity.identifier)
                imported = False
                for p in incoming_proxies:
                    if p.identifier == r[1].identity.identifier:
                        #print "--> importing %s" % p
                        imported = True
                        proxy_config = self.generate_proxy_config(r[1].identity.name, r[1].identity.identifier)
                        if p.proxy_host:
                            proxy_config['proxiedby'] = (p.proxy_host, p.proxy_port)
                        self.register_proxy(proxy_config, p.blame_labels)
                if not imported:
                    proxy_config = self.generate_proxy_config(r[1].identity.name, r[1].identity.identifier)
                    #print "--> registering locally %s" % (proxy_config,)
                    bl = s.blame_labels if s else blame_label
                    self.register_proxy(proxy_config, bl)
        for r in computed:
            if isinstance(r[1], proxy.Attribute):
                (should_forward, s) = self.lookup_service(r[1].identity.identifier)
                if should_forward:
                    proxies.append(s)
                else:
                    print s
                    print "Conflict: not forwarding"
        return proxies

    def after_server(self, callsite):
        #print "after server %s" % callsite.opname
        #logger.debug("after server: %s", callsite)
        if callsite.opname in callsite.service.decl.rpcs:
            rpc = callsite.service.decl.rpcs[callsite.opname]
            assert len(rpc.formals) == len(callsite.args)
            references = self.compute_references(callsite, rpc)
            env = dict(zip(rpc.formals, callsite.args))
            (blame_label, this_service) = self.mark_this_service(env, callsite, rpc, callsite.from_proxy_name)
            #print "<-- server: blame label: %s" % blame_label
            proxies = self.handle_references(references,blame_label)
            self.unfreshen([v for (k, v) in references])
            references2 = self.to_js(references)  # [(k, v.to_js()) for (k,v) in references]
            #if isinstance(callsite.result, suds.sax.text.Text):
            #    callsite.result = str(callsite.result)
            #print references2
            env = dict(zip(rpc.formals, callsite.args) + references2 + [('result', callsite.result)])
            try:
                self.process_updates(env, dict(references), callsite, rpc)
            except ValueError, e:
                report_error(self.registry, str(e), [], env, callsite)
            references = self.compute_references(callsite, rpc)
            references2 = self.to_js(references)  # [(k, v.to_js()) for (k,v) in references]
            env = dict(zip(rpc.formals, callsite.args) + references2 + [('result', callsite.result)])
            #(res, msg) = check_postcondition(rpc, env)
            #if not res:
            #    report_error(self.registry, msg, references)
            #return self.flatten([v for (k, v) in references])
            return ([], proxies)
        else:
            logger.debug("unknown op: %s" % callsite.opname)
            return super(ContractsProxyApplication, self).after_server(callsite)
        return super(ContractsProxyApplication, self).after_server(callsite)

    def after_client(self, callsite, server_attributes, proxies=[]):
        #print "after client %s" % callsite.opname
        #logger.debug("after client: %s", callsite)
        self.merge_attributes(server_attributes)
        if callsite.opname not in callsite.service.decl.rpcs:
            logger.debug("unknown rpc %s", callsite.opname)
            return
        rpc = callsite.service.decl.rpcs[callsite.opname]
        references = self.compute_references(callsite, rpc)
        env = dict(zip(rpc.formals, callsite.args))
        (blame_label, this_service) = self.mark_this_service(env, callsite, rpc, self.name)
        #print "--> client: blame label: %s" % blame_label
        self.handle_references(references,blame_label,proxies)
        assert len(rpc.formals) == len(callsite.args)
        if isinstance(callsite.result, suds.sax.text.Text):
            callsite.result = str(callsite.result)
        references2 = self.to_js(references)  # [(k, v.to_js()) for (k,v) in references]
        env = dict(zip(rpc.formals, callsite.args) + references2 + [('result', callsite.result)])
        (res, msg) = check_postcondition(rpc, env)
        if not res:
            callsite.service = this_service
            report_error(self.registry, msg, references, env, callsite)
            