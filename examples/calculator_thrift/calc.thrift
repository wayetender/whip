namespace py calc

typedef i32 int

struct Hostinfo {
    1: string host;
    2: int port;
}

service Adder {
    // adds two numbers together
    int add(1: int a, 2: int b);
}

exception NotLoggedIn { }

service AdderDiscovery {
    // registers a new account, returns false if account already registered
    bool signup(1: string username, 2: string password);
    
    // returns session id or "error" if unsuccessful login
    string login(1: string username, 2: string password);
    
    // registers a new adder service for discovery
    void register_adder(1: string sid, 2: string host, 3: int port) throws (1: NotLoggedIn e);

    // returns the host information for an adder service
    Hostinfo get_adder_info(1: string sid) throws (1: NotLoggedIn e);

    void dumb(1: string host, 2: int port)
}


// To make things fun
service StringAdder {
    // concatenates the string representation of two numbers together
    int add(1: int a, 2: int b);
}

