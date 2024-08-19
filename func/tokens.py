from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Token:
    kind: TokenKind
    value: str = None

class TokenKind(Enum):
    IF = auto()
    THEN = auto()
    ELSE = auto()
    STRING_DELIMITER = auto()
    STRING_CONTENT = auto()
    STRING_EXPRESSION_ESCAPE_START = auto()
    STRING_EXPRESSION_ESCAPE_END = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    EQUALS = auto()
    LAMBDA = auto()
    ARROW = auto()
    NEWLINE = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()
