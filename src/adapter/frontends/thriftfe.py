from . import ProxyTerminus
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from util import thriftutil
import tempfile
import subprocess
import logging
import shutil
from threading import Thread
import time
import datetime
import importlib
from thrift.protocol import TBinaryProtocol
from util import THttpSecureServer

logger = logging.getLogger(__name__)

def make_method(self, client_proxy, nm):
    def m(self, *args):
        result = client_proxy.on_unproxied_request(nm, list(args), extra={'path': THttpSecureServer.lastPath})
        return result
    return m

cache = {}

def cache_stubs(service, idl, ns):
    d = tempfile.mkdtemp()
    deleted = False
    idl = os.path.join(os.getcwd(), idl)
    try:
        logger.debug("generating thrift stubs in %s for IDL %s", d, idl)
        res = subprocess.call(["thrift", "-r", "--gen", "py", "-out", d, idl])
        if res != 0:
            raise ValueError("thrift could not generate appropriate stubs")
        sys.path.append(d)
        mname = "%s.%s" % (ns, service)
        splits = ns.split('.')
        accum = ''
        for s in splits:
            accum += s
            m = importlib.import_module(accum)
            reload(m)
            accum += '.'
        m = importlib.import_module(mname)
        shutil.rmtree(d)
        sys.path.remove(d)
        deleted = True
        iface = getattr(m, 'Iface')
        ClientCls = getattr(m, 'Client')
        ProcessorCls = getattr(m, 'Processor')
    
        cache[service] = {
            'iface': iface,
            'ClientCls': ClientCls,
            'ProcessorCls': ProcessorCls
        }
    finally:
        if not deleted:
            shutil.rmtree(d)

    
class ThriftProxyTerminus(ProxyTerminus):
    allendpoints = {}
    def __init__(self, idl, ns, service, host, port, protocol, transport, frompath):
        if service not in cache:
            raise ValueError('service %s not in cache' % service)
        cache_info = cache[service]
        self.iface = cache_info['iface']
        self.ClientCls = cache_info['ClientCls']
        self.ProcessorCls = cache_info['ProcessorCls']
        self.transport = transport
        self.protocol = protocol
        self.frompath = frompath
        self.servicename = service
        self.host = host
        self.port = port
    
    def set_proxy(self, proxy):
        if self.protocol == 'binary-https':
            ap = proxy.service.get_actual_endpoint()
            proxy.service.overridden_id = "https://%s:%s%s" % (ap[0], ap[1], self.frompath)

    def serve_requests(self, client_proxy, endpoint = None):
        '''returns: endpoint it is listening on'''
        entries = {}
        for nm, v in self.iface.__dict__.items():
            if nm.startswith('__'):
                continue 
            entries[nm] = make_method(self, client_proxy, nm)
        HandlerCls = type('%sHandler' % self.servicename, (object,), entries)
        processor = self.ProcessorCls(HandlerCls())
        if not endpoint:
            host = '0.0.0.0'
            port = 0
        else:
            host = endpoint[0]
            port = endpoint[1]
        if self.protocol == 'binary-https':
            ap = client_proxy.service.get_actual_endpoint()
            if ap in ThriftProxyTerminus.allendpoints:
                s = ThriftProxyTerminus.allendpoints[ap]
                s.add_processor(self.frompath, processor)
                port = (s.httpd.socket.getsockname()[1])
                return ('127.0.0.1', port)
            else:
                pf = TBinaryProtocol.TBinaryProtocolFactory()
                server_address = (host, port)
                server = THttpSecureServer.THttpServer(processor, server_address, pf, pf, frompath=self.frompath)
                ThriftProxyTerminus.allendpoints[ap] = server
        else:
            server = thriftutil.initialize_server(processor, port, self.transport, self.protocol, 'threaded')
        t = Thread(target=server.serve)
        t.daemon = True
        t.start()
        if self.protocol == 'binary-https':
            while not server.httpd.socket:
                time.sleep(0.01)
            port = (server.httpd.socket.getsockname()[1])
        else:
            while not server.serverTransport.handle:
                time.sleep(0.01)
            port = (server.serverTransport.handle.getsockname()[1])
        return ('127.0.0.1', port)

    def execute_request(self, callsite):
        '''returns the result'''
        startTime = datetime.datetime.now()
        if 'path' not in callsite.extra.keys():
            raise ValueError('no path set in callsite')
        if self.protocol == 'binary-https':
            import thrift.transport.THttpClient as THttpClient
            url = "https://%s:%s%s" % (self.host, self.port, callsite
                .extra['path'])
            trans = THttpClient.THttpClient(url)
            trans.setCustomHeaders({
                'User-Agent': "DProxy / 0.1; Python / %s;"
                % (sys.version,)
            })
            prot = TBinaryProtocol.TBinaryProtocol(trans)
        else:
            trans = thriftutil.get_transport(self.host, self.port, self.transport == 'framed')
            prot = thriftutil.get_protocol(trans, self.protocol)
        client = self.ClientCls(prot)
        m = getattr(client, callsite.opname)
        res = m(*list(callsite.args))
        trans.close()
        tempTime = datetime.datetime.now() - startTime
        #print "time for %s: %f ms" % (callsite.opname, tempTime.total_seconds() * 1000)
        #print "res is %s" % res
        return res

def generate(config, terminal, serviceconfig):
    if 'idl' not in config:
        raise ValueError("idl param must be set")
    if 'ns' not in config:
        raise ValueError("ns param must be set")
    if 'protocol' not in config:
        raise ValueError("protocol param must be set")
    if 'transport' not in config and config['protocol'] != 'binary-https':
        raise ValueError("transport param must be set")
    if 'mapsto' not in serviceconfig:
        raise ValueError("mapstoservice must be set")
    (ip, port) = serviceconfig['actual']
    frompath = serviceconfig.get('fromhttppath', None)
    return ThriftProxyTerminus(config['idl'], config['ns'], serviceconfig['mapsto'], ip, port, config['protocol'], config.get('transport', None), frompath)

def setup_config(nm, config):
    if 'idl' not in config:
        raise ValueError("idl param must be set")
    if 'ns' not in config:
        raise ValueError("ns param must be set")
    if 'protocol' not in config:
        raise ValueError("protocol param must be set")
    if 'transport' not in config and config['protocol'] != 'binary-https':
        raise ValueError("transport param must be set")

    cache_stubs(nm, config['idl'], config['ns'])

generate.setup_config = setup_config
