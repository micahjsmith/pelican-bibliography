from pelican.plugins.bibliography.bibtex.lexer import lexer as _lexer
from pelican.plugins.bibliography.bibtex.models import BibtexEntry
from pelican.plugins.bibliography.bibtex.parser import parser as _parser

import pytest


@pytest.fixture(scope='function')
def lexer():
    yield _lexer


@pytest.fixture(scope='function')
def parser():
    yield _parser


def compare(lexer, expected):
    for tok, (type_, value) in zip(lexer, expected):
        assert tok.type == type_
        assert tok.value == value

    for tok in lexer:
        assert False, 'lexer has unexpected additional tokens'


def test_lexer_good(lexer):
    input = '''
    @article{key,
        foo = {bar},
        baz = {qux {quz}},
    }
    '''

    expected = [
        ('AT', '@'),
        ('ID', 'article'),
        ('ENTRYBEGIN', '{'),
        ('ID', 'key'),
        ('COMMA', ','),
        ('ID', 'foo'),
        ('EQUALS', '='),
        ('VALUE', '{bar}'),
        ('COMMA', ','),
        ('ID', 'baz'),
        ('EQUALS', '='),
        ('VALUE', '{qux {quz}}'),
        ('COMMA', ','),
        ('ENTRYEND', '}'),
    ]

    lexer.input(input)
    compare(lexer, expected)


def test_lexer_weird(lexer):
    input = '''
    @article{key, 5, key={{{value}}}, , ,}
    '''

    expected = [
        ('AT', '@'),
        ('ID', 'article'),
        ('ENTRYBEGIN', '{'),
        ('ID', 'key'),
        ('COMMA', ','),
        ('NUMBER', 5),
        ('COMMA', ','),
        ('ID', 'key'),
        ('EQUALS', '='),
        ('VALUE', '{{{value}}}'),
        ('COMMA', ','),
        ('COMMA', ','),
        ('COMMA', ','),
        ('ENTRYEND', '}'),
    ]

    lexer.input(input)
    compare(lexer, expected)


def test_parser_multiple(parser):
    input = '''
    @article{myarticle, field1={value1}}

    @book{mybook, field1={value1}, field2=5}
    '''
    expected = [
        BibtexEntry(
            type='article',
            key='myarticle',
            fields={'field1': '{value1}'},
        ),
        BibtexEntry(
            type='book',
            key='mybook',
            fields={'field1': '{value1}', 'field2': 5},
        ),
    ]
    result = parser.parse(input)

    for entry, expected_entry in zip(result, expected):
        assert entry == expected_entry
