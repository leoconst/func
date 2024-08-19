from .analysed import Raw
from .opcodes import Opcode
from .types import Callable, INTEGER, STRING, UNIT


BUILTINS = {
    'print': Raw(
        Callable(STRING, UNIT),
        [
            Opcode.PRINT,
        ]),
    'add': Raw(
        Callable(INTEGER, Callable(INTEGER, INTEGER)),
        [
            Opcode.ADD,
        ]),
    'integer_to_string': Raw(
        Callable(INTEGER, STRING),
        [
            Opcode.INTEGER_TO_STRING,
        ]),
}
