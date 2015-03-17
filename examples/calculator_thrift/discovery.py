'''
Simple adder service
'''
import sys
import common
import logging
import uuid
import time
import random
from calc import AdderDiscovery
from calc.ttypes import *

AdderDiscoveryProcessor = AdderDiscovery.Processor

logger = logging.getLogger(__name__)

class Handler:
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.adders = []

    def signup(self, username, password):
        if username not in self.users.keys():
            self.users[username] = password
            return True
        return False

    def login(self, username, password):
        if (username not in self.users.keys()) or (self.users[username] != password):
            return "error"
        sid = str(uuid.uuid4())[0:6]
        self.sessions[sid] = username
        return sid

    def register_adder(self, sid, host, port):
        if sid not in self.sessions:
            raise NotLoggedIn()
        logger.debug("registering adder service %s:%d" % (host, port))
        self.adders.append(Hostinfo(host, port))

    def get_adder_info(self, sid):
        if sid not in self.sessions:
            raise NotLoggedIn()
        logger.debug("returning random service to %s" % self.sessions[sid])
        return random.choice(self.adders)

if __name__ == '__main__':
    processor = AdderDiscoveryProcessor(Handler())
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 38000
    logger.info("adder discovery service listening on %d" % port)
    common.init_with_defaults_and_run_forever(processor, port)

