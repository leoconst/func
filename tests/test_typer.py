import pytest
import testing

from func import types
from func.typer import get_type, TypeError_
from func.analysed import *
from func.builtins import BUILTINS


_INTEGER_STRING_INTEGER_TYPE = types.Callable(
    types.INTEGER,
    types.Callable(
        types.STRING,
        types.INTEGER))
_INTEGER_STRING_INTEGER_LAMBDA = Raw(_INTEGER_STRING_INTEGER_TYPE, [])
_ADD = BUILTINS['add']

@pytest.mark.parametrize('expression, expected_type', [
    (
        Integer(0),
        types.INTEGER
    ),
    (
        String([]),
        types.STRING
    ),
    (
        Call(Call(_INTEGER_STRING_INTEGER_LAMBDA, Integer(2)), String([])),
        types.INTEGER
    ),
    (
        Call(Call(_ADD, Integer(2)), Integer(2)),
        types.INTEGER
    ),
    (
        Lambda('a', Integer(0)),
        types.Callable(types.Named('a'), types.INTEGER)
    ),
    (
        Lambda('a', IfElse(Parameter('a'), String([]), String([]))),
        types.Callable(types.INTEGER, types.STRING)
    ),
    (
        Lambda('a', IfElse(Integer(0), String([]), Parameter('a'))),
        types.Callable(types.STRING, types.STRING)
    ),
    (
        Lambda('a', IfElse(Integer(0), Parameter('a'), String([]))),
        types.Callable(types.STRING, types.STRING)
    ),
    (
        Lambda('a', IfElse(Parameter('a'), Parameter('a'), Parameter('a'))),
        types.Callable(types.INTEGER, types.INTEGER)
    ),
    (
        Lambda('a', Call(Call(_ADD, Parameter('a')), Integer(0))),
        types.Callable(types.INTEGER, types.INTEGER)
    ),
    (
        Lambda('a', Call(Call(_ADD, Integer(0)), Parameter('a'))),
        types.Callable(types.INTEGER, types.INTEGER)
    ),
    (
        Lambda('a', Call(Call(_ADD, Parameter('a')), Parameter('a'))),
        types.Callable(types.INTEGER, types.INTEGER)
    ),
    (
        Lambda('a', Call(Parameter('a'), Integer(7))),
        types.Callable(
            types.Callable(types.INTEGER, types.Named('a')),
            types.Named('a'))
    ),
])
def test_success(expression, expected_type):
    actual_type = get_type(expression)
    assert actual_type == expected_type

@pytest.mark.parametrize('expression, expected_message', [
    (
        Call(Call(_INTEGER_STRING_INTEGER_LAMBDA, Integer(2)), Integer(2)),
        'Expected call argument to be of type String, got Integer',
    ),
    (
        Call(Integer(0), Integer(0)),
        'Expected expression of a callable type, got Integer',
    ),
    (
        IfElse(String([]), Integer(0), Integer(0)),
        'Expected if-else condition to be of type Integer, got String'
    ),
    (
        IfElse(Integer(0), Integer(0), String([])),
        'Expected both if-else branches to be of type Integer, got String'
    ),
    (
        Lambda('a', IfElse(Parameter('a'), Parameter('a'), String([]))),
        'Expected both if-else branches to be of type String, got Integer'
    ),
    (
        Lambda('a', IfElse(Parameter('a'), String([]), Parameter('a'))),
        'Expected both if-else branches to be of type String, got Integer'
    ),
    (
        Parameter('greetings'),
        'Undefined parameter: greetings'
    ),
])
def test_failure(expression, expected_message):
    with testing.raises(TypeError_, message=expected_message):
        get_type(expression)

@pytest.mark.parametrize('expression', [
    Reference('b'),
])
def test_unsupported(expression):
    expected_message = f'Cannot get type of expression: {expression}'
    with testing.raises(TypeError, message=expected_message):
        get_type(expression)