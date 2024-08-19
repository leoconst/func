from enum import Enum, auto


class Opcode(Enum):
    PUSH = auto()
    SET = auto()
    PRINT = auto()
    ADD = auto()
    JUMP = auto()
    JUMP_IF = auto()
    INTEGER_TO_STRING = auto()
