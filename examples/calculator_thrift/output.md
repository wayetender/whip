Jobs:

    * ``python discovery.py``                                     
    * ``../../bin/adapter adapter.yaml``
    * ``../../bin/shim python adder.py 127.0.0.1 8000 127.0.0.1 38000``
    * ``python client.py``
    ** ``signup lucas pass``
    ** ``login lucas pass``
    ** ``add 1 2``


Output:

```
    03/17/2015 01:28:33 PM INFO adder discovery service listening on 38000
    03/17/2015 01:28:37 PM proxy.py:295 accept_redirector_requests() -- DEBUG redirector accepting requests on port 9090
    03/17/2015 01:28:37 PM thrift.py: 32             __init__() -- DEBUG generating thrift stubs in /var/folders/vc/xxlhr8616sz6570gn72jnww80000gn/T/tmpZhzyzD for IDL /Users/lucas/deacon/examples/calculator_thrift/calc.thrift
    03/17/2015 01:28:37 PM thrift.py: 32             __init__() -- DEBUG generating thrift stubs in /var/folders/vc/xxlhr8616sz6570gn72jnww80000gn/T/tmpCLLT0o for IDL /Users/lucas/deacon/examples/calculator_thrift/calc.thrift
    03/17/2015 01:28:37 PM proxy.py:300 register_redirection_port() -- INFO Registering proxy endpoint ('127.0.0.1', 58132) for actual endpoint ('127.0.0.1', '8000')
    03/17/2015 01:28:37 PM proxy.py:300 register_redirection_port() -- INFO Registering proxy endpoint ('127.0.0.1', 58133) for actual endpoint ('127.0.0.1', '38000')
    03/17/2015 01:28:40 PM INFO adder service listening on 8000
    03/17/2015 01:28:40 PM proxy.py:277 get_redirection_info() -- DEBUG servicing redirection request for 127.0.0.1:38000
    03/17/2015 01:28:40 PM proxy.py:280 get_redirection_info() -- DEBUG redirection rule found: 127.0.0.1:38000 ==> 127.0.0.1:58133
    03/17/2015 01:28:40 PM contracts.py:330        before_client() -- DEBUG unknown op: signup
    03/17/2015 01:28:40 PM proxy.py: 43        before_client() -- DEBUG before_client ('127.0.0.1', '38000') proxiedby ('127.0.0.1', '38001') :: signup(['adder-8000', 'password']) 
    03/17/2015 01:28:40 PM contracts.py:337        before_server() -- DEBUG unknown rpc signup
    03/17/2015 01:28:40 PM contracts.py:373         after_server() -- DEBUG unknown op: signup
    03/17/2015 01:28:40 PM proxy.py: 53         after_server() -- DEBUG after_server ('127.0.0.1', '38000') proxiedby ('127.0.0.1', '38001') :: signup(['adder-8000', 'password']) -> True
    03/17/2015 01:28:40 PM contracts.py:381         after_client() -- DEBUG unknown rpc signup
    03/17/2015 01:28:40 PM contracts.py:234      process_updates() -- DEBUG initializing username to adder-8000 for Ghost Session<28b9d1> {'username': None}
    03/17/2015 01:28:40 PM DEBUG registering adder service 127.0.0.1:8000
    03/17/2015 01:28:40 PM INFO registered with adder discovery on 127.0.0.1:38000 as adder-8000
```

End of setup, start of client test:

```
    03/17/2015 01:28:49 PM proxy.py:277 get_redirection_info() -- DEBUG servicing redirection request for 127.0.0.1:38000
    03/17/2015 01:28:49 PM proxy.py:280 get_redirection_info() -- DEBUG redirection rule found: 127.0.0.1:38000 ==> 127.0.0.1:58133
    03/17/2015 01:28:55 PM contracts.py:330        before_client() -- DEBUG unknown op: signup
    03/17/2015 01:28:55 PM proxy.py: 43        before_client() -- DEBUG before_client ('127.0.0.1', '38000') proxiedby ('127.0.0.1', '38001') :: signup(['lucas', 'pass']) 
    03/17/2015 01:28:55 PM contracts.py:337        before_server() -- DEBUG unknown rpc signup
    03/17/2015 01:28:55 PM contracts.py:373         after_server() -- DEBUG unknown op: signup
    03/17/2015 01:28:55 PM proxy.py: 53         after_server() -- DEBUG after_server ('127.0.0.1', '38000') proxiedby ('127.0.0.1', '38001') :: signup(['lucas', 'pass']) -> True
    03/17/2015 01:28:55 PM contracts.py:381         after_client() -- DEBUG unknown rpc signup
    03/17/2015 01:28:58 PM contracts.py:234      process_updates() -- DEBUG initializing username to lucas for Ghost Session<95aa32> {'username': None}
    03/17/2015 01:29:03 PM DEBUG returning random service to lucas
    03/17/2015 01:29:03 PM proxy.py:277 get_redirection_info() -- DEBUG servicing redirection request for 127.0.0.1:8000
    03/17/2015 01:29:03 PM proxy.py:280 get_redirection_info() -- DEBUG redirection rule found: 127.0.0.1:8000 ==> 127.0.0.1:58132
    03/17/2015 01:29:03 PM contracts.py:111         report_error() -- WARNING contract failure
    Failed postcondition  result == a + b  Variables: 
      - a = 1
      - b = 2
      - thisServiceOrigin = ['AdderDiscovery 127.0.0.1:38000 :: register_adder(28b9d1, 127.0.0.1, 8000)']
      - split = <function split at 0x1051286e0>
      - isUnknown = <function is_unknown at 0x1051285f0>
      - result = 2

     ^----> referenced: ['AdderDiscovery 127.0.0.1:38000 :: register_adder(28b9d1, 127.0.0.1, 8000)']
     ^--------> referenced: ['AdderDiscovery 127.0.0.1:38000 :: login(adder-8000, password)']
```

