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
        case Call() as call:
            return _get_call_type(call)
        case Raw() as raw:
            return raw.type
        case _:
            raise TypeError(f'Cannot get type of expression: {expression}')

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

class TypeError_(Exception):
    pass
