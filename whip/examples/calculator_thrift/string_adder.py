'''
Simple adder service
'''
import sys
import common
import logging
from calc import StringAdder
from calc.ttypes import *
import time

StringAdderProcessor = StringAdder.Processor

logger = logging.getLogger(__name__)

class Handler:
    def add(self, a, b):
        return int(str(a) + str(b))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python adder.py MY_IP MY_PORT"
        sys.exit(1)

    my_ip = sys.argv[1]
    my_port = int(sys.argv[2])

    processor = StringAdderProcessor(Handler())
    logger.info("string adder service listening on %d" % my_port)
    server = common.init_with_defaults(processor, my_port)

    common.run_forever(server)
