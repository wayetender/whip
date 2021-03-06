import THttpSecureServer

from evernote.edam.userstore import UserStore
from evernote.edam.notestore import NoteStore
from thrift.server import THttpServer
from thrift.protocol import TBinaryProtocol
from evernote.edam.type.ttypes import User
from evernote.edam.userstore.ttypes import AuthenticationResult
from evernote.edam.type.ttypes import SharedNotebook, LinkedNotebook, Note
from evernote.edam.notestore.ttypes import NoteList

import logging
from threading import Thread
import time

DELAY = 0.5
numRequests = 0
requests = 0

logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)3d %(funcName)20s() -- %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

class Handler(UserStore.Iface):
    def getUser(self, authenticationToken):
        return User(id=1, username="test", email="test", name="test", timezone=None, privilege=None, created=None, updated=None, deleted=None, active=None, shardId=None, attributes=None, accounting=None, premiumInfo=None, businessUserInfo=None)
    def getNoteStoreUrl(self, authenticationToken):
        #-time.sleep(.01)
        #print "getting note store for %s" % authenticationToken
        global requests, startTime
        if requests == 0:
            startTime = time.time()
        requests += 1
        return "https://127.0.0.1:9444/"

class Handler2(NoteStore.Iface):
    def listNotebooks(self, authenticationToken):
        #-time.sleep(.01)
        return []

    def listLinkedNotebooks(self, authToken):
        #time.sleep(.451)
        #time.sleep(.400)
        global numRequests, requests
        requests += 1
        #numRequests += 1
        ln = LinkedNotebook(guid='guid0%s' % numRequests, shareKey='asd', noteStoreUrl='https://127.0.0.1:9444/')
        return [ln]

    def getSharedNotebookByAuth(self, authToken):
        #-time.sleep(.521)
        global numRequests, requests
        requests += 1
        #numRequests += 1
        sn = SharedNotebook(notebookGuid='guid1%s' % numRequests)
        return sn

    def authenticateToSharedNotebook(self, shareKey, authToken):
        #-time.sleep(.495)
        global numRequests, requests
        requests += 1
        #numRequests += 1
        ar = AuthenticationResult(authenticationToken='temp1%s' % numRequests)
        return ar

    def findNotes(self, authToken, filter, offset, maxNotes):
        #-time.sleep(.474)
        global numRequests, requests
        requests += 1
        #numRequests += 1
        note = Note(guid='guid2%s' % numRequests, title='test')
        notes = [note]
        nl = NoteList(notes=notes, totalNotes=len(notes),startIndex=0)
        return nl
    
def start_userstore():
    pf = TBinaryProtocol.TBinaryProtocolFactory()
    processor = UserStore.Processor(Handler())
    server_address = ('127.0.0.1', 9443) # (address, port)
    server = THttpSecureServer.THttpServer(processor, server_address, pf, pf)
    #print "starting userstore..."
    server.serve()

def start_notestore():
    pf = TBinaryProtocol.TBinaryProtocolFactory()
    processor = NoteStore.Processor(Handler2())
    server_address = ('127.0.0.1', 9444) # (address, port)
    server = THttpSecureServer.THttpServer(processor, server_address, pf, pf)
    #print "starting notestore..."
    server.serve()

def start_all():
    t1 = Thread(target=start_userstore)
    t1.daemon = True
    t1.start()
    t2 = Thread(target=start_notestore)
    t2.daemon = True
    t2.start()

if __name__ == '__main__':
    start_all()
    import sys
    sys.path.append('../')
    import test_utils
    test_utils.setup_adapter_only('adapter.yaml', 1)()
    import psutil
    import os
    import time
    startTime = 0
    try:
        process = psutil.Process(os.getpid())
        process = process.children(recursive=True)[1]
        while True:
            if startTime > 0:
                sz = os.path.getsize('/tmp/lru3.dat') if os.path.exists('/tmp/lru3.dat') else 0
                mem = process.memory_info()
                print "%s,%s,%s,%s" % (time.time() - startTime, mem.rss / 1024, sz / 1024, requests)
                sys.stdout.flush()
            time.sleep(2)
    except KeyboardInterrupt:
        pass