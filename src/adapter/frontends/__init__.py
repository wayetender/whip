import abc

class ProxyTerminus(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def serve_requests(self, client_proxy, endpoint = None):
        '''returns: endpoint it is listening on'''
        pass

    @abc.abstractmethod
    def execute_request(self, callsite):
        '''returns the result'''
        pass


import soap
import thrift
protocols = { 'soap': soap.generate, 'thrift': thrift.generate } 

__all__ = ['ProxyTerminus', 'protocols']
