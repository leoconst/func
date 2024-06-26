import pytest

from func.tokens import *


@pytest.mark.parametrize('source, expected', [
    (
        '',
        []
    ),
    (
        "\t repeat 3 '\\'Two plus three\\' equals:\\n\\t\\(add\t2 '3').'  \r\n\n= \t",
        [
            Token(TokenKind.IDENTIFIER, 'repeat'),
            Token(TokenKind.INTEGER, '3'),
            Token(TokenKind.STRING_DELIMITER),
            Token(TokenKind.STRING_CONTENT, '\'Two plus three\' equals:\n\t'),
            Token(TokenKind.STRING_EXPRESSION_ESCAPE_START),
            Token(TokenKind.IDENTIFIER, 'add'),
            Token(TokenKind.INTEGER, '2'),
            Token(TokenKind.STRING_DELIMITER),
            Token(TokenKind.STRING_CONTENT, '3'),
            Token(TokenKind.STRING_DELIMITER),
            Token(TokenKind.STRING_EXPRESSION_ESCAPE_END),
            Token(TokenKind.STRING_CONTENT, '.'),
            Token(TokenKind.STRING_DELIMITER),
            Token(TokenKind.NEWLINE),
            Token(TokenKind.NEWLINE),
            Token(TokenKind.EQUALS),
        ]
    ),
    (
        '\\a -> b\nλc -> d',
        [
            Token(TokenKind.LAMBDA),
            Token(TokenKind.IDENTIFIER, 'a'),
            Token(TokenKind.ARROW),
            Token(TokenKind.IDENTIFIER, 'b'),
            Token(TokenKind.NEWLINE),
            Token(TokenKind.LAMBDA),
            Token(TokenKind.IDENTIFIER, 'c'),
            Token(TokenKind.ARROW),
            Token(TokenKind.IDENTIFIER, 'd'),
        ]
    ),
    (
        "''",
        [
            Token(TokenKind.STRING_DELIMITER),
            Token(TokenKind.STRING_DELIMITER),
        ]
    ),
    (
        "'\\()'",
        [
            Token(TokenKind.STRING_DELIMITER),
            Token(TokenKind.STRING_EXPRESSION_ESCAPE_START),
            Token(TokenKind.STRING_EXPRESSION_ESCAPE_END),
            Token(TokenKind.STRING_DELIMITER),
        ]
    ),
    (
        "'hello\\()world'",
        [
            Token(TokenKind.STRING_DELIMITER),
            Token(TokenKind.STRING_CONTENT, 'hello'),
            Token(TokenKind.STRING_EXPRESSION_ESCAPE_START),
            Token(TokenKind.STRING_EXPRESSION_ESCAPE_END),
            Token(TokenKind.STRING_CONTENT, 'world'),
            Token(TokenKind.STRING_DELIMITER),
        ]
    ),
    (
        'if iffley then athens else welse',
        [
            Token(TokenKind.IF),
            Token(TokenKind.IDENTIFIER, 'iffley'),
            Token(TokenKind.THEN),
            Token(TokenKind.IDENTIFIER, 'athens'),
            Token(TokenKind.ELSE),
            Token(TokenKind.IDENTIFIER, 'welse'),
        ]
    ),
])
def test_success(source, expected):
    actual = list(tokenise(source))
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
    expected_error_message = \
        'Unexpected end-of-source inside expression escape'
    _expect_tokenise_error(source, expected_error_message)

@pytest.mark.parametrize('source', [
    "'\\",
    "'Hello, \\(greeting 'name\\",
])
def test_end_of_source_immediately_after_string_escape(source):
    expected_error_message = \
        'Unexpected end-of-source immediately after string escape'
    _expect_tokenise_error(source, expected_error_message)

def _expect_tokenise_error(source, expected_error_message):
    tokens = tokenise(source)
    with pytest.raises(TokeniseError, match=expected_error_message):
        _evaluate_iterable(tokens)

def _evaluate_iterable(iterable):
    for _ in iterable:
        pass
