import textwrap

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
    if isinstance(v, dict) and len(v.items()) == 1 and isinstance(v.values()[0], list):
        return v.values()[0]
    return v


def eval_code(env, py):
    for k, v in env.items():
       # print "%s = %s" % (k, v)
        env[k] = unwrap(v)

    if 'yield' in env:
        env['_yield'] = env['yield']
        py = py.replace('yield', '_yield')
    py = textwrap.dedent(py).strip()
    try:
        return eval(py, env)
    except SyntaxError:
        py =  '\n'.join((4 * ' ') + x for x in py.splitlines())
        py = "def f():\n%s" % py
       # print py
        exec(py, env)
        return env['f']()
