
service TwitterTweets {

    /1.1/statuses/mentions_timeline.json(request)
    @precondition {{ request['args'].get('count', 0) >= 0 }}
    @precondition {{ 'Authorization' in request['headers'] }}
    @postcondition {{ type(result['body']) == list }}

}

