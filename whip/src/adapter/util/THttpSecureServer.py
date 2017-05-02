#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import BaseHTTPServer

from thrift.server import TServer
from thrift.transport import TTransport

import ssl


class ResponseException(Exception):
  """Allows handlers to override the HTTP response

  Normally, THttpServer always sends a 200 response.  If a handler wants
  to override this behavior (e.g., to simulate a misconfigured or
  overloaded web server during testing), it can raise a ResponseException.
  The function passed to the constructor will be called with the
  RequestHandler as its only argument.
  """
  def __init__(self, handler):
    self.handler = handler

lastPath = None

class THttpServer(TServer.TServer):
  """A simple HTTP-based Thrift server, modified to support Deacon
  """

  def add_processor(self, frompath, proc):
    self.frompaths.append((frompath, proc))

  def __init__(self,
               processor,
               server_address,
               inputProtocolFactory,
               outputProtocolFactory=None,
               server_class=BaseHTTPServer.HTTPServer,
               frompath=None):
    """Set up protocol factories and HTTP server.

    See BaseHTTPServer for server_address.
    See TServer for protocol factories.
    """
    if outputProtocolFactory is None:
      outputProtocolFactory = inputProtocolFactory

    TServer.TServer.__init__(self, processor, None, None, None,
        inputProtocolFactory, outputProtocolFactory)

    thttpserver = self

    if frompath is None:
      frompath = ''

    self.frompaths = [(frompath, processor)]

    class RequestHander(BaseHTTPServer.BaseHTTPRequestHandler):
      def log_request(*args, **kw): pass
      def do_POST(self):
        global lastPath
        lastPath = self.path
        processor = None
        for (fp, p) in thttpserver.frompaths:
          if self.path.startswith(fp):
            processor = p
            break
        if not processor:
            ## XXX TODO pass thru the request
            raise ValueError('no viable processor found for path %s' % lastPath)
        itrans = TTransport.TFileObjectTransport(self.rfile)
        otrans = TTransport.TFileObjectTransport(self.wfile)
        self.rfile.read(2) # XXX to catch the two carraige returns that separate the headers from the body
        itrans = TTransport.TBufferedTransport(
          itrans, int(self.headers['Content-Length']))
        otrans = TTransport.TMemoryBuffer()
        iprot = thttpserver.inputProtocolFactory.getProtocol(itrans)
        oprot = thttpserver.outputProtocolFactory.getProtocol(otrans)
        try:
          processor.process(iprot, oprot)
        except ResponseException, exn:
          exn.handler(self)
        else:
          self.send_response(200)
          self.send_header("content-type", "application/x-thrift")
          self.end_headers()
          self.wfile.write(otrans.getvalue())

    self.httpd = server_class(server_address, RequestHander)
    self.httpd.socket = ssl.wrap_socket (self.httpd.socket, certfile='server.pem', server_side=True)

  def serve(self):
    self.httpd.serve_forever()
