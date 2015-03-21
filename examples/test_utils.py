import subprocess
from subprocess import Popen
import time
import datetime
import sys
from threading import Semaphore
from threading import Thread 
import logging
import os
import multiprocessing
import pickle

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
        self.p = Popen([adapterapp, self.configfile], stderr=subprocess.PIPE, close_fds=True, stdin=subprocess.PIPE)
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
                if 'Registering proxy endpoint' in line:
                    continue
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


def get_adapter_stats():
    global adapter
    cnt = len(adapter.output)
    items = ['traffic', 'timing', 'contracts', 'redirector', 'ghosts']
    ret = {}
    for item in items:
        adapter.p.stdin.write("%s\n" % item)
        while len(adapter.output) == cnt:
            time.sleep(0.01)
        t = adapter.output[cnt]
        t = pickle.loads(t.decode('base64'))
        del adapter.output[cnt]
        ret[item] = t
    return ret

def format_stats(traffic, timing, adapterstats):
    total_time = timing.elapsed.total_seconds() * 1000
    total_contract_time = reduce(lambda s,i: s+sum(i), adapterstats['contracts'].values(), 0)
    total_adapter_time = reduce(lambda s,i: s+sum(i), adapterstats['timing'].values(), 0)
    total_deacon_traffic = reduce(lambda s,i: s+sum(i), adapterstats['traffic'].values(), 0)
    total_redirector_traffic = adapterstats['redirector']
    requests = total_redirector_traffic / 59
    msg = "Total RPCs, Total Time (ms), Total Contract Time (ms), Total adapter time (ms), Total component traffic (bytes), Total inter-adapter traffic (bytes), Total redirector traffic (bytes)\n"
    msg += "%d\t%f\t%f\t%f\t%d\t%d\t%d\n" % (requests, total_time, total_contract_time, total_adapter_time, traffic.bytestx + traffic.bytesrx, total_deacon_traffic, total_redirector_traffic)

    msg += "\nRPCs\n\n"
    msg += "RPC Contract time (ms),Adapter time (ms),Inter-adapter traffic (bytes),Total identities (ghosts+services) sent\n"
    for k in adapterstats['contracts'].keys():
        contract_time = sum(adapterstats['contracts'][k]) / (len(adapterstats['contracts'][k]) / 2)
        adapter_time = sum(adapterstats['timing'][k]) / len(adapterstats['timing'][k])
        traffic = sum(adapterstats['traffic'][k]) / len(adapterstats['traffic'][k])
        ghosts = sum(adapterstats['ghosts'][k]) / len(adapterstats['ghosts'][k])
        msg += "%s\t%f\t%f\t%d\t%d\n" % (k, contract_time, adapter_time, traffic, ghosts)
    return msg

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

def setup_adapter_only(configfile):
    def f():
        global adapter
        if "DYLD_INSERT_LIBRARIES" in os.environ:
            del os.environ["DYLD_INSERT_LIBRARIES"]
        adapter = Adapter(configfile)
        adapter.start()
        adapter.waitForStartup()
    return f


def teardown_adapter_only():
    global adapter
    adapter.signalFinish()


def teardown_adapter():
    global adapter, serverapp
    adapter.signalFinish()
    serverapp.stop()

class UsageTracker:
    def __init__(self):
        self.bytestx = 0
        self.bytesrx = 0
    def __repr__(self):
        return "Bytes Sent: %d Bytes Received: %d" % (self.bytestx, self.bytesrx)

class StopWatch(object):
    def __init__(self, name):
        self.name = name
        self.start = datetime.datetime.now()

    def stop(self):
        self.elapsed = datetime.datetime.now() - self.start

    def __repr__(self):
        if not self.elapsed:
            return "stopwatch %s: <running>" % self.name
        else:
            return "stopwatch %s: %f ms" % (self.name, self.elapsed.total_seconds() * 1000)


def track_traffic(client, tracker = None):
    orig_write = client._oprot.trans.write
    orig_read = client._iprot.trans.read
    if not tracker:
        tracker = UsageTracker()
    def mywrite(b):
        tracker.bytestx += len(b)
        return orig_write(b)
    def myread(a):
        r = orig_read(a)
        tracker.bytesrx += len(r)
        return r
    client._oprot.trans.write = mywrite
    client._iprot.trans.read = myread
    return tracker

