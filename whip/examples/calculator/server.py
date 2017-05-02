import logging
logging.basicConfig(level=logging.DEBUG)

from spyne.application import Application
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode
from spyne.model.complex import Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


logging.getLogger('spyne').setLevel(logging.INFO)

class HelloWorldService(ServiceBase):
    @srpc(Unicode, Integer, _returns=Unicode)
    def login(username, incrementor):
        if username == 'test':
            return "sessionfor%s-%d" % (username, incrementor)
        else:
            return "error"

    @srpc(Unicode, Integer, Integer, _returns=Integer)
    def add(sid, a, b):
        if sid.startswith('sessionfor'):
            d = int(sid.rpartition('-')[2])
            return a + b + d
        else:
            return -1

application = Application([HelloWorldService],
    tns='spyne.examples.hello',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

def make_app():
    from wsgiref.simple_server import make_server, WSGIRequestHandler
    wsgi_app = WsgiApplication(application)

    class QuietHandler(WSGIRequestHandler):
        def log_request(*args, **kw): pass

    return make_server('0.0.0.0', 8000, wsgi_app, handler_class=QuietHandler)

if __name__ == '__main__':
    s = make_app()
    s.serve_forever()
