import uuid

def fresh_origin_hash():
    return uuid.uuid4().int


def fresh_client_name():
    'proxy-%s' % str(uuid.uuid4())


def assert_keys(d, keys):
    for key in keys:
        if key not in d.keys():
            raise ValueError('Config key %s not in %s' % (key, d))

