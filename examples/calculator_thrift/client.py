import sys
import common
import logging
import uuid
import time
import random
import traceback
from calc import Adder, AdderDiscovery
from calc.ttypes import *

AdderClient = Adder.Client
AdderDiscoveryClient = AdderDiscovery.Client

def help():
    print "Available Commands:"
    print "signup [username] [password]    - Register a new user account"
    print "login [username] [password]     - Login to a user account"
    print "add [n1] [n2]                   - Get a random adder and compute n1+n2"
    print "register_adder [host] [port]    - Register new adder service"
    print "quit                            - Exits the program"

def get_adder_service(discovery, sid):
    hostinfo = discovery.get_adder_info(sid)
    return common.get_client_with_defaults(AdderClient, hostinfo.host, hostinfo.port)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python client.py DISCOVERY_IP DISCOVERY_PORT"
        sys.exit(1)

    discovery_ip = sys.argv[1]
    discovery_port = int(sys.argv[2])
    discovery = common.get_client_with_defaults(AdderDiscoveryClient, discovery_ip, discovery_port)
    print "connected to discovery service %s:%d" % (discovery_ip, discovery_port)
    help()
    sid = None
    line = raw_input("> ")
    while line != 'quit':
        parts = line.split(' ')
        cmd = parts[0]
        try:
            if cmd == 'signup':
                if discovery.signup(parts[1], parts[2]):
                    print 'Success'
                else:
                    print "Account already taken"
            elif cmd == 'login':
                sid = discovery.login(parts[1], parts[2]) #+ 'wrong'
                if 'error' in sid:
                    print "Could not login: %s" % sid
                    sid = None
                else:
                    print "Successfully logged in"
            elif cmd == 'add':
                if not sid:
                    print "Must login first"
                else:
                    adder = get_adder_service(discovery, sid)
                    result = adder.add(int(parts[1]), int(parts[2]))
                    print "%s + %s = %d" % (parts[1], parts[2], result)
            elif cmd == 'register_adder':
                if not sid:
                    print "Must login first"
                else:
                    discovery.register_adder(sid, parts[1], int(parts[2]))
                    print "successfully registered adder service"
            else:
                print 'unrecognized command'
                help()
            line = raw_input("> ")
        except KeyboardInterrupt:
            line = 'quit'
        except:
            error = sys.exc_info()
            print "error: ", error[0]
            traceback.print_tb(error[2])
            line = raw_input("> ")
