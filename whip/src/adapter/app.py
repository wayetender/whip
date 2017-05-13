import sys
from util.names import fresh_client_name
from util.config import get_config
from util.config import parse_proxy_list
from util.config import parse_interpreter
from proxy import LocalRedirector
import logging
import pickle
import base64
import os
import time

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)3d %(funcName)20s() -- %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    if len(sys.argv) != 2:
        print "usage: adapter [adapterconfigfile.yaml]"
        sys.exit(1)

    config = get_config(sys.argv[1])
    config['proxy_name'] = config.get('name', fresh_client_name())
    config['redirector_port'] = config.get('redirector_port', 10123)

    # set up port redirector
    redirector = LocalRedirector(config['redirector_port'])

    # app-specific setup: contracts
    import contracts
    app = contracts.ContractsProxyApplication(config, redirector)

    for (nm, interpreter) in config.get('interpreters', {}).items():
        i = parse_interpreter(interpreter)
        app.register_interpreter(nm, i)

    for proxy_config in parse_proxy_list(config.get('server_proxies', []), 'server'):
        app.register_proxy(proxy_config, config['proxy_name'])

    for proxy_config in parse_proxy_list(config.get('client_proxies', []), 'client'):
        app.register_proxy(proxy_config, 'unknown')


    REDIRECTOR_BYTESIZE = 59
    try:
        while True:
            if os.getenv('SHOW_DIAGS_INTERACTIVE', False):
                line = raw_input()
                if line == '':
                    continue
                elif line == 'traffic':
                    print >> sys.stderr, base64.b64encode(pickle.dumps(app.bytesperop))
                elif line == 'ghosts':
                    print >> sys.stderr, base64.b64encode(pickle.dumps(app.ghostsperop))
                elif line == 'timing':
                    print >> sys.stderr, base64.b64encode(pickle.dumps(app.timeperop))
                elif line == 'contracts':
                    print >> sys.stderr, base64.b64encode(pickle.dumps(contracts.timings))
                elif line == 'redirector':
                    print >> sys.stderr, base64.b64encode(pickle.dumps(redirector.requests * REDIRECTOR_BYTESIZE))
                else:
                    continue
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        print ""
