import abc

class ProxyTerminus(object):
    __metaclass__ = abc.ABCMeta

    def set_proxy(self, proxy):
        pass

    @abc.abstractmethod
    def serve_requests(self, client_proxy, endpoint = None):
        '''returns: endpoint it is listening on'''
        pass

    @abc.abstractmethod
    def execute_request(self, callsite):
        '''returns the result'''
        pass


import soap
import thriftfe
protocols = { 'soap': soap.generate, 'thrift': thriftfe.generate } 

__all__ = ['ProxyTerminus', 'protocols']
