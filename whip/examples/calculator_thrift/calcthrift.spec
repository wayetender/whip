
service AdderDiscovery {

    login(username, password)
    # @identifies s:Session by {{ result }}
    # @initializes s.username to {{ username }}

    register_adder(sid, host, port)
    @identifies a:Adder by {{ "%s:%d" % (host, port) }}

    get_adder_info(sid)
    @identifies a:Adder by {{ "%s:%s" % (result.host, result.port) }}

    dumb(host, port)
    @identifies d:AdderDiscovery by {{ "%s:%s" % (host, port ) }}
}

service Adder {
    add(a, b)
    @precondition {{ a > 0 and b > 0 }}
    @postcondition {{ result == a + b }}
}
