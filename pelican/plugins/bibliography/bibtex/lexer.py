"""
Lexer for a subset of Bibtex.

TODO:
- delimit entries with parentheses
- other tokens outside of entry mode
- double quote mark delimited values
"""

import ply.lex as lex


tokens = (
    'AT',
    'COMMA',
    'EQUALS',
    'ID',
    'ENTRYBEGIN',
    'ENTRYEND',
    'NUMBER',
    'VALUE',
)

states = (
    ('entry', 'inclusive'),
    ('value', 'exclusive'),
)


t_AT = r'@'


def t_entry_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_ID(t):
    r'\w+'
    t.value = str(t.value).lower()
    return t


def t_entry(t):
    r'\{'
    t.lexer.begin('entry')

    t.type = 'ENTRYBEGIN'
    return t


def t_entry_RBRACE(t):
    r'\}'

    # t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-1]
    t.type = 'ENTRYEND'
    t.lexer.begin('INITIAL')
    return t


t_entry_COMMA = r','
t_entry_EQUALS = r'='


def t_entry_value(t):
    r'\{'
    t.lexer.code_start = t.lexer.lexpos
    t.lexer.level = 1
    t.lexer.push_state('value')


def t_value_LBRACE(t):
    r'\{'
    t.lexer.level += 1


def t_value_RBRACE(t):
    r'\}'
    t.lexer.level -= 1

    if t.lexer.level == 0:
        t.value = t.lexer.lexdata[t.lexer.code_start-1:t.lexer.lexpos]  # include delimiters
        t.type = 'VALUE'
        t.lexer.lineno += t.value.count('\n')
        t.lexer.pop_state()
        return t


def t_value_OTHER(t):
    r'[^\{\}]+'
    pass


def t_newline(t):
     r'\n+'
     t.lexer.lineno += len(t.value)


def t_error(t):
     print("Illegal character '%s'" % t.value[0])
     t.lexer.skip(1)


t_ignore = ' \t'


lexer = lex.lex()
