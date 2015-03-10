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

logging.getLogger('suds').setLevel(logging.INFO)

class A:
    def serve_forever(self):
        while True:
            time.sleep(1)

setup_f = test_utils.setup_adapter('adapter.yaml', server.make_app())

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

@with_setup(setup_f, test_utils.teardown_adapter)
def test_fresh_game():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    games = client.service.GetMyGames(white, PASSWORD)[0]
    assert len(games) == 1
    game = games[0]
    assert game.id == game_id
    assert game.white == white
    assert game.black == black
    assert game.moves == "*"
    assert game.result == 'Ongoing'
    assert game.hasWhite
    assert game.myTurn
    games = client.service.GetMyGames(black, PASSWORD)[0]
    assert len(games) == 1
    game = games[0]
    assert game.id == game_id
    assert game.white == white
    assert game.black == black
    assert game.moves == "*"
    assert game.result == 'Ongoing'
    assert not game.hasWhite
    assert not game.myTurn
    assert len(test_utils.adapter.output) == 0


