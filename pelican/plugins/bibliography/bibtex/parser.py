"""
Defines a parser for the approximate BibTeX grammar:

    entries : entry entries
            | empty
    entry   : AT ID ENTRYBEGIN ID COMMA terms ENTRYEND
    terms   : term
            | term COMMA terms
            | empty
    empty   :
    term    : key EQUALS value
    key     : ID
    value   : VALUE
            | NUMBER
            | ID

TODO:
- substitute strings
- skip comments
"""

from pelican.plugins.bibliography.bibtex.lexer import tokens
from pelican.plugins.bibliography.bibtex.models import BibtexEntry

import ply.yacc as yacc


def p_entries(p):
    """entries : entry entries"""
    p[0] = [p[1], *p[2]]


def p_entries_empty(p):
    """entries : empty"""
    p[0] = p[1]


def p_entry(p):
    """entry : AT ID ENTRYBEGIN ID COMMA terms ENTRYEND"""
    p[0] = BibtexEntry(
        type=p[2],
        key=p[4],
        fields=dict(p[6]),
    )

def p_terms_term(p):
    """terms : term"""
    p[0] = [p[1]]

def p_terms_terms(p):
    """terms : term COMMA terms"""
    p[0] = [p[1], *p[3]]

def p_terms_empty(p):
    """terms : empty"""
    p[0] = p[1]

def p_empty(p):
    """empty :"""
    p[0] = []

def p_term(p):
    """term : key EQUALS value"""
    p[0] = (p[1], p[3])

def p_key(p):
    """key : ID"""
    p[0] = p[1]

def p_value(p):
    """value : VALUE
             | NUMBER
             | ID
    """
    p[0] = p[1]


parser = yacc.yacc()
