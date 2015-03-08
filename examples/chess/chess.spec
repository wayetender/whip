

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
    @mutable drawOffered,
    @mutable moves,

}

service Chess {
    @identifies games:Game[] by {{
        for (var i in result) {
            yield (result[i].gameId);
        }
    }}
    @initializes {{
        for (var i in result) {
            var gameInfo = result[i];
            var gameGhost = games[gameInfo.id];
            initialize(gameGhost, 'outcome', gameInfo.result);
            initialize(gameGhost, 'drawOffered', gameInfo.drawOffered);
            initialize(gameGhost, 'moves', gameInfo.moves.split(' '));
        }
    }}
    GetMyGames(username, password)
    
    @identifies game:Game by {{ gameId }}
    @precondition {{ game.outcome != 'Ongoing' || game.outcome == '' }}
    @precondition {{ isValidPGNString(myMove) }}
    @precondition {{ !acceptDraw || game.drawOffered }}
    @precondition {{ movecount == moves.length }}
    @updates {{
        if (result == 'Success') {
            if (acceptDraw) update(game, 'outcome', 'Draw');
        }
    }}
    MakeAMove(username, password, gameId, resign, acceptDraw, movecount, myMove, offerDraw, claimDraw, myMessage)
}