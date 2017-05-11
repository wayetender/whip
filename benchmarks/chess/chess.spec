

service Chess {

    GetMyGames(username, password)
    @identifies g:Chess[] by {{ 
        for game in result: 
            nmoves = len(split('[0-9]+\. ', game['moves']))
            yield ('127.0.0.1:8000', str((game['id'], game['drawOffered'], nmoves)))
            if game['drawOffered']:
                 yield ('127.0.0.1:8000', str((game['id'], False, nmoves)))
    }}
    @postcondition {{
        import chess.pgn
        for game in result:
            try: chess_pgn_read_game(StringIO(game['moves']))
            except: assert False
        return True
    }}

    MakeGame(whitePlayer, blackPlayer)
    @identifies gas:Chess[] by {{ 
        yield ('127.0.0.1:8000', str((result, False, 0)))
    }}

    MakeAMove(username, password, gameId, resign, acceptDraw, movecount, myMove, offerDraw, claimDraw, myMessage)
    @where this is {{  str((gameId, acceptDraw, movecount)) }}
    @postcondition {{ result != "NoDrawWasOffered" }}
    @postcondition {{ result != "InvalidGameID" }}


}
