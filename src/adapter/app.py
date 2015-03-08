import sys
from util.names import fresh_client_name
from util.config import get_config
from util.config import parse_proxy_list
from proxy import LocalRedirector
import logging

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)3d %(funcName)20s() -- %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.WARN)

    if len(sys.argv) != 2:
        print "usage: ./proxy [proxyconfigfile.yaml]"
        sys.exit(1)

    config = get_config(sys.argv[1])
    config['proxy_name'] = config.get('proxy_name', fresh_client_name())
    config['redirector_port'] = config.get('redirector_port', 10123)

    # set up port redirector
    redirector = LocalRedirector(config['redirector_port'])

    # app-specific setup: contracts
    from contracts import ContractsProxyApplication
    app = ContractsProxyApplication(config, redirector)

    proxies = parse_proxy_list(config.get('server_proxies', []), 'server')
    proxies += parse_proxy_list(config.get('client_proxies', []), 'client')

    for proxy_config in proxies:
        app.register_proxy(proxy_config)

    print "started up"

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print ""
