
service UserStore {
    getUser(authToken)
    @precondition {{ len(authToken) > 0 }}
}


service NoteStore {
    listNotebooks(authToken)
    @precondition {{ len(authToken) > 0 }}    
}