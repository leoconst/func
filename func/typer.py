from __future__ import annotations

from . import types
from .analysed import *


def get_type(expression):
    expectations = _Expectations()
    type = _get_type(expression, expectations)
    if expectations.contains_unused():
        raise ValueError('Unused parameter expectations')
    return type

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
    callable_type = _get_type(call.callable_, expectations)
    if not isinstance(callable_type, types.Callable):
        raise TypeError_(
            'Expected a callable,'
            f' got expression of type {callable_type}')
    argument_type = _get_type(call.argument, expectations)
    parameter_type = callable_type.parameter
    if argument_type != parameter_type:
        raise TypeError_(
            f'Expected expression of type {parameter_type},'
            f' got {argument_type}')
    return callable_type.return_

def _get_if_else_type(if_else, expectations):
    expectations.expect(if_else.condition,
        'if-else condition to be of type', types.INTEGER)
    match if_else.true:
        case Parameter() as parameter:
            checked_branch = if_else.false
            other_branch = if_else.true
        case _:
            checked_branch = if_else.true
            other_branch = if_else.false
    expected_type = _get_type(checked_branch, expectations)
    expectations.expect(other_branch,
        'if-else branch types to match', expected_type)
    return expected_type

class _Expectations:

    def __init__(self):
        self._parameters = {}

    def expect(self, expression, description, expected):
        match expression:
            case Parameter(name) if name not in self._parameters:
                self._parameters[name] = expected
            case _:
                actual = _get_type(expression, self)
                if actual != expected:
                    raise TypeError_(
                        f'Expected {description} {expected}, got {actual}')

    def get(self, name):
        return self._parameters.pop(name, None)

    def contains_unused(self):
        return bool(self._parameters)

class TypeError_(Exception):
    pass
