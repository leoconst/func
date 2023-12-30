import pytest
from hypothesis import given, strategies

from func.tokens import tokenise
import func.syntax as syntax
from func.syntax import parse
from func.analysis import *


def _get_syntax(source):
    tokens = tokenise(source)
    return parse(tokens)

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

bindings = _get_syntax('''\
main = print greeting
greeting = 'Hello, \\(name)!'
name = 'World'
print = call 7777
call = 0\
''').bindings
@given(strategies.permutations(bindings))
def test_binding_ordering_is_arbitrary(bindings):
    module = syntax.Module(bindings)
    expected = Module({
        'main': Call(Identifier('print'), Identifier('greeting')),
        'greeting': String(['Hello, ', Identifier('name'), '!']),
        'name': String(['World']),
        'print': Call(Identifier('call'), Integer(7777)),
        'call': Integer(0),
    })
    actual = analyse(module)
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