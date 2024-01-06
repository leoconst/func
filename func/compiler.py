from enum import Enum, auto

from .analysis import *


def compile_(module):
    bindings = {**module.bindings, **BUILTINS}
    main = _get_main(bindings)
    units = compile_expression(main, bindings)
    return list(units)

def _get_main(bindings):
    try:
        return bindings['main']
    except KeyError:
        raise CompilationError('No main binding defined')

def _dereference_identifiers(expression, bindings):
    while isinstance(expression, Identifier):
        name = expression.name
        try:
            expression = bindings[name]
        except KeyError:
            raise CompilationError(f'Undefined binding: {name}')
    return expression

def compile_expression(expression, bindings):
    match _dereference_identifiers(expression, bindings):
        case Call():
            return _compile_call(expression, bindings)
        case _:
            CompilationError(f'Unsupported expression type: {expression}')

def _compile_identifier(identifier, bindings):
    value = bindings[identifier.value]
    return compile_expression(value)

def _compile_call(call, bindings):
    argument = _dereference_identifiers(call.argument, bindings)
    yield from _compile_argument(argument, bindings)
    callable_ = _dereference_identifiers(call.callable_, bindings)
    yield from _compile_callable(callable_, bindings)

def _compile_callable(expression, bindings):
    match expression:
        case list() as raw:
            return raw
        case Call():
            return _compile_call(expression, bindings)
        case _:
            raise CompilationError(f'Unsupported callable type: {expression}')

def _compile_argument(expression, bindings):
    match expression:
        case Integer(value):
            yield Opcode.PUSH
            yield value
        case Call():
            yield from _compile_call(expression, bindings)
        case _:
            raise CompilationError(f'Unsupported argument type: {expression}')

class Opcode(Enum):
    PUSH = auto()
    ADD = auto()
    PRINT = auto()

BUILTINS = {
    'print': [
        Opcode.PRINT,
    ],
    'add': [
        Opcode.ADD,
    ]
}

class CompilationError(Exception):
    pass
