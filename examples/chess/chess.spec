
 # Methods (2):
 #    GetMyGames(xs:string username, xs:string password)
 #    MakeAMove(xs:string username, xs:string password, xs:int gameId, xs:boolean resign, xs:boolean acceptDraw, xs:int movecount, xs:string myMove, xs:boolean offerDraw, xs:boolean claimDraw, xs:string myMessage)
 # Types (4):
 #    ArrayOfXfccGame
 #    MakeAMoveResult
 #    Result
 #    XfccGame

ghost UserInfo {
    @identifier username,
}

ghost Game {
    @identifier gameId,
    @immutable outcome,
    drawOffered, # @mutable
    moves # @mutable
}

service Chess {
    @identifies games:Game[] by {{
        for game in result:
            yield (game['id'])
    }}
    @initializes {{
        #print "i see %s" % result
        for game in result:
            gameGhost = games[str(game['id'])]
            initialize(gameGhost, 'outcome', game['result']);
            initialize(gameGhost, 'drawOffered', game['drawOffered'])
            initialize(gameGhost, 'moves', game['moves'].split(' '))
    }}
    GetMyGames(username, password)
    
    @identifies game:Game by {{ gameId }}
    @precondition {{ game.outcome != 'Ongoing' or game.outcome == '' }}
    #@precondition {{ isValidPGNString(myMove) }}
    @precondition {{ not acceptDraw or game.drawOffered }}
    @precondition {{ movecount == moves.length }}
    @updates {{
        if result == 'Success' and acceptDraw:
            update(game, 'outcome', 'Draw')
    }}
    MakeAMove(username, password, gameId, resign, acceptDraw, movecount, myMove, offerDraw, claimDraw, myMessage)
}
