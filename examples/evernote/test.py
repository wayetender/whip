import sys
sys.path.append('../')
import test_utils
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
import time

host = 'localhost:9443'
token = '......................faketoken........................'

def run_sharednotes(host):
    total = test_utils.StopWatch('total')
    client = EvernoteClient(token=token, service_host=host)
    userStore = client.get_user_store()
    tracker = test_utils.track_traffic(userStore._client)
    #user = userStore.getUser()
    #print "notebooks for %s" % user.username
    # notebooks = noteStore.listNotebooks()
    # for n in notebooks:
    #     print n.name

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

if __name__ == '__main__':
    NUM_TRIALS = 1
    import mockevernoteserver
    #mockevernoteserver.start_all()
    time.sleep(1.0)
    print "starting %d trials..." % NUM_TRIALS
    report = []
    for trial in xrange(NUM_TRIALS):
        test_utils.setup_adapter_only('adapter.yaml', 1)()
        (traffic, stopwatch) = run_sharednotes(host)
        stats = test_utils.get_adapter_stats()
        report.append((traffic, stopwatch, stats))
        test_utils.teardown_adapter_only()
        print "Trial %d / %d: %s" % (trial+1, NUM_TRIALS, stopwatch)
    print "-- End of %d trials --" % NUM_TRIALS
    print test_utils.format_stats(report)
