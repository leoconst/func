from __future__ import annotations

from dataclasses import dataclass, field

from . import types
from .analysed import *


def get_type(expression):
    expectations = _Expectations()
    type = _get_type(expression, expectations)
    unresolved_expectations = expectations.get_all()
    if unresolved_expectations:
        raise TypeError_(unresolved_expectations)
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

@dataclass
class Expectation:
    type: Type
    description: str

def _get_lambda_type(lambda_, expectations):
    return_type = _get_type(lambda_.body, expectations)
    name = lambda_.parameter
    parameter_expectation = expectations.get(name)
    if parameter_expectation is None:
        parameter_type = types.Named(name)
    else:
        parameter_type = parameter_expectation.type
    return types.Callable(parameter_type, return_type)

def _get_parameter_type(parameter, expectations):
    expectation = expectations.get(parameter.name)
    if expectation is None:
        raise TypeError_(f'Undefined parameter: {parameter.name}')
    return expectation.type

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
        Expectation(types.INTEGER, 'if-else condition to be of type'))
    match if_else.true:
        case Parameter() as parameter:
            checked_branch = if_else.false
            other_branch = if_else.true
        case _:
            checked_branch = if_else.true
            other_branch = if_else.false
    expected_type = _get_type(checked_branch, expectations)
    expectations.expect(other_branch,
        Expectation(expected_type, 'if-else branch types to match'))
    return expected_type

class _Expectations:

    def __init__(self):
        self._unnamed = []
        self._named = {}

    def expect(self, expression, expectation):
        match expression:
            case Parameter() as parameter:
                self._named[parameter.name] = expectation
            case _:
                actual = _get_type(expression, self)
                expected = expectation.type
                if actual != expected:
                    self._unnamed.append((expectation, actual))

    def get(self, name):
        return self._named.pop(name, None)

    def get_all(self):
        return self._unnamed

class TypeError_(Exception):

    def __init__(self, expectations):
        if (isinstance(expectations, str)):
            super().__init__(expectations)
            return
        expectation_count = len(expectations)
        if expectation_count != 1:
            raise ValueError(
                f'Expected only 1 expectation, got {expectation_count}')
        expectation, actual = expectations[0]
        message = (f'Expected {expectation.description} {expectation.type},'
                   f' got {actual}')
        super().__init__(message)
