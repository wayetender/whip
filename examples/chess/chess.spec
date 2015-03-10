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
    @identifies games:Game[] by {{ for game in result: yield (game['id']) }}
    @initializes {{
        for game in result:
            gameGhost = games[game['id']]
            if game['result'] != 'Ongoing':
                initialize(gameGhost, 'outcome', game['result']);
    }}
    @updates {{
        for game in result:
            gameGhost = games[game['id']]
            update(gameGhost, 'drawOffered', game['drawOffered'])
            update(gameGhost, 'moves', game['moves'])  
    }}
    
    MakeAMove(username, password, gameId, resign, acceptDraw, movecount, myMove, offerDraw, claimDraw, myMessage)
    @identifies game:Game by {{ gameId }}
    @precondition {{ isUnknown(game.outcome) }}
    @precondition {{ not acceptDraw or game.drawOffered }}
    @precondition {{ acceptDraw or resign or movecount == len(split('[0-9]+\. ', game.moves)) }}
    @initializes {{
        if result == 'Success' and acceptDraw:
            initialize(game, 'outcome', 'Draw')
    }}
}
