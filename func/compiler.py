from enum import Enum, auto

from .analysis import *


def compile_(module):
    bindings = {**module.bindings, **_BUILTINS}
    main = get_main(bindings)
    units = compile_expression(main, bindings)
    return list(units)

def get_main(bindings):
    try:
        return bindings['main']
    except KeyError:
        raise CompilationError('No main binding defined')

def dereference_identifiers(expression, bindings):
    while isinstance(expression, Identifier):
        try:
            expression = bindings[expression.name]
        except KeyError:
            raise CompilationError(f'Undefined binding: {name}')
    return expression

def compile_expression(expression, bindings):
    match dereference_identifiers(expression, bindings):
        case Call():
            return compile_call(expression, bindings)
        case _:
            CompilationError(f'Unsupported expression type: {expression}')

def compile_identifier(identifier, bindings):
    value = bindings[identifier.value]
    return compile_expression(value)

def compile_call(call, bindings):
    argument = dereference_identifiers(call.argument, bindings)
    yield from compile_argument(argument)
    callable_ = dereference_identifiers(call.callable_, bindings)
    yield from compile_callable(callable_)

def compile_callable(expression):
    return expression

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
    ],
}

class CompilationError(Exception):
    pass
