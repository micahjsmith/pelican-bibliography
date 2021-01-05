from pelican.plugins.bibliography.bibtex.lexer import lexer as _lexer
import pytest


@pytest.fixture(scope='function')
def lexer():
    yield _lexer


def compare(lexer, expected):
    for tok, (type_, value) in zip(lexer, expected):
        assert tok.type == type_
        assert tok.value == value

    for tok in lexer:
        assert False, 'lexer has unexpected addditional tokens'


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
        ('VALUE', 'bar'),
        ('COMMA', ','),
        ('ID', 'baz'),
        ('EQUALS', '='),
        ('VALUE', 'qux {quz}'),
        ('COMMA', ','),
        ('ENTRYEND', '}'),
    ]

    lexer.input(input)
    compare(lexer, expected)


def test_lexer_weird(lexer):
    input = '''
    @article{key, key, key={{{value}}}, , ,}
    '''

    expected = [
        ('AT', '@'),
        ('ID', 'article'),
        ('ENTRYBEGIN', '{'),
        ('ID', 'key'),
        ('COMMA', ','),
        ('ID', 'key'),
        ('COMMA', ','),
        ('ID', 'key'),
        ('EQUALS', '='),
        ('VALUE', '{{value}}'),
        ('COMMA', ','),
        ('COMMA', ','),
        ('COMMA', ','),
        ('ENTRYEND', '}'),
    ]

    lexer.input(input)
    compare(lexer, expected)
