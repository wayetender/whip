
service UserStore {

    getNoteStoreUrl(authToken)
    @where this is {{ authToken }}
    @identifies ns:NoteStore[] by {{
        yield (result, authToken)
    }}
   # @identifies us:UserStore by {{ result }}

    getUser(authToken)
    @where this is {{ authToken }}
    @precondition {{ len(authToken) > 0 }}
}


service NoteStore {
    listNotebooks(authToken)
    @where this is {{ authToken }}
    @precondition {{ len(authToken) < 0 }}

    listLinkedNotebooks(authToken)
    @where this is {{ authToken }}
    @identifies noteStores:NoteStore[] by {{
        for notebook in result: 
            #print notebook
            yield (notebook.noteStoreUrl, notebook.shareKey)
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