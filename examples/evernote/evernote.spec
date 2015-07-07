
ghost SharedNotebook {
    @identifier shareKey,
    @immutable validAt
}

service UserStore {

    getNoteStoreUrl(authToken)
    @identifies ns:NoteStore by {{ result }}

    getUser(authToken)
    @precondition {{ len(authToken) > 0 }}
}


service NoteStore {
    listNotebooks(authToken)
    @precondition {{ len(authToken) < 0 }}

    listLinkedNotebooks(authToken)
    @identifies noteStores:NoteStore[] by {{
        for notebook in result: yield (notebook.noteStoreUrl)
    }}
    @identifies sharedNotebooks:SharedNotebook[] by {{
        for notebook in result: yield (notebook.shareKey)
    }}
    @initializes {{
        for notebook in result:
            sharedNotebook = sharedNotebooks[notebook.shareKey]
            noteStore = noteStores[notebook.noteStoreUrl]
          #  print "notebook shared url: %s valid at %s" % (notebook.noteStoreUrl, noteStore)
            initialize(sharedNotebook, 'validAt', noteStore)
    }}

    getSharedNotebookByAuth(authToken)

    authenticateToSharedNotebook(shareKey, authToken)
    @identifies sharedNotebook : SharedNotebook by {{ shareKey }}
    @precondition {{ 
        #print "shared notebook valid at: %s" % sharedNotebook.validAt
        #print "receiver: %s" % receiver
        return sharedNotebook.validAt == receiver 
    }}

    findNotes(authToken, filter, offset, maxNotes)
    @precondition {{ offset >= 0 }}
    @postcondition {{ 
        result.totalNotes <= maxNotes and result.totalNotes == len(result.notes)
    }}
}