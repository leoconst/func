import pytest

from func.compiler import *
from func.analysis import *


@pytest.mark.parametrize('module, expected', [
    (
        Module({
            'main': Call(
                Identifier('print'),
                Identifier('string')
            ),
            'string': Call(
                Identifier('integer_to_string'),
                Identifier('value')
            ),
            'value': Call(
                Call(
                    Identifier('add'),
                    Identifier('x')
                ),
                Identifier('y')
            ),
            'x': Integer(3),
            'y': Integer(4),
        }),
        [
            Opcode.PUSH,
            4,
            Opcode.PUSH,
            3,
            Opcode.ADD,
            Opcode.INTEGER_TO_STRING,
            Opcode.PRINT,
        ]
    ),
    (
        Module({
            'main': Call(
                Identifier('print'),
                Identifier('answer')
            ),
            'answer': Call(
                Identifier('integer_to_string'), 
                Call(Identifier('add1'), Identifier('x'))
            ),
            'x': Call(Identifier('add1'), Integer(40)),
            'add1': Call(Identifier('add'), Integer(1)),
        }),
        [
            Opcode.PUSH,
            40,
            Opcode.PUSH,
            1,
            Opcode.ADD,
            Opcode.PUSH,
            1,
            Opcode.ADD,
            Opcode.INTEGER_TO_STRING,
            Opcode.PRINT,
        ]
    ),
    (
        Module({
            'main': Call(Identifier('print'), String(['FUNC'])),
        }),
        [
            Opcode.SET,
            4,
            *b'FUNC',
            Opcode.PRINT,
        ]
    ),
    (
        Module({
            'main': Call(Identifier('print'), String([])),
        }),
        [
            Opcode.SET,
            0,
            Opcode.PRINT,
        ]
    ),
    (
        Module({
            'main': IfElse(Integer(1), Integer(3), Integer(4)),
        }),
        [
            Opcode.PUSH,
            1,
            Opcode.JUMP_IF,
            4,
            Opcode.PUSH,
            4,
            Opcode.JUMP,
            2,
            Opcode.PUSH,
            3,
        ]
    ),
])
def test_success(module, expected):
    actual = compile_(module)
    assert actual == expected
    
@pytest.mark.parametrize('module', [
    Module({
        'main': Call(
            Identifier('print'),
            Call(Identifier('integer_to_string'), Integer(3))
        ),
    }),
    Module({
        'x': Call(Identifier('integer_to_string'), Integer(3)),
        'main': Call(Identifier('print'), Identifier('x')),
    }),
    Module({
        'x': Call(Identifier('integer_to_string'), Integer(3)),
        'show': Identifier('print'),
        'main': Call(Identifier('show'), Identifier('x')),
    }),
])
def test_identifier_dereferencing(module):
    expected = [
        Opcode.PUSH,
        3,
        Opcode.INTEGER_TO_STRING,
        Opcode.PRINT,
    ]
    test_success(module, expected)

@pytest.mark.parametrize('module', [
    Module({}),
    Module({
        'a': Integer(3),
    }),
    Module({
        'a': Integer(3),
        'moin': Integer(0),
    }),
])
def test_no_main_binding(module):
    with pytest.raises(CompilationError, match='No main binding defined'):
        compile_(module)
