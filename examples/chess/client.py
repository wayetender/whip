from suds.client import Client
import random
import string
import logging

HOST = 'http://localhost:8000/?wsdl'
PASSWORD = 'password'

logging.getLogger('suds').setLevel(logging.INFO)

def fresh_user():
    N = 8
    return 'user-%s' % ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(N))

def fresh_game(client, whiteUser, blackUser):
    return client.service.MakeGame(whiteUser, blackUser)

def get_client(host = HOST):
    client = Client(host)
    client.options.cache.clear()
    assert getattr(client.service, 'MakeAMove')
    assert getattr(client.service, 'GetMyGames')
    return client

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

def test_single_move():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    res = client.service.MakeAMove(white, PASSWORD, game_id, False, False, 1, 'e4', False, False, '')
    assert res == 'Success'
    games = client.service.GetMyGames(white, PASSWORD)[0]
    assert len(games) == 1
    game = games[0]
    assert game.id == game_id
    assert game.moves == "1. e4 *"
    assert game.hasWhite
    assert not game.myTurn
    games = client.service.GetMyGames(black, PASSWORD)[0]
    assert len(games) == 1
    game = games[0]
    assert not game.hasWhite
    assert game.myTurn

def test_two_moves():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    res = client.service.MakeAMove(white, PASSWORD, game_id, False, False, 1, 'e4', False, False, '')
    assert res == 'Success'
    res = client.service.MakeAMove(black, PASSWORD, game_id, False, False, 2, 'd5', False, False, '')
    assert res == 'Success'
    game = client.service.GetMyGames(white, PASSWORD)[0][0]
    assert game.myTurn
    assert game.moves == "1. e4 d5 *"
    game = client.service.GetMyGames(black, PASSWORD)[0][0]
    assert not game.myTurn

def test_notmyturn():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    res = client.service.MakeAMove(black, PASSWORD, game_id, False, False, 1, 'e4', False, False, '')
    assert res == 'NotYourTurn'

def test_invalidmove():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    res = client.service.MakeAMove(white, PASSWORD, game_id, False, False, 1, 'e5', False, False, '')
    assert res == 'InvalidMove'

def test_invalidgame():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    res = client.service.MakeAMove(black, PASSWORD, -1, False, False, 1, 'e4', False, False, '')
    assert res == 'InvalidGameID'

def test_nodraw():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    res = client.service.MakeAMove(white, PASSWORD, game_id, False, True, 1, 'e4', False, False, '')
    assert res == 'NoDrawWasOffered'

def test_invalidmovenumber():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    res = client.service.MakeAMove(white, PASSWORD, game_id, False, False, 1, 'e4', False, False, '')
    assert res == 'Success'
    res = client.service.MakeAMove(black, PASSWORD, game_id, False, False, 1, 'd5', False, False, '')
    assert res == 'InvalidMoveNumber'

def test_draw():
    client = get_client()
    white = fresh_user()
    black = fresh_user()
    game_id = fresh_game(client, white, black)
    res = client.service.MakeAMove(white, PASSWORD, game_id, False, False, 1, 'e4', True, False, '')
    assert res == 'Success'
    game = client.service.GetMyGames(black, PASSWORD)[0][0]
    assert game.drawOffered
    res = client.service.MakeAMove(black, PASSWORD, game_id, False, True, 1, '', False, False, '')
    assert res == 'Success'
    game = client.service.GetMyGames(white, PASSWORD)[0][0]
    assert game.result == 'Draw'
    game = client.service.GetMyGames(black, PASSWORD)[0][0]
    assert game.result == 'Draw'
