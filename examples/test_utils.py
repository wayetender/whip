import subprocess
from subprocess import Popen
import time
import sys
from threading import Semaphore
from threading import Thread 
import logging
import os
import server
import multiprocessing

adapterlog = logging.getLogger('adapter')

adapter = None

class WsgiServerRunner(object):
    def __init__(self, server):
        self.server_process = multiprocessing.Process(target=server.serve_forever)

    def start(self):
        self.server_process.start()

    def stop(self):
        self.server_process.terminate()
        self.server_process.join()
        del(self.server_process)

class Adapter(Thread):
    def __init__(self, configfile):
        Thread.__init__(self)
        self.started = Semaphore(0)
        self.finished = False
        self.output = []
        self.error = False
        self.daemon = True
        self.configfile = configfile

    def run(self):
        adapterapp = '%s/../bin/adapter' % os.path.dirname(os.path.abspath(__file__))
        self.p = Popen([adapterapp, self.configfile], stderr=subprocess.PIPE, close_fds=True)
        started = False
        for line in iter(self.p.stderr.readline, ''):
            line = line.replace('\r', '').replace('\n', '')
            if 'Generating LALR tables' in line:
                continue
            #print "i see line " + line
            #sys.stdout.flush()
            if not started:
                if 'Registering proxy endpoint' in line:
                    started = True
                    sys.stdout.flush()
                    self.started.release()
                else:
                    self.error = True
                    self.output.append(line)
                    self.started.release()
                    self.p.terminate()
            else:
                self.output.append(line)
                adapterlog.info(line)

    def waitForStartup(self):
        self.started.acquire()
        if self.error:
            self.finished = True
            subprocess.call('pkill -TERM -P %d' % self.p.pid, shell=True)
            raise ValueError("did not startup: %s" % '\n'.join(self.output))

    def signalFinish(self):
        self.finished = True
        subprocess.call('pkill -TERM -P %d' % self.p.pid, shell=True)

def setup_adapter(configfile, server):
    def f():
        global adapter, serverapp
        if "DYLD_INSERT_LIBRARIES" in os.environ:
            del os.environ["DYLD_INSERT_LIBRARIES"]
        serverapp = WsgiServerRunner(server)
        serverapp.start()
        adapter = Adapter(configfile)
        adapter.start()
        adapter.waitForStartup()
    return f

def teardown_adapter():
    global adapter, serverapp
    adapter.signalFinish()
    serverapp.stop()
