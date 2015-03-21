import sys
sys.path.append('../')
import test_utils
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec

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

    noteStore = client.get_note_store()
    test_utils.track_traffic(noteStore._client, tracker)
    sharedNotebooks = noteStore.listLinkedNotebooks()
    for sharedNotebook in sharedNotebooks:
        sharedNoteStore = client.get_shared_note_store(sharedNotebook)
        notebook = sharedNoteStore.getSharedNotebookByAuth()
        print "Notes in shared notebook: %s" % notebook.notebookGuid
        f = NoteFilter(notebookGuid=notebook.notebookGuid)
        #rs = NotesMetadataResultSpec(includeTitle=True)
        #noteList = sharedNoteStore.findNotesMetadata(f, 0, 10, rs)
        noteList = sharedNoteStore.findNotes(f, 0, 10)
        for note in noteList.notes:
            print " - %s" % note.title

    total.stop()

    return (tracker, total)

if __name__ == '__main__':
    test_utils.setup_adapter_only('adapter.yaml')()
    (traffic, stopwatch) = run_sharednotes(host)
    stats = test_utils.get_adapter_stats()
    print test_utils.format_stats(traffic, stopwatch, stats)
    test_utils.teardown_adapter_only()

