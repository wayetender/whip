import proxy
from parser import GhostDecl, ServiceContractDecl, JSTag, IdentifiesTag, InitializesTag, UpdatesTag, GenericUpdatesTag, GenericInitializesTag, parse
import logging
from proxy import StateVars
from protocol.ttypes import Identity, IdentityType
#from util.js import eval_code, is_unknown, AssertionFailure, rewrite_for_unknown_ops
from util.eval import eval_code, is_unknown, AssertionFailure, rewrite_for_unknown_ops
#from pyv8 import PyV8
import suds
import datetime

logger = logging.getLogger(__name__)

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

    def resolve_service(self, name):
        return self.services[name]

class Registry(object):
    def __init__(self):
        self.identities = {}

    def lookup_or_create(self, identity, default):
        key = (identity.name, identity.identifier)
        if key not in self.identities:
            self.identities[key] = default
        return self.identities[key]

    def lookup(self, identity):
        key = (identity.name, identity.identifier)
        return self.identities.get(key, None)

    def update(self, identity, v):
        key = (identity.name, identity.identifier)
        self.identities[key] = v

    def lookup_or_create_id(self, name, identifier, cs, resolver):
        if name in resolver.services:
            return self.lookup_or_create_service(name, identifier, cs, resolver)
        elif name in resolver.ghosts:
            return self.lookup_or_create_ghost(name, identifier, cs, resolver)
        else:
            raise ValueError("unknown identity type: %s" % name)

    def lookup_or_create_service(self, name, identifier, cs, resolver):
        key = (name, identifier)
        if 'http' in identifier:
            from urlparse import urlparse
            import socket
            o = urlparse(identifier)
            ip = socket.gethostbyname_ex(o.netloc)[2][0]
            port = o.port
            if not port:
                if o.scheme == 'https':
                    port = 443
                else:
                    port = 80
            identifier = "%s://%s:%d%s" % (o.scheme, str(ip), port, o.path)
        default = resolver.create_default_service(name, identifier, cs)
        if key not in self.identities:
            self.identities[key] = default
        return self.identities[key]

    def lookup_or_create_ghost(self, name, identifier, cs, resolver):
        key = (name, identifier)
        default = resolver.create_default_ghost(name, identifier, cs)
        if key not in self.identities:
            self.identities[key] = default
        return self.identities[key]

def report_error(registry, msg, identities, env={}, callsite = None):
    msg = "contract failure\n" + msg
    if callsite:
        msg += "\n occurring at " + str(callsite.service)
    if len(env) > 0:
        msg += "\n Variables: \n"
        for k, v in env.items():
            if k.startswith('_'):
                continue
            if hasattr(v, 'state'):
                msg += " - %s = Ghost {\n" % k
                for k1,v1 in v.state.items():
                    msg += "    - %s = %s (set in %s)\n" % (k1,v1[0], v1[1].op_name)
                msg += "    }\n" 
            else:
                msg += "  - %s = %s\n" % (k, v)
    for identity in dict(identities).values():
        msg += print_trace("", registry, identity, {})
    logger.warn(msg)
    
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
    #print "contract time = %f" % ((stop - start).total_seconds() * 1000)
    return (True, "")

class ContractService(proxy.Service):
    def __init__(self, proxy_endpoint, actual_endpoint, service_decl):
        super(ContractService, self).__init__(proxy_endpoint, actual_endpoint, service_decl.name)
        self.decl = service_decl

class ContractsTerminal(proxy.Terminal):
    def __init__(self, resolver):
        super(ContractsTerminal, self).__init__()
        self.resolver = resolver

    def generate_terminus(self, config):
        (service, terminus) = super(ContractsTerminal, self).generate_terminus(config)
        assert 'mapsto' in config
        service_decl = self.resolver.resolve_service(config['mapsto'])
        s = ContractService(service.proxy_endpoint, service.actual_endpoint, service_decl)
        return (s, terminus)


class StrDict:
    def __init__(self):
        self._items = {}
    def __getitem__(self, key):
        return self._items[str(key)]

class ContractsProxyApplication(proxy.ProxyApplication):
    def __init__(self, config, redirector):
        super(ContractsProxyApplication, self).__init__(redirector)
        if 'spec' not in config.keys():
            raise ValueError("spec must be in proxy config")
        self.resolver = SpecResolver(config['spec'])
        self.terminal = ContractsTerminal(self.resolver)
        self.registry = Registry()

    def register_proxy(self, proxy_config):
        super(ContractsProxyApplication, self).register_proxy(proxy_config)

    def compute_references(self, callsite, rpc):
        identity = callsite.service.get_identity()
        service = self.registry.lookup_or_create(identity, proxy.CallSiteSet(identity, callsite.to_thrift_object()))
        items = [('receiver', service)]
        env = dict(zip(rpc.formals, callsite.args) + [('result', callsite.result)])
        for tag in rpc.tags:
            if isinstance(tag, IdentifiesTag):
                if 'result' in tag.expr and not callsite.result:
                    continue

                if tag.multiple: 
                    inner_items = StrDict()
                    def y(identifier):
                        identifier = str(identifier)
                        ghost = self.registry.lookup_or_create_id(tag.type, identifier, callsite.to_thrift_object(), self.resolver)
                        inner_items._items[identifier] = ghost
                    nenv = dict(env.items() + [('yield', y)])
                    eval_code(nenv, tag.expr)
                    items.append((tag.name, inner_items))
                else:            
                    identifier = str(eval_code(env, tag.expr))
                    ghost = self.registry.lookup_or_create_id(tag.type, identifier, callsite.to_thrift_object(), self.resolver)
                    items.append((tag.name, ghost))
        return items

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
        #logger.debug("before client: %s", callsite)
        if callsite.opname in callsite.service.decl.rpcs:
            rpc = callsite.service.decl.rpcs[callsite.opname]
            assert len(rpc.formals) == len(callsite.args)
            references = self.compute_references(callsite, rpc)
            references2 = self.to_js(references)  # [(k, v.to_js()) for (k,v) in references]
            env = dict(zip(rpc.formals, callsite.args) + references2)
            #(res, msg) = check_precondition(rpc, env)
            #if not res:
            #    report_error(self.registry, msg, references)
            return self.flatten([v for (k, v) in references])
        else:
            logger.debug("unknown op: %s" % callsite.opname)
            return super(ContractsProxyApplication, self).before_client(callsite)

    def before_server(self, callsite, client_attributes):
        #logger.debug("before server: %s", callsite)
        self.merge_attributes(client_attributes)
        if callsite.opname not in callsite.service.decl.rpcs:
            logger.debug("unknown rpc %s", callsite.opname)
            return
        rpc = callsite.service.decl.rpcs[callsite.opname]
        references = self.compute_references(callsite, rpc)
        references2 = self.to_js(references)  # [(k, v.to_js()) for (k,v) in references]
        assert len(rpc.formals) == len(callsite.args)
        references = self.compute_references(callsite, rpc)
        env = dict(zip(rpc.formals, callsite.args) + references2)
        (res, msg) = check_precondition(rpc, env)
        if not res:
            report_error(self.registry, msg, references, env, callsite)

    def after_server(self, callsite):
        #logger.debug("after server: %s", callsite)
        if callsite.opname in callsite.service.decl.rpcs:
            rpc = callsite.service.decl.rpcs[callsite.opname]
            assert len(rpc.formals) == len(callsite.args)
            references = self.compute_references(callsite, rpc)
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
            return self.flatten([v for (k, v) in references])
        else:
            logger.debug("unknown op: %s" % callsite.opname)
            return super(ContractsProxyApplication, self).after_server(callsite)
        return super(ContractsProxyApplication, self).after_server(callsite)

    def after_client(self, callsite, server_attributes):
        #logger.debug("after client: %s", callsite)
        self.merge_attributes(server_attributes)
        if callsite.opname not in callsite.service.decl.rpcs:
            logger.debug("unknown rpc %s", callsite.opname)
            return
        rpc = callsite.service.decl.rpcs[callsite.opname]
        references = self.compute_references(callsite, rpc)
        assert len(rpc.formals) == len(callsite.args)
        if isinstance(callsite.result, suds.sax.text.Text):
            callsite.result = str(callsite.result)
        references2 = self.to_js(references)  # [(k, v.to_js()) for (k,v) in references]
        env = dict(zip(rpc.formals, callsite.args) + references2 + [('result', callsite.result)])
        (res, msg) = check_postcondition(rpc, env)
        if not res:
            report_error(self.registry, msg, references, env, callsite)
            