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

logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)3d %(funcName)20s() -- %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

class Handler(UserStore.Iface):
    def getUser(self, authenticationToken):
        return User(id=1, username="test", email="test", name="test", timezone=None, privilege=None, created=None, updated=None, deleted=None, active=None, shardId=None, attributes=None, accounting=None, premiumInfo=None, businessUserInfo=None)
    def getNoteStoreUrl(self, authenticationToken):
        time.sleep(DELAY)
        #print "getting note store for %s" % authenticationToken
        return "https://localhost:9444/"

class Handler2(NoteStore.Iface):
    def listNotebooks(self, authenticationToken):
        time.sleep(DELAY)
        return []

    def listLinkedNotebooks(self, authToken):
        time.sleep(DELAY)
        ln = LinkedNotebook(guid='guid0', noteStoreUrl='https://localhost:9444/')
        return [ln]

    def getSharedNotebookByAuth(self, authToken):
        time.sleep(DELAY)
        sn = SharedNotebook(notebookGuid='guid1')
        return sn

    def authenticateToSharedNotebook(self, shareKey, authToken):
        time.sleep(DELAY)
        ar = AuthenticationResult(authenticationToken='temp1')
        return ar

    def findNotes(self, authToken, filter, offset, maxNotes):
        time.sleep(DELAY)
        note = Note(guid='guid2', title='test')
        notes = [note]
        nl = NoteList(notes=notes, totalNotes=len(notes),startIndex=0)
        return nl

def start_userstore():
    pf = TBinaryProtocol.TBinaryProtocolFactory()
    processor = UserStore.Processor(Handler())
    server_address = ('', 9443) # (address, port)
    server = THttpSecureServer.THttpServer(processor, server_address, pf, pf)
    #print "starting userstore..."
    server.serve()

def start_notestore():
    pf = TBinaryProtocol.TBinaryProtocolFactory()
    processor = NoteStore.Processor(Handler2())
    server_address = ('', 9444) # (address, port)
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
    try:
        while True:
            raw_input()
    except KeyboardInterrupt:
        pass