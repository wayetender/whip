import sys
sys.path.append('../')

from suds.client import Client
import logging
from nose.tools import with_setup
import server
import test_utils

logging.getLogger('suds').setLevel(logging.INFO)

setup_f = test_utils.setup_adapter('adapter.yaml', server.make_app())

def get_client():
    url = 'http://localhost:8000/?wsdl'
    client = Client(url)
    client.options.cache.clear()
    return client

@with_setup(setup_f, test_utils.teardown_adapter)
def test_login():
    client = get_client()
    sid = client.service.login('test', 3)
    assert 'error' not in sid
    assert len(test_utils.adapter.output) == 0

@with_setup(setup_f, test_utils.teardown_adapter)
def test_bad_login():
    client = get_client()
    sid = client.service.login('badlogin', 3)
    assert 'error' in sid

@with_setup(setup_f, test_utils.teardown_adapter)
def test_bad_offset():
    client = get_client()
    sid = client.service.login('test', -1)
    assert len(test_utils.adapter.output) > 1
    assert 'Failed precondition for RPC login ( offset >= 0 )' in str(test_utils.adapter.output)
    assert "['Calculator 127.0.0.1:8000 :: login(test, -1)']" in str(test_utils.adapter.output)

@with_setup(setup_f, test_utils.teardown_adapter)
def test_add():
    client = get_client()
    offset = 3
    sid = client.service.login('test', offset)
    assert 'error' not in sid
    res = client.service.add(sid, 1, 2)
    assert res == 1 + 2 + offset
    assert len(test_utils.adapter.output) == 0


