from __future__ import annotations

from . import types
from .analysed import *


def get_type(expression):
    expectations = _Expectations()
    return _get_type(expression, expectations)

def _get_type(expression, expectations):
    match expression:
        case Integer():
            return types.INTEGER
        case String():
            return types.STRING
        case Lambda() as lambda_:
            return _get_lambda_type(lambda_, expectations)
        case Parameter() as parameter:
            return _get_parameter_type(parameter, expectations)
        case Call() as call:
            return _get_call_type(call, expectations)
        case IfElse() as if_else:
            return _get_if_else_type(if_else, expectations)
        case Raw() as raw:
            return raw.type
        case _:
            raise TypeError(f'Cannot get type of expression: {expression}')

def _get_lambda_type(lambda_, expectations):
    return_type = _get_type(lambda_.body, expectations)
    name = lambda_.parameter
    parameter_type = expectations.get(name)
    if parameter_type is None:
        parameter_type = types.Named(name)
    return types.Callable(parameter_type, return_type)

def _get_parameter_type(parameter, expectations):
    type = expectations.get(parameter.name)
    if type is None:
        raise TypeError_(f'Undefined parameter: {parameter.name}')
    return type

def _get_call_type(call, expectations):
    callable_type = expectations.expect_callable(call.callable_)
    expectations.expect(call.argument,
        'call argument', callable_type.parameter)
    return callable_type.return_

def _get_if_else_type(if_else, expectations):
    expectations.expect(if_else.condition, 'if-else condition', types.INTEGER)
    if isinstance(if_else.true, Parameter):
        checked_branch, other_branch = if_else.false, if_else.true
    else:
        checked_branch, other_branch = if_else.true, if_else.false
    expected_type = _get_type(checked_branch, expectations)
    expectations.expect(other_branch, 'both if-else branches', expected_type)
    return expected_type

class _Expectations:

    def __init__(self):
        self._parameters = {}

    def expect(self, expression, description, expected):
        match expression:
            case Parameter(name=name) if name not in self._parameters:
                self._parameters[name] = expected
            case _:
                actual = _get_type(expression, self)
                if actual != expected:
                    raise TypeError_(f'Expected {description} to be of type'
                                     f' {expected}, got {actual}')

    def expect_callable(self, expression):
        actual = _get_type(expression, self)
        if not isinstance(actual, types.Callable):
            raise TypeError_(
                f'Expected expression of a callable type, got {actual}')
        return actual

    def get(self, name):
        return self._parameters.get(name, None)

class TypeError_(Exception):
    pass
