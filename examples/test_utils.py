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
import math

adapterlog = logging.getLogger('adapter')

adapter = None


def mean(s): 
    return sum(s) * 1.0 / len(s)
def variance(s): 
    avg = mean(s)
    return math.sqrt(mean(map(lambda x: (x - avg)**2, s)))

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

def format_stats(report):
    cnt = len(report)
    total_times = []
    total_contract_times = []
    total_adapter_times = []
    total_deacon_traffics = []
    total_redirector_traffics = []
    total_requests = []
    for traffic, timing, adapterstats in report:
        total_times.append(timing.elapsed.total_seconds() * 1000)
        total_contract_times.append(reduce(lambda s,i: s+sum(i), adapterstats['contracts'].values(), 0))
        total_adapter_times.append(reduce(lambda s,i: s+sum(i), adapterstats['timing'].values(), 0))
        total_deacon_traffics.append(reduce(lambda s,i: s+sum(i), adapterstats['traffic'].values(), 0))
        total_redirector_traffics.append(adapterstats['redirector'])
        total_requests.append(adapterstats['redirector'] / 59)
    total_time = mean(total_times)
    total_contract_time = mean(total_contract_times)
    total_adapter_time = mean(total_adapter_times)
    total_deacon_traffic = mean(total_deacon_traffics)
    total_redirector_traffic = mean(total_redirector_traffics)
    total_requests = mean(total_requests)
    msg = "Trials,Total RPCs, Total Time (ms), stdev, Total Contract Time (ms), stdev, Total adapter time (ms), stdev, Total component traffic (bytes), Total inter-adapter traffic (bytes), Total redirector traffic (bytes)\n"
    msg += "%d\t%d\t%f\t%f\t%f\t%f\t%f\t%f%d\t%d\t%d\n" % (cnt, total_requests, total_time, variance(total_times), total_contract_time, variance(total_contract_times), total_adapter_time, variance(total_adapter_times), traffic.bytestx + traffic.bytesrx, total_deacon_traffic, total_redirector_traffic)

    f = {}
    for t in ['contracts','timing','traffic','ghosts']:
        d = f.get(t, {})    
        f[t] = d
        for _,_,adapterstats in report:
            for k,v in adapterstats[t].items():
                s = d.get(k, [])
                d[k] = s + v

    msg += format_rpc_stats(cnt, f)

    return msg

    
def format_rpc_stats(trials,adapterstats):
    msg = "\nRPCs\n\n"
    msg += "RPC, Trials, Contract time (ms),stdev,Adapter time (ms),stdev,Inter-adapter traffic (bytes),Total identities (ghosts+services) sent\n"
    contract_time = []
    adapter_time = []
    for k in adapterstats['contracts'].keys():
        contract_time.append(sum(adapterstats['contracts'][k][0::2]))
        adapter_time.append(sum(adapterstats['timing'][k]))
        traffic = sum(adapterstats['traffic'][k]) / len(adapterstats['traffic'][k])
        ghosts = sum(adapterstats['ghosts'][k]) / len(adapterstats['ghosts'][k])
        msg += "%s\t%d\t%f\t%f\t%f\t%f\t%d\t%d\n" % (k, trials, mean(contract_time), variance(contract_time), mean(adapter_time), variance(adapter_time), traffic, ghosts)
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

