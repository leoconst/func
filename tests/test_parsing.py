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
])
def test_success(source, expected):
    tokens = tokenise(source)
    actual = parse(tokens)
    assert actual == expected
