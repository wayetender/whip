
service TwitterTweets {

    /1.1/statuses/mentions_timeline.json(request)
    @precondition {{ request['args'].get('count', 0) >= 0 }}
    @precondition {{ 'Authorization' in request['headers'] }}
    @postcondition {{ type(result['body']) == list }}

}



service User<UID> {
    /1.1/statuses/user_timeline(request)
    @where UID is {{ request.args.get('user_id', request.args.get('screen_name')) }}
    @precondition {{ 'Authorization' in request['headers'] }}
    @precondition {{ 'user_id' in request.args or 'screen_name' in request.args}}
    @identifies t:Tweet[] by {{
        for tweet in result:
            yield (request.host, tweet['id_str'])
    }}
    @postcondition {{ 
        'count' not in request.args or \
            len(result) <= max(200, request.args['count']) }}
    @postcondition {{
        for tweet in result: 
            assert rfc822.parsedate_tz(tweet['created_at']) != None
    }}

}

service Tweet<ID> {
    /1.1/statuses/retweet/<id>.json(request)
    @where ID is {{ id }}
    @postcondition {{ 'errors' not in result }}
}