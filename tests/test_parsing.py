import tests

from func.parsing import *


def test_example():
    source = "name = 'World'\ngreet = print 'Hello, \\(name)!'"
    actual = parse(source)
    expected = ModuleSyntax([
        BindingSyntax(
            'name',
            StringExpressionSyntax([
                'World',
            ])
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
    assert actual == expected
