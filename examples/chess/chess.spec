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
    GetMyGames(username, password)
    @identifies games:Game[] by {{
        for game in result:
            yield (game['id'])
    }}
    @initializes {{
        #print "i see %s" % result
        for game in result:
            gameGhost = games[str(game['id'])]
            if game['result'] != 'Ongoing':
                initialize(gameGhost, 'outcome', game['result']);
    }}
    @updates {{
        for game in result:
            gameGhost = games[str(game['id'])]
            update(gameGhost, 'drawOffered', game['drawOffered'])
            update(gameGhost, 'moves', game['moves'].split(' '))        
    }}
    
    
    MakeAMove(username, password, gameId, resign, acceptDraw, movecount, myMove, offerDraw, claimDraw, myMessage)
    @identifies game:Game by {{ gameId }}
    @precondition {{ game.outcome != 'Ongoing' or game.outcome == '' }}
    #@precondition {{ isValidPGNString(myMove) }}
    @precondition {{ not acceptDraw or game.drawOffered }}
    @precondition {{ movecount == moves.length }}
    @updates {{
        if result == 'Success' and acceptDraw:
            update(game, 'outcome', 'Draw')
    }}
}
