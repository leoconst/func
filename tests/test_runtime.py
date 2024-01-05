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
    out, _ = capsys.readouterr()
    assert out == '42\n'
