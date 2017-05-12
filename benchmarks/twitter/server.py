
from flask import Flask
from flask import request
from flask import make_response
import urllib2
import socket
import json
import threading
import time
import json


from flask import Flask
app = Flask(__name__)

requests = 0

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/1.1/friends/list.json")
def friends_list():
    global requests, startTime
    if requests == 0:
        startTime = time.time()
    requests += 1
    return json.dumps({'users': 
        [{'id_str': '11%s' % str(requests).zfill(10)}]})

@app.route("/1.1/statuses/user_timeline.json")
def user_timeline():
    global requests, startTime
    if requests == 0:
        startTime = time.time()
    requests += 1
    return json.dumps([{
        'created_at': 'Thu Jan 18 00:10:45 +0000 2007',
        'id_str': '21%s' % str(requests).zfill(10)}])

@app.route("/1.1/statuses/retweet/__id__.json")
def retweet():
    global requests, startTime
    if requests == 0:
        startTime = time.time()
    requests += 1
    return json.dumps([])


if __name__ == "__main__":
    context = ('server.pem', 'server.pem')
    t = threading.Thread(target=lambda: app.run(port=3912, ssl_context=context, threaded=True, debug=False))
    t.setDaemon(True)
    t.start()
    import sys
    import test_utils
    test_utils.setup_adapter_only('adapter.yaml', 0)()
    import psutil
    import os
    startTime = 0
    try:
        process = psutil.Process(os.getpid())
        process = process.children(recursive=True)[1]
        while True:
            if startTime > 0:
                sz = os.path.getsize('/tmp/lru3.dat') if os.path.exists('/tmp/lru3.dat') else 0
                mem = process.memory_info()
                print "%s,%s,%s,%s" % (time.time() - startTime, mem.rss / 1024, sz / 1024, requests)
                sys.stdout.flush()
            time.sleep(2)
    except KeyboardInterrupt:
        pass
