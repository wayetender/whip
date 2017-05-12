from . import ProxyTerminus

from flask import Flask
from flask import request
from flask import make_response
import urllib2
import socket
import json
import threading
import datetime
import ssl

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


network_times = open('times', 'w')
network_times.truncate()

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
            try:
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
            except:
                import sys, traceback
                print traceback.print_exc(file=sys.stdout)
                print sys.exc_info()
                
        self.app.add_url_rule("/<path:p>", 'handle', handle)
        self.app.config['PROPAGATE_EXCEPTIONS'] =True
        t = threading.Thread(target=lambda: self.app.run(host=host, port=port, ssl_context=context, threaded=True, debug=False, ))
        t.setDaemon(True)
        t.start()

        return ('127.0.0.1', port)

    def execute_request(self, callsite):
        h = callsite.args[0]['headers']['Host']
        apath = 'https://%s:%s%s' % (h, self.actual_port, callsite.opname) if ':' not in h else "https://%s%s" % (h, callsite.opname)
        context = ssl._create_unverified_context()
        nrequest = urllib2.Request(apath)
        for (header, v) in callsite.args[0]['headers'].items():
            if header == 'Content-Length' or header == 'Accept-Encoding': continue
            nrequest.add_header(header, v)
        startTime = datetime.datetime.now()
        proxy_resp = urllib2.urlopen(nrequest, context=context)
        body = str(proxy_resp.read()).encode('ascii', 'ignore')
        code = proxy_resp.getcode()
        tempTime = (datetime.datetime.now() - startTime).total_seconds() * 1000
        
        network_times.write("%s\n" % tempTime)
        network_times.flush()
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

    
