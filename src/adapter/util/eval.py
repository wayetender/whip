
class Console(object):
    def log(self, text):
        print "[JAVASCRIPT LOG] %s" % text

class AssertionFailure:
    pass

class Unknown(object):
    def __init__(self):
        self.isUnknown = True

    def __getattr__(self, nm):
        return Unknown()

    def __call__(self, v):
        return Unknown()

def rewrite_for_unknown_ops(c):
    return c

def is_unknown(g):
    return isinstance(g, Unknown)


def unwrap(v):
    return v


def eval_code(env, py):
    return eval(py, env)
