
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

    findNotes(authToken, filter, offset, maxNotes)
    @precondition {{ offset >= 0 }}
    @postcondition {{ len(result) <= maxNotes }}
}