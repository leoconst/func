import pytest

from func.compiler import Opcode
from func.runtime import execute


@pytest.mark.parametrize('program, expected_output', [
    (
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
        ],
        '42\n'
    ),
    (
        [
            Opcode.SET,
            13,
            *b'Hello, world!',
            Opcode.PRINT,
        ],
        'Hello, world!\n'
    ),
    (
        [
            Opcode.PUSH,
            1,
            Opcode.JUMP_IF,
            4,
            Opcode.PUSH,
            8,
            Opcode.JUMP,
            2,
            Opcode.PUSH,
            5,
            Opcode.INTEGER_TO_STRING,
            Opcode.PRINT,
        ],
        '5\n'
    ),
    (
        [
            Opcode.PUSH,
            0,
            Opcode.JUMP_IF,
            4,
            Opcode.PUSH,
            8,
            Opcode.JUMP,
            2,
            Opcode.PUSH,
            5,
            Opcode.INTEGER_TO_STRING,
            Opcode.PRINT,
        ],
        '8\n'
    ),
])
def test_success(capsys, program, expected_output):
    execute(program)
    captured = capsys.readouterr()
    assert captured.out == expected_output
