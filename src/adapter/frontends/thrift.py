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

logger = logging.getLogger(__name__)

def make_method(self, client_proxy, nm):
    def m(self, *args):
        result = client_proxy.on_unproxied_request(nm, list(args))
        return result
    return m


class ThriftProxyTerminus(ProxyTerminus):
    def __init__(self, idl, ns, service, host, port, protocol, transport):
        self.idl = idl
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
            self.servicename = service
            m = __import__(mname, globals(), locals(), [service])
            shutil.rmtree(d)
            deleted = True
            self.iface = getattr(m, 'Iface')
            self.ClientCls = getattr(m, 'Client')
            self.ProcessorCls = getattr(m, 'Processor')
            trans = thriftutil.get_transport(host, port, transport == 'framed')
            prot = thriftutil.get_protocol(trans, protocol)
            self.client = self.ClientCls(prot)
        finally:
            if not deleted:
                shutil.rmtree(d)
        self.transport = transport
        self.protocol = protocol
        

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
            port = 0
        else:
            port = endpoint[1]
        server = thriftutil.initialize_server(processor, port, self.transport, self.protocol, 'threaded')
        t = Thread(target=server.serve)
        t.daemon = True
        t.start()
        while not server.serverTransport.handle:
            time.sleep(0.01)
        port = (server.serverTransport.handle.getsockname()[1])
        return ('127.0.0.1', port)

    def execute_request(self, callsite):
        '''returns the result'''
        m = getattr(self.client, callsite.opname)
        #tempTime = datetime.datetime.now() - startTime
        res = m(*list(callsite.args))
        #startTime = datetime.datetime.now()
        #res = self.unwrap_arrays(res)
        #print "res is %s" % res
        return res

def generate(config, terminal, serviceconfig):
    if 'idl' not in config:
        raise ValueError("idl param must be set")
    if 'ns' not in config:
        raise ValueError("ns param must be set")
    if 'protocol' not in config:
        raise ValueError("protocol param must be set")
    if 'transport' not in config:
        raise ValueError("transport param must be set")
    if 'mapsto' not in serviceconfig:
        raise ValueError("mapstoservice must be set")
    (ip, port) = serviceconfig['actual']
    return ThriftProxyTerminus(config['idl'], config['ns'], serviceconfig['mapsto'], ip, port, config['protocol'], config['transport'])
