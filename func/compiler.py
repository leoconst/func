from enum import Enum, auto

from .analysis import *


def compile_(module):
    main = get_main(module)
    units = compile_expression(main)
    return list(units)

def get_main(module):
    try:
        return module.bindings['main']
    except KeyError:
        raise CompilationError('No main binding defined')

def compile_expression(expression):
    match expression:
        case Call():
            return compile_call(expression)
        case _:
            CompilationError(f'Unsupported expression type: {expression}')

def compile_call(call):
    yield from compile_argument(call.argument)
    yield from compile_callable(call.callable_)

def compile_callable(expression):
    match expression:
        case Identifier():
            return compile_callable_identifier(expression)
        case _:
            raise CompilationError(f'Unsupported call type: {expression}')

def compile_callable_identifier(identifier):
    try:
        return _BUILTINS[identifier.name]
    except KeyError:
        raise CompilationError(f'Undefined call: {identifier}')

def compile_argument(expression):
    match expression:
        case Integer(value):
            yield Opcode.PUSH
            yield value
        case _:
            raise CompilationError(f'Unsupported argument type: {expression}')

class Opcode(Enum):
    PUSH = auto()
    PRINT = auto()

_BUILTINS = {
    'print': [
        Opcode.PRINT,
    ]
}

class CompilationError(Exception):
    pass
