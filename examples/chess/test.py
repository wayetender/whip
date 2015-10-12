import sys
sys.path.append('../')
import server
from suds.client import Client
import logging
from nose.tools import with_setup
import test_utils
import random
import string
import time

setup_f = test_utils.setup_adapter('adapter.yaml', server.make_app())

logging.getLogger('spyne.protocol.xml').setLevel(logging.INFO)

PASSWORD = 'password'

def get_client():
    url = 'http://localhost:8000/?wsdl'
    client = Client(url)
    client.options.cache.clear()
    assert getattr(client.service, 'MakeAMove')
    assert getattr(client.service, 'GetMyGames')
    return client

def fresh_user():
    N = 8
    return 'user-%s' % ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(N))

def fresh_game(client, whiteUser, blackUser):
    return client.service.MakeGame(whiteUser, blackUser)

def run_maintests():
    total = test_utils.StopWatch('total')
    client = get_client()
    tracker = test_utils.track_suds_traffic(client)
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    test_utils.measure('GetMyGames', lambda: client.service.GetMyGames(white, PASSWORD))
    
    res = test_utils.measure('MakeAMove', lambda: client.service.MakeAMove(white, PASSWORD, game_id, False, False, 1, 'e4', False, False, ''))
    assert res == 'Success'
    test_utils.measure('GetMyGames', lambda: client.service.GetMyGames(white, PASSWORD))
    res = test_utils.measure('MakeAMove', lambda: client.service.MakeAMove(black, PASSWORD, game_id, False, False, 2, 'd5', False, False, ''))
    assert res == 'Success'
    game = test_utils.measure('GetMyGames', lambda: client.service.GetMyGames(white, PASSWORD)[0][0])
    assert game.myTurn
    assert game.moves == "1. e4 d5 *"
    game = test_utils.measure('GetMyGames', lambda: client.service.GetMyGames(black, PASSWORD)[0][0])
    assert not game.myTurn
    if len(test_utils.adapter.output) != 0:
        print test_utils.adapter.output
        assert False
    total.stop()
    return (tracker, total)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)3d %(funcName)20s() -- %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    NUM_TRIALS = 10
    print "starting %d trials..." % NUM_TRIALS
    report = []
    for trial in xrange(NUM_TRIALS):
        setup_f()
        (traffic, stopwatch) = run_maintests()
        stats = test_utils.get_adapter_stats()
        report.append((traffic, stopwatch, stats))
        test_utils.teardown_adapter()
        print "Trial %d / %d: %s" % (trial+1, NUM_TRIALS, stopwatch)
    print "-- End of %d trials --" % NUM_TRIALS
    print test_utils.format_stats(report)

