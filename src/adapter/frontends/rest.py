from . import ProxyTerminus

from flask import Flask
from flask import request
from flask import make_response
import urllib2
import socket
import json
import threading

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class RestProxyTerminus(ProxyTerminus):
    def __init__(self, ip, port):
        self.actual_ip = ip
        self.actual_port = port

    def serve_requests(self, client_proxy, endpoint = None):
        '''returns: endpoint it is listening on'''
        context = ('server.pem', 'server.pem')
        if not endpoint:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', 0))
            port = sock.getsockname()[1]
            sock.close()
            host = '0.0.0.0'
        else:
            host = endpoint[0]
            port = endpoint[1]
        self.app = Flask(__name__)

        def handle(p):
            arg = {
                'args': dict(request.args.items()),
                'headers': dict(request.headers.items())
            }
            result = client_proxy.on_unproxied_request('/%s' % p, [arg])
            resp = make_response(json.dumps(result['body']))
            for (header, v) in result['headers'].items():
                if header == 'content-length': continue
                resp.headers[header] = v
            return resp

        self.app.add_url_rule("/<path:p>", 'handle', handle)
        t = threading.Thread(target=lambda: self.app.run(host=host, port=port, ssl_context=context, threaded=True, debug=False))
        t.setDaemon(True)
        t.start()
        return ('127.0.0.1', port)

    def execute_request(self, callsite):
        apath = 'https://%s:%s%s' % (callsite.args[0]['headers']['Host'], self.actual_port, callsite.opname)
        nrequest = urllib2.Request(apath)
        for (header, v) in callsite.args[0]['headers'].items():
            if header == 'Content-Length' or header == 'Accept-Encoding': continue
            nrequest.add_header(header, v)
        proxy_resp = urllib2.urlopen(nrequest)
        body = proxy_resp.read()
        code = proxy_resp.getcode()
        res = {
            'headers': dict(proxy_resp.info()),
            'body': json.loads(body),
            'code': code
        }
        return res

def generate(config, terminal, serviceconfig):
    if 'mapsto' not in serviceconfig:
        raise ValueError("mapstoservice must be set")
    (ip, port) = serviceconfig['actual']
    frompath = serviceconfig.get('fromhttppath', None)
    return RestProxyTerminus(ip, port)

    
