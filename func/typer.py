from __future__ import annotations

from dataclasses import dataclass

from . import types
from .analysed import *


def get_type(expression):
    match expression:
        case Integer():
            return types.INTEGER
        case String():
            return types.STRING
        case Lambda() as lambda_:
            return _get_lambda_type(lambda_)
        case Call() as call:
            return _get_call_type(call)
        case IfElse() as if_else:
            return _get_if_else_type(if_else)
        case Raw() as raw:
            return raw.type
        case _:
            raise TypeError(f'Cannot get type of expression: {expression}')

def _get_lambda_type(lambda_):
    parameter_type = types.Named(lambda_.parameter)
    return_type = get_type(lambda_.body)
    return types.Callable(parameter_type, return_type)

def _get_call_type(call):
    callable_type = get_type(call.callable_)
    if not isinstance(callable_type, types.Callable):
        raise TypeError_(
            'Expected a callable,'
            f' got expression of type {callable_type}')
    argument_type = get_type(call.argument)
    parameter_type = callable_type.parameter
    if argument_type != parameter_type:
        raise TypeError_(
            f'Expected expression of type {parameter_type},'
            f' got {argument_type}')
    return callable_type.return_

def _get_if_else_type(if_else):
    condition_type = get_type(if_else.condition)
    if condition_type != types.INTEGER:
        raise TypeError_(
            f'Expected if-else condition to be of type {types.INTEGER},'
            f' got {condition_type}')
    true_type = get_type(if_else.true)
    false_type = get_type(if_else.false)
    if true_type != false_type:
        raise TypeError_('Expected if-else branch types to match,'
            f' got true: {true_type}, false: {false_type}')
    return true_type

class TypeError_(Exception):
    pass
