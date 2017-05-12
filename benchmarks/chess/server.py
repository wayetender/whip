import logging
from spyne.application import Application
from spyne.decorator import rpc
from spyne.service import ServiceBase
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode
from spyne.model.primitive import Boolean
from spyne.model.enum import Enum

from spyne.model.complex import Array

from spyne.protocol.soap import Soap11

from spyne.server.wsgi import WsgiApplication

from spyne.model.complex import ComplexModel
import spyne.model.primitive

import chess
import chess.pgn

from datetime import date
import time

import pprint
import sys


logging.getLogger('spyne').setLevel(logging.INFO)
logging.getLogger('spyne.protocol.xml').setLevel(logging.INFO)

DELAY = 0.5

startTime = 0
numGames = 0
requests = 0

NS = "http://www.bennedik.com/webservices/XfccBasic"

Result = Enum('Ongoing', 'WhiteWins', 'BlackWins', 'Draw', 'WhiteWinAdjucated', 'Cancelled', type_name='Result', __namespace__=NS)
MakeAMoveResult = Enum('Success', 'ServerError', 'AuthenticationFailed', 'InvalidGameID', 'NotYourGame', 'NotYourTurn', 'InvalidMoveNumber', 'InvalidMove', 'NoDrawWasOffered', 'LostOnTime', 'YouAreOnLeave', 'MoveIsAmbiguous', type_name='MakeAMoveResult', __namespace__=NS)

class Game:
    def __init__(self, id, black, white, eventDate, site):
        self.board = chess.pgn.Game()
        self.id = id
        self.black = black
        self.white = white
        self.site = site
        self.eventDate = eventDate
        self.drawOffered = False
        self.result = Result.Ongoing

    def my_turn(self, who):
        hasWhite = who == self.white
        return self.result == Result.Ongoing and \
            self.board.end().board().turn % 2 == (0 if hasWhite else 1)

    def my_game(self, who):
        return self.white == who or self.black == who

    def move_count(self):
        return self.board.end().board().turn

    def generate_soap_obj(self, who):
        exporter = chess.pgn.StringExporter()
        self.board.export(exporter, headers=False, variations=False, comments=False)
        game = XfccGame()
        game.id = self.id
        game.black = self.black
        game.white = self.white
        game.hasWhite = who == self.white
        game.myTurn = self.my_turn(who)
        game.daysPlayer = 30
        game.hoursPlayer = 0
        game.minutesPlayer = 0
        game.daysOpponent = 30
        game.hoursOpponent = 0
        game.minutesOpponent = 0
        game.moves = str(exporter)
        game.drawOffered = self.drawOffered
        game.result = self.result
        game.eventDate = self.eventDate
        return game

class XfccGame(ComplexModel):
    __namespace__ = NS
    _type_info = [
        ('id', Integer),
        ('white', Unicode),
        ('black', Unicode),
        ('event', Unicode),
        ('site', Unicode),
        ('myTurn', Boolean),
        ('hasWhite', Boolean),
        ('daysPlayer', Integer),
        ('hoursPlayer', Integer),
        ('minutesPlayer', Integer),
        ('daysOpponent', Integer),
        ('hoursOpponent', Integer),
        ('minutesOpponent', Integer),
        ('moves', Unicode),
        ('drawOffered', Boolean),
        ('result', Result),
        ('eventDate', Unicode)
    ]

    id = Integer
    white = Unicode
    black = Unicode
    event = Unicode
    site = Unicode
    myTurn = Boolean
    hasWhite = Boolean
    daysPlayer = Integer
    hoursPlayer = Integer
    minutesPlayer = Integer
    daysOpponent = Integer
    hoursOpponent = Integer
    minutesOpponent = Integer
    moves = Unicode
    drawOffered = Boolean
    result = Result
    eventDate = Unicode

res = Array(XfccGame)
res.__type_name__ = 'ArrayOfXfccGame'
res.__namespace__ = NS

class ChessService(ServiceBase):
    __namespace__ = NS
    
    @rpc(Unicode, Unicode, _returns=res)
    def GetMyGames(ctx, username, password):
        global DELAY, requests
        #time.sleep(.459)
        requests += 1
        games = ctx.app.gamesByUser.get(username, [])
        a = [g.generate_soap_obj(username) for g in games]
        return a

    @rpc(Unicode, Unicode, Integer, Boolean, Boolean, Integer, Unicode, Boolean, Boolean, Unicode, _returns=MakeAMoveResult)
    def MakeAMove(ctx, username, password, gameId, resign, acceptDraw, movecount, myMove, offerDraw, claimDraw, myMessage):
        global DELAY, requests
        requests += 1
        #time.sleep(.465)
        game = ctx.app.games.get(gameId)
        if not game:
            return MakeAMoveResult.InvalidGameID
        if not game.my_game(username):
            return MakeAMoveResult.NotYourGame
        if not game.my_turn(username):
            return MakeAMoveResult.NotYourTurn
        
        if acceptDraw:
            if not game.drawOffered:
                return MakeAMoveResult.NoDrawWasOffered
            else:
                game.result = Result.Draw
                return MakeAMoveResult.Success
        
        if claimDraw:
            if game.board.end().board().can_claim_draw():
                game.result = Result.Draw
                return MakeAMoveResult.Success
            else:
                return MakeAMoveResult.InvalidMove

        if resign:
            game.result = Result.WhiteWins if game.black == username else Result.BlackWins
            return MakeAMoveResult.Success

        if game.move_count() != movecount - 1:
            return MakeAMoveResult.InvalidMoveNumber

        try:
            move = game.board.end().board().push_san(myMove)
            game.board.end().add_main_variation(move)
        except ValueError:
            return MakeAMoveResult.InvalidMove 

        if offerDraw:
            game.drawOffered = True

        return MakeAMoveResult.Success

    @rpc(Unicode, Unicode, _returns=Integer)
    def MakeGame(ctx, whiteUser, blackUser):
        global DELAY, startTime, numGames, requests
        if numGames == 0:
            startTime = time.time()
        numGames += 1
        requests += 1
        #time.sleep(DELAY)
        today = date.today().strftime('%Y.%m.%d')
        game_id = numGames
        game = Game(game_id, blackUser, whiteUser, today, 'site')
        ctx.app.games.clear()
        ctx.app.games[game_id] = game
        ctx.app.gamesByUser.clear()
        ctx.app.gamesByUser[whiteUser] = [game] # ctx.app.gamesByUser.get(whiteUser, []) + [game]
        ctx.app.gamesByUser[blackUser] = [game] #ctx.app.gamesByUser.get(blackUser, []) + [game]
        return game_id

class ChessApplication(Application):
    def __init__(self, *args, **kwargs):
        self.games = {}
        self.gamesByUser = {}
        super(ChessApplication, self).__init__(*args, **kwargs)

    def call_wrapper(self, ctx):
        try:
            return ctx.service_class.call_wrapper(ctx)

        except KeyError:
            raise ResourceNotFoundError(ctx.in_object)


from lxml import etree, objectify
def _on_method_return_document(ctx):
    root = ctx.out_document
    return
    #s = etree.tostring(root, pretty_print=True)
    
    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'): continue
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i+1:]
    objectify.deannotate(root, cleanup_namespaces=True)

    #print(etree.tostring(root, pretty_print=True))
ChessService.event_manager.add_listener('method_return_document',
                                             _on_method_return_document)


application = ChessApplication([ChessService],
    tns=NS,
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

def make_app():
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    
    from wsgiref.simple_server import make_server, WSGIRequestHandler
    wsgi_app = WsgiApplication(application)
    class QuietHandler(WSGIRequestHandler):
        def log_request(*args, **kw): pass

    return make_server('0.0.0.0', 8000, wsgi_app, handler_class=QuietHandler)

if __name__ == '__main__':
    import sys
    import test_utils
    import os
    import psutil
    from threading import Thread
    server = make_app()
    t1 = Thread(target=server.serve_forever)
    t1.daemon = True
    t1.start()
    test_utils.setup_adapter_only('adapter.yaml', 1)()
    
    
    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)3d %(funcName)20s() -- %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.INFO)
    
    while True:
        process = psutil.Process(os.getpid())
        process = process.children(recursive=True)[1]
        while True:
            if startTime > 0:
                sz = os.path.getsize('/tmp/lru3.dat') if os.path.exists('/tmp/lru3.dat') else 0
                mem = process.memory_info()
                print "%s,%s,%s,%s" % (time.time() - startTime, mem.rss / 1024, sz / 1024, requests)
                sys.stdout.flush()
            time.sleep(2)
