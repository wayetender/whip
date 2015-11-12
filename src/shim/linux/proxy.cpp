#include "proxy.h"
#include <transport/TSocket.h>
#include <transport/TBufferTransports.h>
#include <protocol/TBinaryProtocol.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdint.h>
#include <dlfcn.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <string.h>
#include <arpa/inet.h>
#include <errno.h>
#include <sys/select.h>
#include <string>
#include <boost/lexical_cast.hpp>

using namespace apache::thrift;
using namespace apache::thrift::protocol;
using namespace apache::thrift::transport;
using namespace ClientProxy;
using boost::shared_ptr;


const char* default_host = "localhost";
const char* raddress = NULL;
const char* rport = NULL;
void __attribute__((constructor)) shim_init(void)
{
    raddress = getenv("SHIM_CLIENT_ADDRESS");
    if (raddress == NULL) 
    {
        raddress = default_host;
    }
    rport = getenv("SHIM_CLIENT_PORT");
}

int connect(int sockfd, const struct sockaddr *res, socklen_t addrlen)
{
    static int (*original_connect)(int, const struct sockaddr*, socklen_t) = NULL;
    if (!original_connect)
        original_connect = (int (*)(int, const sockaddr*, socklen_t))(dlsym(RTLD_NEXT, "connect"));

    int error;
    int port = ntohs(((struct sockaddr_in*)res)->sin_port);
    char address[1024] = "";

    if (port == 9090) {
        return original_connect(sockfd, res, addrlen);
    }
    
    TTransport* trans;
    RedirectionClient* client = NULL;
    if (rport == NULL) 
    {
        fprintf(stderr, "error: SHIM_CLIENT_PORT not set; not proxying connections\n");
    } 
    else 
    {
        int iport = atoi(rport);
        try 
        {
            shared_ptr<TSocket> socket(new TSocket(raddress, iport));
            trans = new TFramedTransport(socket);
            shared_ptr<TProtocol> protocol(new TBinaryProtocol(shared_ptr<TTransport>(trans)));
            client = new RedirectionClient(protocol);
        } 
        catch(...) 
        {
            fprintf(stderr, "error: could not setup socket to client proxy at %s:%d\n", address, iport);
        }
    }
    if (res->sa_family != AF_INET || client == NULL)
    {
        return original_connect(sockfd, res, addrlen);
    }
    inet_ntop(AF_INET, &((struct sockaddr_in*)res)->sin_addr, address, 1024);
    // try 
    // {
        RedirectionInfo info;
        trans->open();
        //fprintf(stderr, "getting redirection info for %s:%d\n", address, port);
        client->get_redirection_info(info, address, port);
        trans->close();
        if (info.is_proxied)
        {
            struct addrinfo hints, *server_info;
            memset(&hints, 0, sizeof(hints));
            hints.ai_family = AF_INET;
            hints.ai_socktype = SOCK_STREAM;
            const char* port_str = boost::lexical_cast<std::string>(info.port).c_str();
            //fprintf(stderr, "redirecting to %s:%s\n", info.address.c_str(), port_str);
            error = getaddrinfo(info.address.c_str(), port_str, &hints, &server_info);
            if (error)
            {
                fprintf(stderr, "error: %s\n", gai_strerror(error));
                client = NULL;
            }
            else
            {
                //checking for error here is a bad idea due to nonblocking sockets
                return original_connect(sockfd, server_info->ai_addr, server_info->ai_addrlen);   
            }
        }
        else
        {
            fprintf(stderr, "warning: connection to %s:%d is not listed as proxied\n", address, port);
        }
    // } 
    // catch(...) 
    // {
        // fprintf(stderr, "error: could not connect to client proxy\n");
        // client = NULL;
        // throw "error";
    // }

    //    error = connect(sockfd, server_info->ai_addr, server_info->ai_addrlen);

    return original_connect(sockfd, res, addrlen);
}




// void __attribute__((destructor)) proxy_fini(void)
// {
//     fprintf(stderr, "%s", "proxy_fini()s\n");
// }


