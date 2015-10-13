import yaml
import parser
from names import assert_keys

def get_config(name):
    with open(name) as f:
        return yaml.load(f.read())


def parse_proxy(item, t):
    parsed = parser.parse(item)
    if parsed[0] != 'proxy':
        raise ValueError("parse error %s " % parsed)
    config = parsed[1]
    assert_keys(config, ['actual', 'mapsto'])
    config['type'] = t
    return config

def parse_interpreter(item):
    parsed = parser.parse(item)
    if parsed[0] != 'interpreter':
        raise ValueError("parse error %s " % parsed)
    config = parsed[1][1]
    return config


def parse_proxy_list(lst, t):
    proxies = []
    for item in lst:
        proxies.append(parse_proxy(item, t))
    return proxies


def parse_spec(str):
    return []
