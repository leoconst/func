from __future__ import annotations

import itertools
from dataclasses import dataclass, field

from . import types
from .analysed import *


def get_type(expression):
    result = _get_type(expression)
    if result.expectations:
        raise TypeError_(result.expectations)
    return result.type

def _get_type(expression):
    match expression:
        case Integer():
            return Result(types.INTEGER)
        case String():
            return Result(types.STRING)
        case Lambda() as lambda_:
            return _get_lambda_type(lambda_)
        case Call() as call:
            return _get_call_type(call)
        case IfElse() as if_else:
            return _get_if_else_type(if_else)
        case Raw() as raw:
            return Result(raw.type)
        case _:
            raise TypeError(f'Cannot get type of expression: {expression}')

@dataclass
class Result:
    type: Type
    expectations: dict[str, Expectation] = field(default_factory=dict)

@dataclass
class Expectation:
    type: Type
    description: str

def _get_lambda_type(lambda_):
    expectations = _Expectations()
    return_type = expectations.unwrap(_get_type(lambda_.body))
    name = lambda_.parameter
    parameter_expectation = expectations.get(name)
    if parameter_expectation is None:
        parameter_type = types.Named(name)
    else:
        parameter_type = parameter_expectation.type
    return expectations.wrap(types.Callable(parameter_type, return_type))

def _get_call_type(call):
    expectations = _Expectations()
    callable_type = expectations.unwrap(_get_type(call.callable_))
    if not isinstance(callable_type, types.Callable):
        raise TypeError_(
            'Expected a callable,'
            f' got expression of type {callable_type}')
    argument_type = expectations.unwrap(_get_type(call.argument))
    parameter_type = callable_type.parameter
    if argument_type != parameter_type:
        raise TypeError_(
            f'Expected expression of type {parameter_type},'
            f' got {argument_type}')
    return expectations.wrap(callable_type.return_)

def _get_if_else_type(if_else):
    expectations = _Expectations()
    expectations.expect(if_else.condition,
        Expectation(types.INTEGER, 'if-else condition to be of type'))
    true_type = expectations.unwrap(_get_type(if_else.true))
    expectations.expect(if_else.false,
        Expectation(true_type,
            'if-else false branch type to match true branch type'))
    return expectations.wrap(true_type)

class _Expectations:

    def __init__(self):
        self._expectations = {}

    def expect(self, expression, expectation):
        match expression:
            case Parameter() as parameter:
                self.add(parameter.name, expectation)
            case _:
                result = _get_type(expression)
                actual = self.unwrap(result)
                expected = expectation.type
                if actual != expected:
                    raise TypeError_(
                        f'Expected {expectation.description} {expected},'
                        f' got {actual}')

    def add(self, name, expectation):
        self._expectations[name] = expectation

    def get(self, name):
        return self._expectations.pop(name, None)

    def unwrap(self, result):
        match result:
            case Result() as result:
                self._expectations.update(result.expectations)
                return result.type
            case Hole():
                raise TypeError_('Unexpected hole')

    def wrap(self, type):
        return Result(type, self._expectations)

class TypeError_(Exception):
    pass
