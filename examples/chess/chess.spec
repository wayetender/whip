
service Chess {

    ghost Game {
        @identifier gameId,
        @immutable outcome,
        @immutable white,
    }

    GetMyGames(username, password)
    @identifies games:Game[] by {{ for game in result: yield (game['id']) }}
    @initializes {{
        for game in result:
            gameGhost = games[game['id']]
            initialize(gameGhost, 'white', game['white'])
            if game['result'] != 'Ongoing':
                initialize(gameGhost, 'outcome', game['result']);
    }}
    
    MakeAMove(username, password, gameId, resign, acceptDraw, movecount, myMove, offerDraw, claimDraw, myMessage)
    @identifies game:Game by {{ gameId }}
    @precondition {{ isUnknown(game.outcome) }}
    @precondition {{ not acceptDraw or game.drawOffered }}
    #@precondition {{ acceptDraw or resign or movecount == len(split('[0-9]+\. ', game.moves)) }}
    @postcondition {{
        if not (acceptDraw or resign or movecount % 2 == (1 if username == game.white else 0)):
            return result == 'InvalidMoveNumber'
        else:
            return result == 'Success'
    }}
    @initializes {{
        if result == 'Success' and acceptDraw:
            initialize(game, 'outcome', 'Draw')
        if result == 'Success' and resign:
            initialize(game, 'outcome', 'BlackWins' if username == game.white else 'WhiteWins')
    }}

    MakeGame(whitePlayer, blackPlayer)
}
