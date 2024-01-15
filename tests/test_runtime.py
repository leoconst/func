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
            Opcode.PUSH, 6,
            Opcode.CALL, 7, # factorial
            Opcode.INTEGER_TO_STRING,
            Opcode.PRINT,
            Opcode.END,
            # factorial: [n]
            Opcode.COPY, # [n, n]
            Opcode.PUSH, 2, # [2, n, n]
            Opcode.MOVE, 1, # [n, 2, n]
            Opcode.LESS_THAN_OR_EQUAL, # [0|1, n]
            Opcode.JUMP_IF, 20, # (factorial_1) [n]
            Opcode.COPY, # [n, n]
            Opcode.DECREMENT, # [(n - 1), n]
            Opcode.CALL, 7, # factorial [(n - 1)!, n]
            Opcode.MULTIPLY, # [(n - 1)!*n]
            Opcode.RETURN,
            # factorial_1: [n]
            Opcode.RETURN,
        ],
        '720\n'
    ),
])
def test_success(capsys, program, expected_output):
    execute(program)
    captured = capsys.readouterr()
    assert captured.out == expected_output
