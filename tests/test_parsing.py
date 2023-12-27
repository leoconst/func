from func.parsing import *
from func.tokenising import tokenise


def test_empty():
    tokens = []
    actual = parse(tokens)
    expected = ModuleSyntax([])
    assert actual == expected

def test_example():
    source = "name = 'World'\ngreet = print 'Hello, \\(name)!'"
    tokens = tokenise(source)
    actual = parse(tokens)
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
