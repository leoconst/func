import pytest

from func.tokens import (
    ConstantToken,
    ConstantTokenKind,
    ValueToken,
    ValueTokenKind,
)
from func.tokeniser import *


@pytest.mark.parametrize('source, expected', [
    (
        '',
        []
    ),
    (
        ("\t repeat 3 '\\'Two plus three\\' equals:\\n\\t\\(add\t2 '3').'"
         "  \r\n\n= \t"),
        [
            ValueToken(ValueTokenKind.IDENTIFIER, 'repeat'),
            ValueToken(ValueTokenKind.INTEGER, '3'),
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
            ValueToken(
                ValueTokenKind.STRING_CONTENT,
                '\'Two plus three\' equals:\n\t'),
            ConstantToken(ConstantTokenKind.STRING_EXPRESSION_ESCAPE_START),
            ValueToken(ValueTokenKind.IDENTIFIER, 'add'),
            ValueToken(ValueTokenKind.INTEGER, '2'),
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
            ValueToken(ValueTokenKind.STRING_CONTENT, '3'),
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
            ConstantToken(ConstantTokenKind.STRING_EXPRESSION_ESCAPE_END),
            ValueToken(ValueTokenKind.STRING_CONTENT, '.'),
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
            ConstantToken(ConstantTokenKind.NEWLINE),
            ConstantToken(ConstantTokenKind.NEWLINE),
            ConstantToken(ConstantTokenKind.EQUALS),
        ]
    ),
    (
        '\\a -> b\nλc -> d',
        [
            ConstantToken(ConstantTokenKind.LAMBDA),
            ValueToken(ValueTokenKind.IDENTIFIER, 'a'),
            ConstantToken(ConstantTokenKind.ARROW),
            ValueToken(ValueTokenKind.IDENTIFIER, 'b'),
            ConstantToken(ConstantTokenKind.NEWLINE),
            ConstantToken(ConstantTokenKind.LAMBDA),
            ValueToken(ValueTokenKind.IDENTIFIER, 'c'),
            ConstantToken(ConstantTokenKind.ARROW),
            ValueToken(ValueTokenKind.IDENTIFIER, 'd'),
        ]
    ),
    (
        "''",
        [
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
        ]
    ),
    (
        "'\\()'",
        [
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
            ConstantToken(ConstantTokenKind.STRING_EXPRESSION_ESCAPE_START),
            ConstantToken(ConstantTokenKind.STRING_EXPRESSION_ESCAPE_END),
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
        ]
    ),
    (
        "'hello\\()world'",
        [
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
            ValueToken(ValueTokenKind.STRING_CONTENT, 'hello'),
            ConstantToken(ConstantTokenKind.STRING_EXPRESSION_ESCAPE_START),
            ConstantToken(ConstantTokenKind.STRING_EXPRESSION_ESCAPE_END),
            ValueToken(ValueTokenKind.STRING_CONTENT, 'world'),
            ConstantToken(ConstantTokenKind.STRING_DELIMITER),
        ]
    ),
    (
        'if iffley then athens else welse',
        [
            ConstantToken(ConstantTokenKind.IF),
            ValueToken(ValueTokenKind.IDENTIFIER, 'iffley'),
            ConstantToken(ConstantTokenKind.THEN),
            ValueToken(ValueTokenKind.IDENTIFIER, 'athens'),
            ConstantToken(ConstantTokenKind.ELSE),
            ValueToken(ValueTokenKind.IDENTIFIER, 'welse'),
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
