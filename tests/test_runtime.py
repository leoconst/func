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
])
def test_success(capsys, program, expected_output):
    execute(program)
    captured = capsys.readouterr()
    assert captured.out == expected_output
