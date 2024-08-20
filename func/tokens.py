from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class ConstantToken:
    kind: ConstantTokenKind

@dataclass
class ValueToken:
    kind: ValueTokenKind
    value: str

class ConstantTokenKind(Enum):
    IF = auto()
    THEN = auto()
    ELSE = auto()
    STRING_DELIMITER = auto()
    STRING_EXPRESSION_ESCAPE_START = auto()
    STRING_EXPRESSION_ESCAPE_END = auto()
    EQUALS = auto()
    LAMBDA = auto()
    ARROW = auto()
    NEWLINE = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()

class ValueTokenKind(Enum):
    STRING_CONTENT = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
