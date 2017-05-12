import sys
import test_utils
from evernote.api.client import EvernoteClient, Store
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
import time
import inspect
import functools

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
#if using valid SSL, uncomment and use the following instead
#import thrift.transport.THttpClient as THttpClient
import THttpInsecureClient

from thrift.transport import TTransport
import ssl
import httplib

host = 'localhost:9443'
token = '......................faketoken........................'


def _get_thrift_client(self, client_class, url):
    http_client = THttpInsecureClient.THttpClient(url)
    buffered = TTransport.TBufferedTransport(http_client)
    thrift_protocol = TBinaryProtocol.TBinaryProtocol(http_client)
    return client_class(thrift_protocol)


Store._get_thrift_client = _get_thrift_client

def run_sharednotes(host, n=0):
    total = test_utils.StopWatch('total')
    client = EvernoteClient(token="%s%s" % (token, n), service_host=host)
    userStore = client.get_user_store()
    userStore._get_thrift_client = _get_thrift_client
    
    #tracker = test_utils.track_traffic(userStore._client)
    #user = userStore.getUser()
    #print "notebooks for %s" % user.username
    # notebooks = noteStore.listNotebooks()
    # for n in notebooks:
    #     print n.name

    tracker = None
    client.get_note_store()
    noteStore = test_utils.measure('getNoteStoreUrl', lambda: client.get_note_store())
    test_utils.track_traffic(noteStore._client, tracker)
    sharedNotebooks = test_utils.measure('listLinkedNotebooks', lambda: noteStore.listLinkedNotebooks())
    for sharedNotebook in sharedNotebooks:
        #print sharedNotebook.shareKey
        sharedNoteStore = test_utils.measure('authenticateToSharedNotebook', lambda: client.get_shared_note_store(sharedNotebook))
        #print sharedNoteStore.token
        notebook = test_utils.measure('getSharedNotebookByAuth', lambda: sharedNoteStore.getSharedNotebookByAuth())
        #print "Notes in shared notebook: %s" % notebook.notebookGuid
        f = NoteFilter(notebookGuid=notebook.notebookGuid)
        #rs = NotesMetadataResultSpec(includeTitle=True)
        #noteList = sharedNoteStore.findNotesMetadata(f, 0, 10, rs)
        noteList = test_utils.measure('findNotes', lambda: sharedNoteStore.findNotes(f, 0, 10))
        for note in noteList.notes:
            #print " - %s" % note.title
            pass

    total.stop()

    return (tracker, total)

#run_sharednotes(host)

import psutil
import os
#process = psutil.Process(os.getpid())

if __name__ == '__main__':
    NUM_TRIALS = int(os.getenv('NUM_OPS')) / 5
    #mockevernoteserver.start_all()
    time.sleep(1.0)
    print "starting %d trials..." % NUM_TRIALS
    report = []
    request_num = 1
    
    #test_utils.setup_adapter_only('adapter.yaml', 1)()
    for trial in xrange(NUM_TRIALS):
        (traffic, stopwatch) = run_sharednotes(host, trial)
        for [m] in test_utils.measurements.values():
            print "%s,%s" % (request_num, m * 1000)
            request_num += 1
        test_utils.measurements.clear()
        #if trial % 100 == 0:
        #    print trial
        #    pass
            #import gc
            #gc.collect(2)
            #mem = process.memory_info()
            #print mem
            #print mem / 1024
        #stats = test_utils.get_adapter_stats()
        #report.append((traffic, stopwatch, stats))
        #test_utils.teardown_adapter_only()
    #    print "Trial %d / %d: %s" % (trial+1, NUM_TRIALS, stopwatch)
    print "-- End of %d trials --" % NUM_TRIALS
    #print test_utils.format_stats(report)
