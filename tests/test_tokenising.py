import pytest

from func.tokenising import *


def test_empty():
    assert list(tokenise('')) == []

def test_example():
    source = '''\
 \t repeat 3 '\\'Two plus three\\' equals:\\n\\t\\(add\t2 '3').'  \r\n\n= \t\
'''
    actual = list(tokenise(source))
    expected = [
        PlainToken(TokenKind.IDENTIFIER, 'repeat'),
        PlainToken(TokenKind.INTEGER, '3'),
        StringToken([
            '\'Two plus three\' equals:\n\t',
            [
                PlainToken(TokenKind.IDENTIFIER, 'add'),
                PlainToken(TokenKind.INTEGER, '2'),
                StringToken([
                    '3',
                ]),
            ],
            '.'
        ]),
        PlainToken(TokenKind.NEWLINE, '\r\n'),
        PlainToken(TokenKind.NEWLINE, '\n'),
        PlainToken(TokenKind.EQUALS, '='),
    ]
    assert actual == expected

@pytest.mark.parametrize('source', [
    "'Hello wo-",
    "'\\('Hi th-",
    "'\\('Greetings \\('name",
])
def test_end_of_source_in_string(source):
    expected_error_message = 'Unexpected end-of-source inside string'
    _expect_tokenise_error(source, expected_error_message)

@pytest.mark.parametrize('source', [
    "'\\(",
    "'Hello \\(name 'key:\\(time_to_",
])
def test_end_of_source_in_expression_escape(source):
    expected_error_message = 'Unexpected end-of-source inside expression escape'
    _expect_tokenise_error(source, expected_error_message)

def _expect_tokenise_error(source, expected_error_message):
    tokens = tokenise(source)
    with pytest.raises(TokeniseError, match=expected_error_message):
        _evaluate_iterable(tokens)

def _evaluate_iterable(iterable):
    for _ in iterable:
        pass
