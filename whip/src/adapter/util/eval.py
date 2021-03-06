import textwrap
import rfc822
import chess
import chess.pgn
from StringIO import StringIO

class Console(object):
    def log(self, text):
        print "[CONTRACT LOG] %s" % text

class AssertionFailure:
    pass

class Unknown(Exception):
    def __init__(self):
        self.isUnknown = True

    def __getattr__(self, nm):
        return Unknown()

    def __call__(self, v):
        return Unknown()

    def __cmp__(self, other):
        raise self
    def __bool__(self):
        raise self
    def __nonzero__(self):
        raise self
    def __add__(self, other):
        raise self
    def __sub__(self, other):
        raise self
    def __mul__(self, other):
        raise self

    def __len__(self):
        raise self

def rewrite_for_unknown_ops(c):
    return c

def is_unknown(g):
    return isinstance(g, Unknown)


def unwrap(v):
    if isinstance(v, dict) and len(v.items()) == 1 and isinstance(v.values()[0], list):
        return v.values()[0]
    return v

def split(r, s):
    if is_unknown(s):
        return s
    import re
    return re.split(r, s)

def is_fresh(ghost):
        return ghost.fresh

def eval_code(env, py):
    try:
        for k, v in env.items():
           # print "%s = %s" % (k, v)
            env[k] = unwrap(v)

        env['isUnknown'] = is_unknown
        env['split'] = split
        env['isFresh'] = is_fresh
        env['rfc822_parsedate_tz'] = rfc822.parsedate_tz
        env['chess_pgn_read_game'] = chess.pgn.read_game
        env['StringIO'] = StringIO

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
    except Unknown, u:
        return u
