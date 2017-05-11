# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import requests
from requests_oauthlib import OAuth1
from urlparse import parse_qs
import logging
import sys
sys.path.append('../')
import test_utils
import os

requests.packages.urllib3.disable_warnings()
# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig() 
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True




REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

CONSUMER_KEY = "________KEY_________"
CONSUMER_SECRET = "________SECRET__________"

OAUTH_TOKEN = "______________TOKEN____________________"
OAUTH_TOKEN_SECRET = "_______________SECRET________________"


def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=OAUTH_TOKEN,
                resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth

nrequests = 0

def runtests(oauth):
    global nrequests
    r = test_utils.measure('friends', lambda: requests.get(url="https://127.0.0.1:3912/1.1/friends/list.json?user_id=%s" % nrequests, auth=oauth, verify=False))
    friend = r.json()["users"][0]["id_str"]
    r = test_utils.measure('timeline', lambda: requests.get(url="https://127.0.0.1:3912/1.1/statuses/user_timeline.json?user_id=%s" % friend, auth=oauth, verify=False))
    tweet = r.json()[0]['id_str']
    r = test_utils.measure('retweet', lambda: requests.get(url="https://127.0.01:3912/1.1/statuses/retweet/__id__.json?tweet_id=%s" % tweet, auth=oauth, verify=False))
    nrequests += 3
    

if __name__ == "__main__":
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        #r = requests.get(url="https://localhost:5000/1.1/statuses/mentions_timeline.json", auth=oauth, verify=False)
        
        NUM_TRIALS = int(os.getenv('NUM_OPS')) / 3
        print "starting %d trials..." % NUM_TRIALS
        report = []
        num_requests = 1
        
        #test_utils.setup_adapter_only('adapter.yaml', 1)()
        for trial in xrange(NUM_TRIALS):
            runtests(oauth)
            for [m] in test_utils.measurements.values():
                print "%s,%s" % (num_requests, m * 1000)
                num_requests += 1
            test_utils.measurements.clear()
            #if trial % 100 == 0:
            #    print trial
            #    pass
                #import gc
                #gc.collect(2)
                #mem = process.memory_info()
                #print mem
                #print mem / 1024
            #stats = test_utils.get_adapter_stats()
            #report.append((traffic, stopwatch, stats))
            #test_utils.teardown_adapter_only()
        #    print "Trial %d / %d: %s" % (trial+1, NUM_TRIALS, stopwatch)
        print "-- End of %d trials --" % NUM_TRIALS
