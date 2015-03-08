#!/usr/local/bin/thrift --gen cpp

namespace cpp ClientProxy

struct RedirectionInfo {
    1: bool is_proxied;
    2: string address;
    3: i32 port;
}

service Redirection {
    RedirectionInfo get_redirection_info(1: string address, 2: i32 port);
}
