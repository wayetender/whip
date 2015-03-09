import sys
sys.path.append('../')

from suds.client import Client
import logging
from nose.tools import with_setup
import server
import test_utils

logging.getLogger('suds').setLevel(logging.INFO)

setup_f = test_utils.setup_adapter('adapter.yaml', server.make_app())

@with_setup(setup_f, test_utils.teardown_adapter)
def test_login():
    url = 'http://localhost:8000/?wsdl'
    client = Client(url)
    client.options.cache.clear()
    sid = client.service.login('test', 3)
    assert 'error' not in sid
    assert len(test_utils.adapter.output) == 0

@with_setup(setup_f, test_utils.teardown_adapter)
def test_add():
    url = 'http://localhost:8000/?wsdl'
    client = Client(url)
    client.options.cache.clear()
    offset = 3
    sid = client.service.login('test', offset)
    assert 'error' not in sid
    res = client.service.add(sid, 1, 2)
    assert res == 1 + 2 + offset
    assert len(test_utils.adapter.output) == 0


