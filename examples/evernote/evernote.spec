
service UserStore {

    getNoteStoreUrl(authToken)
    @identifies ns:NoteStore by {{ result }}
   # @identifies us:UserStore by {{ result }}

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
    
    getSharedNotebookByAuth(authToken)

    authenticateToSharedNotebook(shareKey, authToken)
    @precondition {{ 
        #print "shared notebook valid at: %s" % sharedNotebook.validAt
        #print "receiver: %s" % receiver
        #return sharedNotebook.validAt == receiver 
        #print shareKey
        return True #len(shareKey) > 0
    }}

    findNotes(authToken, filter, offset, maxNotes)
    @precondition {{ offset >= 0 }}
    @postcondition {{ 
        result.totalNotes <= maxNotes and result.totalNotes == len(result.notes)
    }}
}