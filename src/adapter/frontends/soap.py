from . import ProxyTerminus

from spyne.model._base import ModelBase
from spyne.model.complex import ComplexModelBase
from spyne.model.complex import ComplexModelMeta
from spyne.model.complex import ComplexModel
from spyne.protocol.soap import Soap11
from spyne.application import Application
from suds.client import Client
from spyne.model.complex import Iterable,Array
from spyne.decorator import srpc, rpc
from spyne.service import ServiceBase, ServiceBaseMeta
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode
from spyne.model.primitive import DateTime
from spyne.model.primitive import Boolean
from spyne.model.primitive import Double
from spyne.model.primitive import Integer16
from spyne.model.primitive import Integer64
from spyne.model.primitive import Float
from spyne.model.primitive import Date
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import wsgiref.util
from suds import sudsobject
from suds.sudsobject import Object as SudsObject
import suds.sax.date
import threading
import logging
import spyne.util.etreeconv
import suds.sax.text
import urllib
import datetime

    

logging.getLogger('suds').setLevel(logging.INFO)
logging.getLogger('spyne').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

logging.getLogger('spyne').setLevel(logging.CRITICAL)
logging.getLogger('spyne').setLevel(logging.INFO)


class FakeSudsNode(SudsObject):

    def __init__(self, data):
        SudsObject.__init__(self)
        self.__keylist__ = data.keys()
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, FakeSudsNode(value))
            elif isinstance(value, list):
                l = []
                for v in value:
                    if isinstance(v, list) or isinstance(v, dict):
                        l.append(FakeSudsNode(v))
                    else:
                        l.append(v)
                setattr(self, key, l)
            else:
                setattr(self, key, value)


class FakeSudsInstance(SudsObject):

    def __init__(self, data):
        SudsObject.__init__(self)
        self.__keylist__ = data.keys()
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, FakeSudsNode(value))
            else:
                setattr(self, key, value)

    @classmethod
    def build_instance(cls, instance):
        suds_data = {}
        def node_to_dict(node, node_data):
            if hasattr(node, '__keylist__'):
                keys = node.__keylist__
                for key in keys:
                    if isinstance(node[key], list):
                        lkey = key.replace('[]', '')
                        node_data[lkey] = node_to_dict(node[key], [])
                    elif hasattr(node[key], '__keylist__'):
                        node_data[key] = node_to_dict(node[key], {})
                    else:
                        if isinstance(node_data, list):
                            node_data.append(node[key])
                        else:
                            node_data[key] = node[key]
                return node_data
            else:
                if isinstance(node, list):
                    for lnode in node:
                        node_data.append(node_to_dict(lnode, {}))
                    return node_data
                else:
                    return node
        node_to_dict(instance, suds_data)
        return cls(suds_data)

def to_spyne_model(e, factory, tns):
    if isinstance(e, basestring):
        typename = e
        if typename == 'string':
            return Unicode
        elif typename == 'integer' or typename == 'int':
            return Integer
        elif typename == 'short':
            return Integer16
        elif typename == 'long':
            return Integer64
        elif typename == 'float':
            return Float
        elif typename == 'boolean':
            return Boolean
        elif typename == 'dateTime':
            return DateTime
        elif typename == 'double':
            return Double
        elif typename == 'date':
            return Date
        else:
            t = factory.resolver.find("{%s}%s" % (tns, typename))
            if t == None:
                raise ValueError("unknown type1 %s" % typename)
            e = t.resolve()
            #print dir(e.rawchildren[0])

    if e.name == 'string':
        return Unicode

    children = e.children()
    if len(children) == 0:
       # print str(e) + "  " + str(e.type)
        typename = str(e.type[0]) if e.type else None
        if not typename:
            typename = str(e.rawchildren[0].ref[0]) if len(e.rawchildren) > 0 and e.rawchildren[0].ref else None
        if not typename:
            typename = e.ref[0]
       # print typename
        if typename == 'string':
            return Unicode
        elif typename == 'integer' or typename == 'int':
            return Integer
        elif typename == 'short':
            return Integer16
        elif typename == 'long':
            return Integer64
        elif typename == 'float':
            return Float
        elif typename == 'boolean':
            return Boolean
        elif typename == 'dateTime':
            return DateTime
        elif typename == 'double':
            return Double
        elif typename == 'date':
            return Date
        else:
            t = factory.resolver.find("{%s}%s" % (tns, typename))
            if not t:
                return to_spyne_model(typename, factory, tns)
            typename = str(t.resolve().name)
            children = t.resolve().children()
            
    else:
        typename = str(e.name)

    M = type(typename, (ComplexModelBase,), {})
    M.__namespace__ = tns
    M.__type_name__ = typename

    number_of_multi_occurrences = 0
    rchild = None
    for child, ancestry in children:
        model = to_spyne_model(child, factory, tns)
        if child.multi_occurrence():
            number_of_multi_occurrences += 1
            rchild = model
        setattr(M, child.name, model)      

    M = ComplexModelMeta(str(e.name), M.__bases__, M.__dict__.copy())

    if number_of_multi_occurrences == 1:
        print "nulti occurence for %s" % M
        M = Iterable(rchild)
        M.__type_name__ = typename
    if number_of_multi_occurrences > 1:
        raise ValueError("not sure how to handle multiple multi-occurrences")

    return M


def make_method(args, client_proxy, method_name, rm, t):
    def m(self, *args):
        global startTime, tempTime
        #startTime = datetime.datetime.now()
        #tempTime = 0
        nargs = []
        for arg in args:
            nargs.append(t.unwrap_arrays(arg))
        result = client_proxy.on_unproxied_request(method_name, nargs)
        #print "returning"
        #print result
        #tempTime += (datetime.datetime.now() - startTime)
        #print "\t%f" % tempTime.total_seconds()
        return result
        # if isinstance(result, list):
        #     items = [] #Iterable()
        #     for item in result:
        #         toret = rm()
        #         print dir(toret)
        #         for k,v in item.items():
        #             setattr(toret, k, v)
        #         items.append(toret)
        #     #print items
        #     return items
        #if isinstance(result, list):
        #    for i in result:
        #        print "here %s" % (i,)
        #        yield i
        #else:
        #    yield result
    m.__name__ = method_name
    return m


#f = open('systimes.txt', 'w')
startTime = 0
tempTime = 0

class SoapProxyTerminus(ProxyTerminus):
    def __init__(self, wsdl):
        self.wsdl_location = wsdl
        self.client = Client(wsdl, headers={'Content-Type': 'iso-8859-1'})
        self.client.options.cache.clear()

    def unwrap_simple(self, r):
        if not isinstance(r, sudsobject.Object):
            return r
        r = client.dict(r)

        print "unwrapping %s" % r
        if len(r) == 1 and type(r.values()[0]) == list:
            return unwrap_arrays(r.values()[0])
        for k,v in r.items():
            r[k] = unwrap_arrays(v)
        return r

    def unwrap_arrays(self, r):
        if isinstance(r, sudsobject.Object):
            r = self.client.dict(r)
        if isinstance(r, datetime.datetime):
            return r
        if type(r) == suds.sax.text.Text:
            return unicode(r)
        if isinstance(r, (unicode, int, str, bool, float, datetime.datetime)):
            return r
       # if len(r) == 1 and type(r.values()[0]) == list:
       #     return self.unwrap_arrays(r.values()[0])
        elif type(r) == list:
            v2 = []
            for item in r:
                v2.append(self.unwrap_arrays(item))
            return v2
        if hasattr(r, 'items'):
            r2 = {}
            for k,v in r.items():
                if 'time' in k.lower():
                    r2[k] = suds.sax.date.DateTime(self.unwrap_arrays(v)).value
                else:
                    r2[k] = self.unwrap_arrays(v)
            return r2
        elif hasattr(r, '__dict__'):
            
            obj = {}
            for k, v in r.__dict__.items():
                if 'time' in k.lower():
                    obj[k] = suds.sax.date.DateTime(self.unwrap_arrays(v)).value
                else:
                    obj[k] = self.unwrap_arrays(v)
            return obj
        return r

    def serve_requests(self, client_proxy, endpoint = None):
        f = self.client.factory
        tns = self.client.wsdl.tns[1]
        me = self

        class WrappedService(ServiceBase):
            pass

        for method in self.client.wsdl.services[0].ports[0].methods.values():
            assert len(method.soap.input.body.parts) == 1
            assert len(method.soap.output.body.parts) == 1
            
            
            element = f.resolver.find("{%s}%s" % (method.soap.input.body.parts[0].element[1], method.soap.input.body.parts[0].element[0]))

            if element == None:
                raise ValueError("element not found %s" % method.soap.input.body.parts[0].element[0])
            argnames = []
            args = []
            #print element.namespace()[1]
            for child, ancestry in element.children():
                argname = child.name
                if child.type:
                    typename = child.type[0]
                    atns = child.type[1]
                else: # restriction type
                    typename = child.rawchildren[0].rawchildren[0].ref[0]
                    atns = tns
                argmodel = to_spyne_model(typename, f, atns)
                argnames.append(argname)
                args.append(argmodel)
                #WrappedService.__namespace__ = element.namespace()[1]

           
            ret = f.resolver.find("{%s}%s" % (method.soap.output.body.parts[0].element[1], method.soap.output.body.parts[0].element[0]))
            if ret == None:
                raise ValueError("element not found %s" % method.soap.output.body.parts[0].element[0])
            if len(ret.children()) == 0:
                retmodel = ComplexModel()
            else: 
                retval = (ret.children())
                if len(retval) == 1:
                    retval = retval[0][0]
                    #print retval
                    typename = retval.type[0]
                    retmodel = to_spyne_model(typename, f, retval.type[1] or tns)
                    if retval.multi_occurrence():
                        import decimal
                        retmodel.Attributes.max_occurs=decimal.Decimal('inf')
                else:
                    M = type(str(ret.name), (ComplexModelBase,), {})
                    M.__namespace__ = tns
                    M.__type_name__ = str(ret.name)

                    for (ret2, hierarchy) in retval:
                        #print ret2
                        typename = ret2.type[0]
                        retmodel = to_spyne_model(typename, f, ret2.namespace()[1] or tns)
                        if ret2.multi_occurrence():
                            import decimal
                            retmodel.Attributes.max_occurs=decimal.Decimal('inf')
                        setattr(M, ret2.name, retmodel)

                    M = ComplexModelMeta(str(ret.name), M.__bases__, M.__dict__.copy())
                    retmodel = M


            m = make_method(args, client_proxy, str(method.name), retmodel, me)

            setattr(WrappedService, str(method.name), rpc(*args, _args=argnames, _returns=retmodel, _no_ctx=False)(m))

        WrappedService = ServiceBaseMeta('WrappedService', WrappedService.__bases__, WrappedService.__dict__.copy())

        application = Application([WrappedService],
                tns=tns,
                in_protocol=Soap11(),
                out_protocol=Soap11()
            )

        wsgi_app = WsgiApplication(application)
        wsdl_location = self.wsdl_location
        class WsdlProxy:
            def __init__(self, application):
                self.application = application

            def __call__(self, environ, start_response):
                path = wsgiref.util.request_uri(environ)
                if path == wsdl_location:
                    logger.debug("returning proxied wsdl at %s" % wsdl_location)
                    return self.application(environ, start_response)
                if path.endswith('.xsd'):
                    logger.debug("getting actual file %s" % wsdl_location)
                    wsgiref.util.setup_testing_defaults(environ)
                    status = '200 OK'
                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return urllib.urlopen(path).read()
                else:
                    return self.application(environ, start_response)

        if not endpoint:
            server = make_server('0.0.0.0', 0, WsdlProxy(wsgi_app))
            endpoint = ('127.0.0.1', server.server_port)
        else:
            server = make_server(endpoint[0], endpoint[1], WsdlProxy(wsgi_app))

        self.listen_forever(server)
        return endpoint

    def listen_forever(self, server):
        t = threading.Thread(target=server.serve_forever)
        t.setDaemon(True)
        t.start()

    def execute_request(self, callsite):
        global tempTime, startTime
        '''returns the result'''
        s = self.client.service
        m = getattr(s, callsite.opname)
        #tempTime = datetime.datetime.now() - startTime
        res = m(*list(callsite.args))
        #startTime = datetime.datetime.now()
        return self.unwrap_arrays(res)

def generate(config, terminal):
    if 'wsdl' not in config:
        raise ValueError("WSDL param must be set")
    return SoapProxyTerminus(config['wsdl'])
