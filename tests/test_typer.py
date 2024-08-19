import pytest
import testing

from func import types
from func.typer import get_type, TypeError_, Typed
from func.analysed import *


_INTEGER_STRING_INTEGER = types.Callable(
    types.INTEGER,
    types.Callable(
        types.STRING,
        types.INTEGER))

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
        Call(Call(Typed(_INTEGER_STRING_INTEGER), Integer(2)), String([])),
        types.INTEGER
    ),
])
def test_success(expression, expected_type):
    actual_type = get_type(expression)
    assert actual_type == expected_type

@pytest.mark.parametrize('expression, expected_message', [
    (
        Call(Call(Typed(_INTEGER_STRING_INTEGER), Integer(2)), Integer(2)),
        'Expected expression of type String, got Integer',
    ),
    (
        Call(Integer(0), Integer(0)),
        'Expected a callable, got expression of type Integer',
    ),
])
def test_failure(expression, expected_message):
    with testing.raises(TypeError_, message=expected_message):
        get_type(expression)

@pytest.mark.parametrize('expression', [
    Lambda('parameter', Integer(0)),
    IfElse(Integer(0), String(['Yes']), String(['No'])),
])
def test_unsupported(expression):
    expected_message = f'Cannot get type of expression: {expression}'
    with testing.raises(TypeError, message=expected_message):
        get_type(expression)
