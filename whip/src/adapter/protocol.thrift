include "clientprotocol.thrift"

typedef i32 int
typedef i64 long
typedef string blob

enum IdentityType {
    SERVICE = 0,
    TOKEN = 1,
    PROXY = 2,
}

enum IdentityAttributeType {
    STATE_VARS = 0,
    CALLSITE_SET = 1,
    PROXY_INFO = 2,
}

struct PortConfiguration {
    1: string identifier;
    2: optional string proxy_host;
    3: optional int proxy_port;
    4: list<string> blame_labels;
}

struct Identity {
    1: IdentityType id_type;
    2: string name;
    3: string identifier;
}

struct IdentityAttribute {
    1: Identity identity;
    2: IdentityAttributeType value_type;
    3: blob attribute_data;
    4: list<Identity> referenced_identities;
}

struct Annotated {
    1: blob original_payload;
    2: list<IdentityAttribute> identity_attributes;
    3: list<PortConfiguration> port_configurations;
    4: string from_proxy_name;
}


// --- Attributes ----------------------------------
struct CallSite {
    1: Identity receiver;
    2: string op_name;
    3: list<string> arguments;
    4: blob extra;
}

struct StateVar {
    1: string name;
    2: string value;
    3: CallSite where_set;
}

struct StateVarsAttribute { // STATE_VARS
    1: list<StateVar> state_vars;
}

struct CallSiteSetAttribute { // CALLSITE_SET
    1: list<CallSite> callsite_set;
}

struct ProxyInfoAttribute { //PROXY_INFO
    1: string proxy_name;
    2: string terminus_endpoint;
}
// --- End of Attributes ---------------------------


service Proxy {
    Identity get_this_identity();

    Annotated execute(1: Annotated request);

    list<IdentityAttribute> get_identity_attributes(1: Identity id);
}

