import pytest

from func.compiler import *
from func.analysed import *


@pytest.mark.parametrize('module, expected', [
    (
        Module({
            'main': Call(
                Reference('print'),
                Reference('string')
            ),
            'string': Call(
                Reference('integer_to_string'),
                Reference('value')
            ),
            'value': Call(
                Call(
                    Reference('add'),
                    Reference('x')
                ),
                Reference('y')
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
                Reference('print'),
                Reference('answer')
            ),
            'answer': Call(
                Reference('integer_to_string'), 
                Call(Reference('add1'), Reference('x'))
            ),
            'x': Call(Reference('add1'), Integer(40)),
            'add1': Call(Reference('add'), Integer(1)),
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
            'main': Call(Reference('print'), String(['FUNC'])),
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
            'main': Call(Reference('print'), String([])),
        }),
        [
            Opcode.SET,
            0,
            Opcode.PRINT,
        ]
    ),
    (
        Module({
            'main': IfElse(Integer(1), String(['Yes']), String(['No'])),
        }),
        [
            Opcode.PUSH,
            1,
            Opcode.JUMP_IF,
            6,
            Opcode.SET,
            2,
            *b'No',
            Opcode.JUMP,
            5,
            Opcode.SET,
            3,
            *b'Yes',
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
    (
        Module({
            'main': Call(
                Reference('print'),
                Call(
                    Reference('integer_to_string'),
                    Call(
                        Reference('add10'),
                        Integer(3)
                    ))
            ),
            'add10': Lambda(
                'x',
                Call(Call(Reference('add'), Parameter('x')), Integer(10))
            ),
        }),
        [
            Opcode.PUSH,
            3,
            Opcode.PUSH,
            10,
            Opcode.ADD,
            Opcode.INTEGER_TO_STRING,
            Opcode.PRINT,
        ]
    ),
])
def test_success(module, expected):
    actual = compile_(module)
    assert actual == expected
    
@pytest.mark.parametrize('module', [
    Module({
        'main': Call(
            Reference('print'),
            Call(Reference('integer_to_string'), Integer(3))
        ),
    }),
    Module({
        'x': Call(Reference('integer_to_string'), Integer(3)),
        'main': Call(Reference('print'), Reference('x')),
    }),
    Module({
        'x': Call(Reference('integer_to_string'), Integer(3)),
        'show': Reference('print'),
        'main': Call(Reference('show'), Reference('x')),
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
