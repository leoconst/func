from .analysed import *
from .opcodes import Opcode

from collections import defaultdict
from dataclasses import dataclass, field


def compile_(module):
    bindings = {**module.bindings, **BUILTINS}
    main = _get_main(bindings)
    context = _Context(bindings)
    units = _compile_expression(main, context)
    return list(units)

def _get_main(bindings):
    try:
        return bindings['main']
    except KeyError:
        raise CompilationError('No main binding defined')

def _dereference_references(expression, context):
    while isinstance(expression, Reference):
        name = expression.name
        try:
            expression = context.bindings[name]
        except KeyError:
            raise CompilationError(f'Undefined binding: {name}')
    return expression

def _compile_expression(expression, context):
    match _dereference_references(expression, context):
        case Integer() as integer:
            return _compile_integer(integer, context)
        case String() as string:
            return _compile_string(string, context)
        case IfElse() as if_else:
            return _compile_if_else(if_else, context)
        case Call() as call:
            return _compile_call(call, context)
        case Parameter() as parameter:
            return _compile_parameter(parameter, context)
        case _:
            raise CompilationError(
                f'Unsupported expression type: {expression}')

def _compile_parameter(parameter, context):
    context.parameter_counts[parameter.name] += 1
    if context.parameter_counts[parameter.name] > 1:
        yield Opcode.DUPLICATE

def _compile_integer(integer, context):
    yield Opcode.PUSH
    yield integer.value

def _compile_string(string, context):
    value = _extract_string(string.parts)
    raw = value.encode('utf8')
    length = len(raw)
    yield Opcode.SET
    yield length
    yield from raw

def _compile_if_else(if_else, context):
    true_block = list(_compile_expression(if_else.true, context))
    false_block = _compile_expression(if_else.false, context)
    false_block_with_jump = [*false_block, Opcode.JUMP, len(true_block)]
    yield from _compile_expression(if_else.condition, context)
    yield Opcode.JUMP_IF
    yield len(false_block_with_jump)
    yield from false_block_with_jump
    yield from true_block

def _compile_call(call, context):
    argument = _dereference_references(call.argument, context)
    yield from _compile_expression(argument, context)
    callable_ = _dereference_references(call.callable_, context)
    yield from _compile_callable(callable_, context)

def _compile_callable(expression, context):
    match _dereference_references(expression, context):
        case list() as raw:
            return raw
        case Call():
            return _compile_call(expression, context)
        case Lambda() as lambda_:
            return _compile_lambda(lambda_, context)
        case _:
            raise CompilationError(f'Unsupported callable type: {expression}')

def _compile_lambda(lambda_, context):
    yield from _compile_expression(lambda_.body, context)

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

@dataclass
class _Context:
    bindings: dict
    parameter_counts: defaultdict = field(default_factory=lambda: defaultdict(int))
