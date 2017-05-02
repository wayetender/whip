from suds.client import Client
import datetime
import gc

def start():
    global last, checkpoints
    last = datetime.datetime.now()
    checkpoints = []

def checkpoint(n):
    global last, checkpoints
    check = datetime.datetime.now()
    checkpoints.append((n, (check - last).total_seconds() * 1000))
    last = check


if __name__ == '__main__':
    url = 'http://localhost:8000/?wsdl'
    client = Client(url)
    client.options.cache.clear()
    #gc.disable()

    sid = client.service.login('test', 3)

    MAX = 10
    CHECKPOINT_EVERY = 2
    n = 1
    start()
    while n <= MAX:
        assert client.service.add(sid, 2, 3) == 8
        if n % CHECKPOINT_EVERY == 0:
            checkpoint(n)
        n += 1
        gc.collect()

    for (k,v) in checkpoints:
        #print "\t%d\t%f" % (k, v)
        print "\t%f" % (v)


