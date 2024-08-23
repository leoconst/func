from .analysed import *
from .opcodes import Opcode


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

def _dereference_references(expression, bindings):
    while isinstance(expression, Reference):
        name = expression.name
        try:
            expression = bindings[name]
        except KeyError:
            raise CompilationError(f'Undefined binding: {name}')
    return expression

def _compile_expression(expression, bindings):
    match _dereference_references(expression, bindings):
        case Integer() as integer:
            return _compile_integer(integer, bindings)
        case String() as string:
            return _compile_string(string, bindings)
        case IfElse() as if_else:
            return _compile_if_else(if_else, bindings)
        case Call() as call:
            return _compile_call(call, bindings)
        case _:
            raise CompilationError(
                f'Unsupported expression type: {expression}')

def _compile_integer(integer, bindings):
    yield Opcode.PUSH
    yield integer.value

def _compile_string(string, bindings):
    value = _extract_string(string.parts)
    raw = value.encode('utf8')
    length = len(raw)
    yield Opcode.SET
    yield length
    yield from raw

def _compile_if_else(if_else, bindings):
    true_block = list(_compile_expression(if_else.true, bindings))
    false_block = _compile_expression(if_else.false, bindings)
    false_block_with_jump = [*false_block, Opcode.JUMP, len(true_block)]
    yield from _compile_expression(if_else.condition, bindings)
    yield Opcode.JUMP_IF
    yield len(false_block_with_jump)
    yield from false_block_with_jump
    yield from true_block

def _compile_call(call, bindings):
    argument = _dereference_references(call.argument, bindings)
    yield from _compile_expression(argument, bindings)
    callable_ = _dereference_references(call.callable_, bindings)
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
