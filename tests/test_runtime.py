from func.compiler import Opcode
from func.runtime import execute


def test(capsys):
    execute([
        Opcode.PUSH,
        40,
        Opcode.PUSH,
        1,
        Opcode.ADD,
        Opcode.PUSH,
        1,
        Opcode.ADD,
        Opcode.PRINT,
    ])
    captured = capsys.readouterr()
    assert captured.out == '42\n'
