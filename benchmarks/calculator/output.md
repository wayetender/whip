This test checks the nominal higher order nature of Deacon. It has 3 components: an adder service that adds numbers, a discovery service for adder services, and a client. In order to use the discovery service, you must create an account and login.

 * Deacon Spec: [calcthrift.spec](calcthrift.spec)
 * Deacon adapter configuration: [adapter.yaml](adapter.yaml)
 * Thrift IDL: [calc.thrift](calc.thrift)
 * Fault: [Line 18 of adder.py](adder.py#L18)

Programs run:

 * ``python discovery.py``                                     
 * ``../../bin/adapter adapter.yaml``
 * ``../../bin/shim python adder.py 127.0.0.1 8000 127.0.0.1 38000``
 * ``python client.py`` which runs the following commands:
  * ``signup lucas pass``
  * ``login lucas pass``
  * ``add 1 2``


Output of setup (before client is run) -- adder service signs up to the discovery service and registers its adder service:

```
    03/17/2015 01:28:33 PM INFO adder discovery service listening on 38000
    03/17/2015 01:28:37 PM proxy.py:295 accept_redirector_requests() -- DEBUG redirector accepting requests on port 9090
    03/17/2015 01:28:37 PM proxy.py:300 register_redirection_port() -- INFO Registering proxy endpoint ('127.0.0.1', 58132) for actual endpoint ('127.0.0.1', '8000')
    03/17/2015 01:28:37 PM proxy.py:300 register_redirection_port() -- INFO Registering proxy endpoint ('127.0.0.1', 58133) for actual endpoint ('127.0.0.1', '38000')
    03/17/2015 01:28:40 PM INFO adder service listening on 8000
    03/17/2015 01:28:40 PM proxy.py:277 get_redirection_info() -- DEBUG servicing redirection request for 127.0.0.1:38000
    03/17/2015 01:28:40 PM proxy.py:280 get_redirection_info() -- DEBUG redirection rule found: 127.0.0.1:38000 ==> 127.0.0.1:58133
    03/17/2015 01:28:40 PM proxy.py: 43        before_client() -- DEBUG before_client ('127.0.0.1', '38000') proxiedby ('127.0.0.1', '38001') :: signup(['adder-8000', 'password']) 
    03/17/2015 01:28:40 PM proxy.py: 53         after_server() -- DEBUG after_server ('127.0.0.1', '38000') proxiedby ('127.0.0.1', '38001') :: signup(['adder-8000', 'password']) -> True
    03/17/2015 01:28:40 PM contracts.py:234      process_updates() -- DEBUG initializing username to adder-8000 for Ghost Session<28b9d1> {'username': None}
    03/17/2015 01:28:40 PM DEBUG registering adder service 127.0.0.1:8000
    03/17/2015 01:28:40 PM INFO registered with adder discovery on 127.0.0.1:38000 as adder-8000
```

End of setup, start of client test -- client registers, logs in, gets a (buggy) adder service, and adds 1 and 2:

```
    03/17/2015 01:28:49 PM proxy.py:277 get_redirection_info() -- DEBUG servicing redirection request for 127.0.0.1:38000
    03/17/2015 01:28:49 PM proxy.py:280 get_redirection_info() -- DEBUG redirection rule found: 127.0.0.1:38000 ==> 127.0.0.1:58133
    03/17/2015 01:28:55 PM proxy.py: 43        before_client() -- DEBUG before_client ('127.0.0.1', '38000') proxiedby ('127.0.0.1', '38001') :: signup(['lucas', 'pass']) 
    03/17/2015 01:28:55 PM proxy.py: 53         after_server() -- DEBUG after_server ('127.0.0.1', '38000') proxiedby ('127.0.0.1', '38001') :: signup(['lucas', 'pass']) -> True
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

Note the last two lines, which show where the faulty "Adder" service came from: namely the ``register_adder`` command which was performed by session ``28b9d1``, whose ghost originated from ``login(adder-8000, password)``.
