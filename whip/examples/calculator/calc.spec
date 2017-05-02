ghost Session {
    @identifier sessionId, 
    @immutable username,
    @immutable offset,
    valid
}

service Calculator {
    login(username, offset)
    @precondition {{ offset >= 0 }}
    @identifies sess:Session by {{ result }}
    @updates sess.valid to {{ result != 'error' }}
    @updates sess.username to {{ username }} if {{ result != 'error' }}
    @updates sess.offset to {{ offset }} if {{ result != 'error' }}
    @postcondition {{ sess.valid == True or result == 'error' }}
    
    add(sid, a, b)
    @identifies sess:Session by {{ sid }}
    ##@invariant for sess {{ sess.valid == true }}
    @precondition {{ sess.valid == True }}
    @precondition {{ a > 0 and b > 0 }}
    @postcondition {{ result == a + b + sess.offset }}
}
