import pytest

from func.parsing import *
from func.tokenising import tokenise


@pytest.mark.parametrize('source, expected', [
    (
        '',
        ModuleSyntax([])
    ),
    (
        'hello = world',
        ModuleSyntax([
            BindingSyntax(
                'hello',
                IdentifierExpressionSyntax('world')
            )
        ])
    ),
    (
        "indentifier_calls = a b c\nstring_calls = 'a' 'b' 'c'",
        ModuleSyntax([
            BindingSyntax(
                'indentifier_calls',
                CallExpressionSyntax(
                    CallExpressionSyntax(
                        IdentifierExpressionSyntax('a'),
                        IdentifierExpressionSyntax('b')
                    ),
                    IdentifierExpressionSyntax('c')
                )
            ),
            BindingSyntax(
                'string_calls',
                CallExpressionSyntax(
                    CallExpressionSyntax(
                        StringExpressionSyntax(['a']),
                        StringExpressionSyntax(['b'])
                    ),
                    StringExpressionSyntax(['c'])
                )
            ),
        ])
    ),
    (
        "name = 'World'\ngreet = print 'Hello, \\(name)!'",
        ModuleSyntax([
            BindingSyntax(
                'name',
                StringExpressionSyntax(['World'])
            ),
            BindingSyntax(
                'greet',
                CallExpressionSyntax(
                    IdentifierExpressionSyntax('print'),
                    StringExpressionSyntax([
                        'Hello, ',
                        IdentifierExpressionSyntax('name'),
                        '!',
                    ])
                )
            ),
        ])
    ),
    (
        'var = (3)',
        ModuleSyntax([
            BindingSyntax(
                'var',
                IntegerExpressionSyntax('3')
            ),
        ])
    ),
    (
        'var = (a b)',
        ModuleSyntax([
            BindingSyntax(
                'var',
                CallExpressionSyntax(
                    IdentifierExpressionSyntax('a'),
                    IdentifierExpressionSyntax('b')
                )
            ),
        ])
    ),
    (
        'var = (a b) (c d)',
        ModuleSyntax([
            BindingSyntax(
                'var',
                CallExpressionSyntax(
                    CallExpressionSyntax(
                        IdentifierExpressionSyntax('a'),
                        IdentifierExpressionSyntax('b')
                    ),
                    CallExpressionSyntax(
                        IdentifierExpressionSyntax('c'),
                        IdentifierExpressionSyntax('d')
                    )
                )
            ),
        ])
    ),
    (
        'var = a (b c d)',
        ModuleSyntax([
            BindingSyntax(
                'var',
                CallExpressionSyntax(
                    IdentifierExpressionSyntax('a'),
                    CallExpressionSyntax(
                        CallExpressionSyntax(
                            IdentifierExpressionSyntax('b'),
                            IdentifierExpressionSyntax('c')
                        ),
                        IdentifierExpressionSyntax('d')
                    )
                )
            ),
        ])
    ),
])
def test_success(source, expected):
    tokens = tokenise(source)
    actual = parse(tokens)
    assert actual == expected

@pytest.mark.parametrize('source, expectation, reality', [
    ('var', 'an equals symbol', 'end-of-source'),
    ('var =', 'an expression', 'end-of-source'),
    ('var = =', 'an expression', 'an equals symbol'),
    ('call me', 'an equals symbol', 'an identifier'),
    ("val = call this 'thing' now =", 'a newline', 'an equals symbol'),
    ('name = value\n', 'an identifier', 'end-of-source'),
    ("number = 3\n'not a binding'", 'an identifier', 'a string'),
    ("number = 3\nstring = ''\n", 'an identifier', 'end-of-source'),
    ('=', 'an identifier', 'an equals symbol'),
    ("''", 'an identifier', 'a string'),
    ("'string'", 'an identifier', 'a string'),
    ('100', 'an identifier', 'an integer'),
    ('var = 1 =', 'a newline', 'an equals symbol'),
    ('(', 'an identifier', 'an opening bracket'),
    ('value = (', 'an expression', 'end-of-source'),
    ('value = )', 'an expression', 'a closing bracket'),
    ('value = (hello', 'a closing bracket', 'end-of-source'),
])
def test_failure(source, expectation, reality):
    tokens = tokenise(source)
    expected_error_message = f'Expected {expectation}, got {reality}'
    with pytest.raises(ParseError, match=expected_error_message):
        parse(tokens)
