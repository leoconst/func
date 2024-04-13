from enum import Enum, auto

from .analysis import *


def compile_(module):
    bindings = {**module.bindings, **BUILTINS}
    main = _get_main(bindings)
    units = _compile_expression(main, bindings)
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

def _compile_expression(expression, bindings):
    match _dereference_identifiers(expression, bindings):
        case Integer(value):
            yield Opcode.PUSH
            yield value
        case String():
            value = _extract_string(expression.parts)
            raw = value.encode('utf8')
            length = len(raw)
            yield Opcode.SET
            yield length
            yield from raw
        case Call():
            yield from _compile_call(expression, bindings)
        case IfElse(condition, true, false):
            yield from _compile_expression(condition, bindings)
            yield Opcode.JUMP_IF
            false_block = list(_compile_expression(false, bindings))
            yield len(false_block)
            yield from false_block
            true_block = _compile_expression(true, bindings)
            yield from true_block
        case _:
            CompilationError(f'Unsupported expression type: {expression}')

def _compile_call(call, bindings):
    argument = _dereference_identifiers(call.argument, bindings)
    yield from _compile_expression(argument, bindings)
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

def _extract_string(parts):
    match parts:
        case []:
            return ''
        case [str() as content]:
            return content
        case _:
            raise CompilationError(
                'String expression escapes are not supported')

class Opcode(Enum):
    PUSH = auto()
    SET = auto()
    PRINT = auto()
    ADD = auto()
    JUMP_IF = auto()
    INTEGER_TO_STRING = auto()

BUILTINS = {
    'print': [
        Opcode.PRINT,
    ],
    'add': [
        Opcode.ADD,
    ],
    'integer_to_string': [
        Opcode.INTEGER_TO_STRING,
    ],
}

class CompilationError(Exception):
    pass
