from pyv8 import PyV8
import datetime

class Console(PyV8.JSClass):
    def log(self, text):
        print "[JAVASCRIPT LOG] %s" % text


class Unknown(PyV8.JSClass):
    def __init__(self):
        self.isUnknown = True

    def __getattr__(self, nm):
        return Unknown()

    def __call__(self, v):
        return Unknown()


def is_unknown(g):
    return isinstance(g, Unknown)


def getFunctions():
    return '''
function isUnknown(ghost) {
    return (typeof ghost['isUnknown'] !== "undefined") && ghost['isUnknown'];
}
function _unknowncmpEQ(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a == b;
}
function _unknowncmpADD(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a + b;
}
function _unknowncmpSUB(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a - b;
}
function _unknowncmpGTE(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a >= b;
}
function _unknowncmpLTE(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a <= b;
}
function _unknowncmpGT(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a > b;
}
function _unknowncmpLT(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a < b;
}
function _unknowncmpAND(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a && b;
}
function _unknowncmpOR(a, b) {
    if (isUnknown(a))
        return a;
    else if (isUnknown(b))
        return b;
    else
        return a || b;
}


    '''

class Global(PyV8.JSClass):
    console = Console()

    def unknown(self):
        return Unknown()

    def isFresh(self, ghost):
        return ghost.fresh

    # def isUnknown(self, ghost):
    #     return hasattr(ghost, 'isUnknown') and ghost.isUnknown

    # def _unknowncmpEQ(self, a, b):
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     else:
    #         return a == b

    # def _unknowncmpADD(self, a, b):
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     else:
    #         if isinstance(a, str):
    #             return str(a) + str(b)
    #         return a + b

    # def _unknowncmpSUB(self, a, b):
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     else:
    #         if isinstance(a, str):
    #             return str(a) - str(b)
    #         return a - b


    # def _unknowncmpGTE(self, a, b):
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     else:
    #         return a >= b

    # def _unknowncmpLTE(self, a, b):
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     else:
    #         return a <= b

    # def _unknowncmpLT(self, a, b):
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     else:
    #         return a < b


    # def _unknowncmpGT(self, a, b):
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     else:
    #         return a > b

    # def _unknowncmpAND(self, a, b):
    #     if isinstance(a, bool) and not a:
    #         return False
    #     if isinstance(b, bool) and not b:
    #         return False
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     return a and b

    # def _unknowncmpOR(self, a, b):
    #     if isinstance(a, bool) and a:
    #         return True
    #     if isinstance(b, bool) and b:
    #         return True
    #     if self.isUnknown(a):
    #         return a
    #     if self.isUnknown(b):
    #         return b
    #     return a or b
        

def unwrap(v):
    if isinstance(v, list):
        v2 = []
        for item in v:
            v2.append(unwrap(item))
        return PyV8.JSArray(v2)
    elif isinstance(v, dict):
        v2 = {}
        for k,val in v.items():
            v2[k] = unwrap(val)
        return v2
    else:
        return v

lock = None
entered = 0

class AssertionFailure:
    pass

def eval_javascript(env, js):
    global lock, entered


    def assert_f(v):
        if not v:
            print "ASSERTION FAILED"
            raise AssertionFailure()
        return True

    def assert_strict(v):
        if hasattr(v, 'isUnknown') and v.isUnknown:
            print "STRICT ASSERTION IS UNKNOWN"
            raise AssertionFailure()
        else:
            return assert_f(v)

    if not lock:
        lock = PyV8.JSLocker()
        lock.enter()

    entered += 1

    with PyV8.JSContext(Global()) as ctxt:
        ctxt.locals['assert'] = assert_f
        ctxt.locals['assert_strict'] = assert_strict
        for k, v in env.items():
            ctxt.locals[k] = unwrap(v)
            #if k == 'flight':
            #    print ctxt.locals[k]
        pres =  PyV8.convert(ctxt.eval(js))
    

    entered -= 1
    if entered == 0:
        lock.leave()
        lock = None

    return pres


def js_lookup(val, name, lookup_str):
    with PyV8.JSLocker():
        with PyV8.JSContext(Global()) as ctxt:
            ctxt.locals[name] = val
            return ctxt.eval(lookup_str)



class Visitor(object):
    def __init__(self, e):
        self.e = e

    def onProgram(self, prog):
        self.ast = prog.toAST()

        self.finalstr = ''
        for decl in prog.scope.declarations:
            decl.visit(self)
            self.finalstr += self.str

        for stmt in prog.body:
            stmt.visit(self)
            self.finalstr += self.str

        #print str(prog)
        #self.json = json.loads(prog.toJSON())


    def __getattr__(self, name):
        if name.startswith('on'):
            def return_usual(e):
                #print "usual for %s" % name
                self.str = str(e)
            return return_usual

    def onFunctionDeclaration(self, f):
        f.function.visit(self)
        self.str = "%s; " % (self.str)

    def onForInStatement(self, f):
        f.body.visit(self)
        self.str = "if (isUnknown(%s)) { return unknown(); } else { for (var %s in %s) { %s } } " % (f.enumerable, f.each, f.enumerable, self.str)

    def onVariableDeclaration(self, d):
        self.str = "var %s;" % (d.proxy.name)

    def onAssignment(self, a):
        a.value.visit(self)
        v = self.str
        self.str = "%s = %s" % (a.target, v)

    def onIfStatement(self, i):
        i.condition.visit(self)
        check = self.str
        i.thenStatement.visit(self)
        then = self.str
        if i.hasElseStatement:
            i.elseStatement.visit(self)
            elsePart = self.str
        else:
            elsePart = ''
        self.str = "tmp = %s; if (isUnknown(tmp)) { return unknown(); } else { if (tmp) { %s } else { %s } }" % (check, then, elsePart)


    def onFunctionLiteral(self, f):
        body = []
        for b in f.body:
            b.visit(self)
            body.append(self.str)
        params = []
        for i in xrange(0, f.scope.num_parameters):
            params.append(str(f.scope.parameter(i).name))

        self.str = "function %s(%s) { %s }" % (f.name, ", ".join(params), " ".join(body))

    def onBlock(self, block):
        strs = []
        for stmt in block.statements:
            stmt.visit(self)
            strs.append(self.str)
        if strs == []:
            return ''
        self.str = "{ %s }" % " ".join(strs)

    def onCall(self, stmt):
        stmt.expression.visit(self)
        e = self.str
        args = []
        for arg in stmt.args:
            arg.visit(self)
            args.append(self.str)
        self.str = "%s(%s)" % (e, ", ".join(args))

    def onExpressionStatement(self, stmt):
        stmt.expression.visit(self)
        self.str = "%s; " % (self.str)

    def onReturnStatement(self, stmt):
        stmt.expression.visit(self);
        self.str = "return %s;" % (self.str)

    def onCompareOperation(self, stmt):
        stmt.left.visit(self)
        left = self.str
        stmt.right.visit(self)
        right = self.str

        self.str = "%s(%s, %s)" % ('_unknowncmp%s' % stmt.op, left, right)

    def onBinaryOperation(self, stmt):
        stmt.left.visit(self)
        left = self.str
        stmt.right.visit(self)
        right = self.str

        self.str = "%s(%s, %s)" % ('_unknowncmp%s' % stmt.op, left, right)


def rewrite_for_unknown_ops(js):
    start = datetime.datetime.now()
    with PyV8.JSLocker():
        with PyV8.JSContext() as c:
            with PyV8.JSEngine() as e:
                s = e.compile(js)
                visitor = Visitor(e)
                s.visit(visitor)
                stop = datetime.datetime.now()
                diff = (stop - start).total_seconds()
                print "rewrite time = %f" % (diff * 1000)
                return getFunctions() + visitor.finalstr

