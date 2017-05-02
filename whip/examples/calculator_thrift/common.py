from thrift.protocol import TBinaryProtocol
from thrift.protocol import TCompactProtocol
from thrift.protocol import TJSONProtocol
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.transport import TZlibTransport
from thrift.server import TNonblockingServer
from thrift.server import TProcessPoolServer
from thrift.server import TServer
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

# These specify how data gets marshalled
PROTOCOLS = {
    'fast': TBinaryProtocol.TBinaryProtocolAcceleratedFactory,
    'binary': TBinaryProtocol.TBinaryProtocolFactory,
    'compact': TCompactProtocol.TCompactProtocolFactory,
    'json': TJSONProtocol.TJSONProtocolFactory,
}


# These specify how data gets written and read from the socket
TRANSPORTS = {
    'buffered': TTransport.TBufferedTransportFactory,
    'framed': TTransport.TFramedTransportFactory,
    'compressed': TZlibTransport.TZlibTransportFactory,
    # TODO: twisted, tornado
}


# These specify how new connections are handled on the server
SERVERS = {
    'nonblocking': TNonblockingServer.TNonblockingServer,
    'process-pool': TProcessPoolServer.TProcessPoolServer,
    'simple': TServer.TSimpleServer,
    'threaded': TServer.TThreadedServer,
}


def initialize_server(processor, port, trans_type, prot_type, server_type, **kwargs):
    transport = TSocket.TServerSocket(port=port)
    tfactory = TRANSPORTS[trans_type]()
    pfactory = PROTOCOLS[prot_type]()
    server_c = SERVERS[server_type]
    if server_type is 'threaded':
        kwargs['daemon'] = True
    if server_type is 'nonblocking':
        return server_c(processor, transport, pfactory, pfactory, **kwargs)
    return server_c(processor, transport, tfactory, tfactory, pfactory, pfactory, **kwargs)

def get_transport(host, port, framed = False):
    transport = TSocket.TSocket(host, port)
    if framed:
        transport = TTransport.TFramedTransport(transport)
    transport.open()
    return transport


def get_protocol(transport, prot_type):
    pfactory = PROTOCOLS[prot_type]()
    return pfactory.getProtocol(transport)

def init(*args, **kwargs):
    return initialize_server(*args, **kwargs)

def init_with_defaults(processor, port, **kwargs):
    return init(processor, port, 'framed', 'fast', 'threaded', **kwargs)

def get_client_with_defaults(cls, ip, port):
    transport = get_transport(ip, port, framed = True)
    protocol = get_protocol(transport, 'fast')
    return cls(protocol)

def run_forever(server):
    try:
        server.serve()
    except KeyboardInterrupt:
        pass

def init_and_run_forever(*args, **kwargs):
    run_forever(init(*args, **kwargs))

def init_with_defaults_and_run_forever(processor, port):
    run_forever(init_with_defaults(processor, port))    
