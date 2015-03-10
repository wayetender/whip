class GhostDecl(object):
    def __init__(self, name, fields, requires):
        self.name = name
        self.fields = fields
        self.requires = requires
    def __repr__(self):
        return "ghost %s %s requires {{ %s }}\n" % (self.name, self.fields, self.requires)

class ServiceContractDecl(object):
    def __init__(self, name, rpcs):
        self.name = name
        self.rpcs = rpcs

    def __repr__(self):
        return "service %s { \n\t%s\n }" % (self.name, "\n\n\t".join([str(rpc) for rpc in self.rpcs.values()]))

class Procedure(object):
    def __init__(self, name, formals, tags):
        self.name = name
        self.formals = formals
        self.tags = tags

    def __repr__(self):
        buf = '%s(%s)' % (self.name, ', '.join([str(f) for f in self.formals]))
        return "%s\n%s" % (''.join([str(t) + '\n\t' for t in self.tags]), buf)

class JSTag(object):
    def __init__(self, tag_type, js):
        self.tag_type = tag_type
        self.js = js

    def __repr__(self):
        return "@%s %s" % (self.tag_type, self.js)


class IdentifiesTag(object):
    def __init__(self, type, name, expr, ifcheck, multiple):
        self.type = type
        self.name = name
        self.expr = expr
        self.ifcheck = ifcheck
        self.multiple = multiple

    def __repr__(self):
        return "@identifies %s%s as %s by %s" % (self.type, "[]" if self.multiple else '', self.name, self.expr)

class UpdatesTag(object):
    def __init__(self, name, field, val, ifexpr = None):
        self.name = name
        self.field = field
        self.val = val
        self.ifexpr = ifexpr

    def __repr__(self):
        return "@updates %s.%s to %s" % (self.name, self.field, self.val)


class InitializesTag(object):
    def __init__(self, name, field, val, ifexpr = None):
        self.name = name
        self.field = field
        self.val = val
        self.ifexpr = ifexpr

    def __repr__(self):
        return "@initializes %s.%s to %s" % (self.name, self.field, self.val)


class GenericUpdatesTag(object):
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "@updates %s" % (self.val)

class GenericInitializesTag(object):
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "@initializes %s" % (self.val)

class InvariantTag(object):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def __repr__(self):
        return "@invariant for %s is %s" % (self.name, self.expr)


states = (
    ('comment', 'exclusive'),
    ('singlelinecomment', 'exclusive'),
    ('javascript', 'exclusive'),
    )

reserved = {
   'service' : 'SERVICE',
   'ghost' : 'GHOST',
   'mapstoservice' : 'MAPSTO',
   'proxiedby' : 'PROXIEDBY',
   'using' : 'USING',
   'for' : 'FOR',
   'to' : 'TO',
   'if' : 'IF',
   'by' : 'BY',
   'requires' : 'REQUIRES',
}

tokens = [
    'PRECONDITION_ONLY', 'PRECONDITION_FULL', 'POSTCONDITION_ONLY', 'POSTCONDITION_FULL', 'IDENTIFIES', 'UPDATES', 'INVARIANT', 'IMMUTABLE', 'IDENTIFIERTAG', 'INITIALIZES', # tags
    'COMMA', 'DOT', 'EQUALS', 'COLON',   # punctuation
    'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'LSQUARE', 'RSQUARE',   # brackets
    'STRING', 'BOOLEAN', 'INTEGER', 'DECIMAL', 'IP',  # literals
    'JAVASCRIPT', 'IDENTIFIER',
    ] + list(reserved.values())

# Syntax
#t_SEMI          = r';'
#t_ARROW         = r'->'
t_COMMA         = r','
t_DOT           = r'\.'
t_EQUALS        = r'='
t_LBRACE        = r'\{'
t_RBRACE        = r'\}'
t_LSQUARE       = r'\['
t_RSQUARE       = r'\]'
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
t_COLON         = r':'

# Literals
t_IP            = r'[0-9][0-9]?[0-9]?\.[0-9][0-9]?[0-9]?\.[0-9][0-9]?[0-9]?\.[0-9][0-9]?[0-9]?'
t_INTEGER       = r'-?[1-9][0-9]*'
t_DECIMAL       = t_INTEGER + r'\.[0-9]*'

# Tags
t_PRECONDITION_ONLY = r'@precondition'
t_POSTCONDITION_ONLY = r'@postcondition'
t_IDENTIFIES = r'@identifies'
t_UPDATES = r'@updates'
t_INVARIANT = r'@invariant'
t_IMMUTABLE = r'@immutable'
t_IDENTIFIERTAG = r'@identifier'
t_INITIALIZES = r'@initializes'

t_ignore = " \t"

def t_TAG_FULL(t):
    r'@(preconditionXXX|postconditionXXX) +[^{][^\n][^\n][^\n]+'
    if t.value.startswith('@precondition'):
        t.type = 'PRECONDITION_FULL'
        t.value = t.value[14:]
    if t.value.startswith('@postcondition'):
        t.type = 'POSTCONDITION_FULL'
        t.value = t.value[15:]
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    if t.value == 'true' or t.value == 'false':
        t.type = 'BOOLEAN'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_STRING(t):
    '(?:"(?:[^"\\n\\r\\\\]|(?:"")|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*")|(?:\'(?:[^\'\\n\\r\\\\]|(?:\'\')|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*\')'
    t.value = t.value[1:-1].decode("string-escape")
    t.type = 'STRING'
    return t

def t_begin_comment(t):
    r'\/\*'
    t.lexer.begin('comment')

def t_comment_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_comment_error(t):
    t.lexer.skip(1)

t_comment_ignore = r''

def t_comment_end(t):
    r'\*\/'
    t.lexer.begin('INITIAL')


def t_begin_singlelinecomment(t):
    r'\#|\/\/'
    t.lexer.begin('singlelinecomment')

t_singlelinecomment_ignore = r''

def t_singlelinecomment_error(t):
    t.lexer.skip(1)

def t_singlelinecomment_end(t):
    r'\n'
    t.lexer.begin('INITIAL')

def t_begin_javascript(t):
    r'\{\{'
    t.lexer.code_start = t.lexer.lexpos
    t.lexer.level = 1  
    t.lexer.begin('javascript')

def t_javascript_lbrace(t):     
    r'\{\{'
    t.lexer.level +=1                

t_javascript_ignore = r''

def t_javascript_error(t):
    t.lexer.skip(1)

def t_javascript_rbrace(t):
    r'\}\}'
    t.lexer.level -=1

    if t.lexer.level == 0:
         t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-2]
         t.type = "JAVASCRIPT"
         t.lexer.lineno += t.value.count('\n')
         t.lexer.begin('INITIAL')
         return t


# Build the lexer
import ply.lex as lex
lex.lex()

from ast import *

def p_goal(p):
    '''goal : idl 
        | proxystring'''
    p[0] = p[1]

def p_idl_entry(p):
    '''idl : service idl
        | ghost idl'''
    p[0] = [p[1]] + p[2]

def p_idl_empty(p):
    'idl : '
    p[0] = []

def p_service(p):
    'service : SERVICE IDENTIFIER LBRACE procedures RBRACE'
    p[0] = ServiceContractDecl(p[2], p[4])

def p_params_empty(p):
    'params : '
    p[0] = dict()

def p_params_lst(p):
    'params : param COMMA params'
    p[0] = dict(p[1].items() + p[3].items())

def p_params_singleton(p):
    'params : param'
    p[0] = p[1]

def p_param_js(p):
    'param : fieldtags IDENTIFIER EQUALS JAVASCRIPT'
    p[0] = {p[2] : (p[1], p[4])}

def p_param_nonjs(p):
    'param : fieldtags IDENTIFIER EQUALS literal'
    p[0] = {p[2] : p[4]}

def p_param_noval(p):
    'param : fieldtags IDENTIFIER'
    p[0] = {p[2] : (p[1], None)}

def p_literal(p):
    '''literal : STRING
        | IP
        | DECIMAL
        | BOOLEAN'''
    p[0] = p[1]


def p_fieldtags_empty(p):
    'fieldtags : '
    p[0] = 'mutable'

def p_fieldtags_identifier(p):
    'fieldtags : IDENTIFIERTAG'
    p[0] = 'identifier'

def p_fieldtags_immutble(p):
    'fieldtags : IMMUTABLE'
    p[0] = 'immutable'

def p_procedures_empty(p):
    'procedures : '
    p[0] = {}

def p_procedures_lst(p):
    'procedures : IDENTIFIER LPAREN formals RPAREN tags procedures'
    p[0] = dict([(p[1], Procedure(p[1], p[3], p[5]))] + p[6].items())

def p_formals_empty(p):
    'formals : '
    p[0] = []

def p_formals_lst(p):
    'formals : IDENTIFIER COMMA formals'
    p[0] = [p[1]] + p[3]

def p_formals_singleton(p):
    'formals : IDENTIFIER'
    p[0] = [p[1]]


def p_tags_one(p):
    'tags : tag tags'
    p[0] = [p[1]] + p[2]

def p_tags_empty(p):
    'tags : '
    p[0] = []

def p_precondition_single(p):
    'tag : PRECONDITION_FULL'
    p[0] = JSTag('precondition', p[1])

def p_precondition_multi(p):
    'tag : PRECONDITION_ONLY JAVASCRIPT'
    p[0] = JSTag('precondition', p[2])

def p_postcondition_multi(p):
    'tag : POSTCONDITION_ONLY JAVASCRIPT'
    p[0] = JSTag('postcondition', p[2])

def p_postcondition_single(p):
    'tag : POSTCONDITION_FULL'
    p[0] = JSTag('postcondition', p[1])

def p_tags_token(p):
    'tag : IDENTIFIES IDENTIFIER COLON IDENTIFIER BY JAVASCRIPT'
    p[0] = IdentifiesTag(p[4], p[2], p[6], '', False)

def p_tags_multiple(p):
    'tag : IDENTIFIES IDENTIFIER COLON IDENTIFIER LSQUARE RSQUARE BY JAVASCRIPT'
    p[0] = IdentifiesTag(p[4], p[2], p[8], '', True)

def p_tags_token_if(p):
    'tag : IDENTIFIES IDENTIFIER COLON IDENTIFIER BY JAVASCRIPT IF JAVASCRIPT'
    p[0] = IdentifiesTag(p[4], p[2], p[6], p[8], False)

def p_tags_updates(p):
    'tag : UPDATES IDENTIFIER DOT IDENTIFIER TO JAVASCRIPT'
    p[0] = UpdatesTag(p[2], p[4], p[6])

def p_tags_updates_if(p):
    'tag : UPDATES IDENTIFIER DOT IDENTIFIER TO JAVASCRIPT IF JAVASCRIPT'
    p[0] = UpdatesTag(p[2], p[4], p[6], p[8])

def p_tags_updates_generic(p):
    'tag : UPDATES JAVASCRIPT'
    p[0] = GenericUpdatesTag(p[2])

def p_tags_init(p):
    'tag : INITIALIZES IDENTIFIER DOT IDENTIFIER TO JAVASCRIPT'
    p[0] = InitializesTag(p[2], p[4], p[6])

def p_tags_init_if(p):
    'tag : INITIALIZES IDENTIFIER DOT IDENTIFIER TO JAVASCRIPT IF JAVASCRIPT'
    p[0] = InitializesTag(p[2], p[4], p[6], p[8])

def p_tags_initializes_generic(p):
    'tag : INITIALIZES JAVASCRIPT'
    p[0] = GenericInitializesTag(p[2])

def p_tags_invariant(p):
    'tag : INVARIANT FOR IDENTIFIER JAVASCRIPT'
    p[0] = InvariantTag(p[3], p[4])


def p_ghost_no_requires(p):
    'ghost : GHOST IDENTIFIER LBRACE params RBRACE'
    p[0] = GhostDecl(p[2], p[4], '')

def p_ghost_requires(p):
    'ghost : GHOST IDENTIFIER LBRACE params RBRACE REQUIRES JAVASCRIPT'
    p[0] = GhostDecl(p[2], p[4], p[7])


def p_proxystring(p):
    'proxystring : IP COLON INTEGER proxyargs'
    p[0] = ('proxy', dict([('actual', (p[1], p[3]))] + p[4]))

def p_proxyargs_using(p):
    'proxyargs : proxyargs USING IDENTIFIER LPAREN params RPAREN'
    p[0] = p[1] + [('using', (p[3], p[5]))]

def p_proxyargs_mapsto(p):
    'proxyargs : proxyargs MAPSTO IDENTIFIER'
    p[0] = p[1] + [('mapsto', p[3])]

def p_proxyargs_proxiedby(p):
    'proxyargs : proxyargs PROXIEDBY IP COLON INTEGER'
    p[0] = p[1] + [('proxiedby', (p[3], p[5]))]

def p_proxyargs_empty(p):
    'proxyargs : '
    p[0] = []

def p_error(t):
    print("Syntax error at '%s'" % t.__dict__)
    import sys
    sys.exit(1)

import ply.yacc as yacc
yacc.yacc()


def print_tokens(s):
    lex.input(s)
    while True:
        tok = lex.token()
        if not tok: break      # No more input
        print tok

def parse(s):
    return yacc.parse(s)

def parse_file(f, do_print=False):
    with open(f, 'r') as content_file:
        s = content_file.read()
        if do_print:
            print print_tokens(s)
        return parse(s)

## --------------TESTING STUFF BELOW THIS LINE -------------- ##

# data = '''
# service Multiplier {
#     int square(int n)
#         requires {{ true; }}
#         guarantees {{ n * n == result }};

#     int increment(int n)
#         requires {{ n < 2147483646; /* max value - 1 */ }}
#         guarantees {{ n + 1 == result; }};
# }

# service Composer {
#     /* returns a service call fun(n) -> f(g(n)) */
#     [int -> int] compose_int([int -> int] f, [int -> int] g);
# }
# '''

# # Give the lexer some input
# lex.input(data)

# # Tokenize
# while True:
#     tok = lex.token()
#     if not tok: break      # No more input
#     print tok

# # or just parse it:
# print yacc.parse(data)

