import pytest

from func.tokens import tokenise
from func.syntax import parse
from func.analysis import *


@pytest.mark.parametrize('source, expected', [
    (
        'name0 = 0\nname1 = 1',
        Module({
            'name0': Integer(0),
            'name1': Integer(1),
        })
    ),
    (
        "main = 5 name\nname = 'World'",
        Module({
            'main': Call(Integer(5), Identifier('name')),
            'name': String(['World']),
        })
    ),
    (
        "name = 'World'\nmain = 5 name",
        Module({
            'main': Call(Integer(5), Identifier('name')),
            'name': String(['World']),
        })
    ),
    (
        "x = 4\ndescription = 'Number is \\(x).'",
        Module({
            'x': Integer(4),
            'description': String(['Number is ', Identifier('x'), '.'])
        })
    ),
])
def test_success(source, expected):
    syntax = _get_syntax(source)
    actual = analyse(syntax)
    assert actual == expected

def test_duplicate_binding_name():
    syntax = _get_syntax('name = 0\nname = 1')
    with pytest.raises(AnalysisError, match="Duplicate binding name: 'name'"):
        analyse(syntax)

@pytest.mark.parametrize('source, name', [
    ('name = q', 'q'),
    ("main = print name\nprint = 3", 'name'),
    ("main = 'The answer is \\(answer)!'", 'answer'),
])
def test_unbound_name(source, name):
    syntax = _get_syntax(source)
    with pytest.raises(AnalysisError, match=f"Unbound name: '{name}'"):
        analyse(syntax)

def _get_syntax(source):
    tokens = tokenise(source)
    return parse(tokens)
