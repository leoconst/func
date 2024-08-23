import pytest
from hypothesis import given, strategies

from func.tokeniser import tokenise
import func.syntax as syntax
from func.parser import parse
from func.analysed import *
from func.analyser import analyse, AnalysisError


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
            'main': Call(Integer(5), Reference('name')),
            'name': String(['World']),
        })
    ),
    (
        "x = 4\ndescription = 'Number is \\(x).'",
        Module({
            'x': Integer(4),
            'description': String(['Number is ', Reference('x'), '.'])
        })
    ),
    (
        'func = λa -> a 7',
        Module({
            'func': Lambda('a', Call(Parameter('a'), Integer(7)))
        })
    ),
    (
        'conditional = if 1 then 2 else 3',
        Module({
            'conditional': IfElse(Integer(1), Integer(2), Integer(3))
        })
    ),
    (
        'function = λoverloaded -> overloaded\noverloaded = 3',
        Module({
            'function': Lambda('overloaded', Parameter('overloaded')),
            'overloaded': Integer(3),
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
call = λcode -> 0\
''').bindings
@given(strategies.permutations(bindings))
def test_binding_ordering_is_arbitrary(bindings):
    module = syntax.Module(bindings)
    expected = Module({
        'main': Call(Reference('print'), Reference('greeting')),
        'greeting': String(['Hello, ', Reference('name'), '!']),
        'name': String(['World']),
        'print': Call(Reference('call'), Integer(7777)),
        'call': Lambda('code', Integer(0)),
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
    ('func = λrun -> it', 'it'),
    ('func = λa -> a b', 'b'),
    ('name = if condition then 1 else 0', 'condition'),
    ("name = if 1 then true else 'no'", 'true'),
    ("name = if 0 then 'yes' else false", 'false'),
])
def test_unbound_name(source, name):
    syntax = _get_syntax(source)
    with pytest.raises(AnalysisError, match=f"Unbound name: '{name}'"):
        analyse(syntax)
