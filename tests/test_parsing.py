import pytest

from func.parsing import *
from func.tokenising import tokenise


@pytest.mark.parametrize('source, expected', [
    (
        '',
        ModuleSyntax([])
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
