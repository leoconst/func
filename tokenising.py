from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable


class TokeniseError(Exception):
    pass

def tokenise(source):
    for raw_kind, value in _get_raw_tokens(source):
        kind = _token_kind(raw_kind, value)
        if kind is not None:
            yield Token(kind, value)

def _get_raw_tokens(source):
    for match in _RAW_TOKEN_RE.finditer(source):
        kind = _RawTokenKind[match.lastgroup]
        value = match.group()
        yield (kind, value)

def _token_kind(raw_kind, value):
    match raw_kind:
        case _RawTokenKind.MISMATCH:
            raise TokeniseError(f'Unexpected character: {value!r}')
        case _RawTokenKind.IGNORED:
            return
        case other:
            return TokenKind[other.name]

class TokenKind(Enum):
    STRING_START = auto()
    STRING_CONTENTS = auto()
    STRING_ESCAPE = auto()
    STRING_ESCAPE_CHARACTER = auto()
    STRING_END = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    EQUALS = auto()
    NEWLINE = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()

class _RawTokenKind(Enum):
    STRING_START = r'\''
    STRING_CONTENTS = r'(?<=[\'\)])[^\'\\]+(?=[\\])'
    STRING_ESCAPE = r'\\'
    STRING_ESCAPE_CHARACTER = r'(?<=\\)[nt]'
    IDENTIFIER = r'[A-Za-z_][A-Za-z0-9_]*'
    INTEGER = r'[0-9]+'
    EQUALS = r'='
    NEWLINE = r'\n|\r\n'
    OPEN_BRACKET = r'\('
    CLOSE_BRACKET = r'\)'
    IGNORED = r'[ \t]+'
    STRING_END = r'(?<=[\'\)])[^\'\\]*\''
    MISMATCH = r'.'

_RAW_TOKEN_RE = re.compile(
    r'|'.join(rf'(?P<{raw_token_kind.name}>{raw_token_kind.value})'
        for raw_token_kind in _RawTokenKind), re.DOTALL)

@dataclass
class Token:
    kind: TokenKind
    value: str


def _main():
    source = " \t repeat 3 'Two plus three equals:\\n\\t\\(add\t2 3).'  \r\n\n= \t"
    actual = list(tokenise(source))
    expected = [
        Token(TokenKind.IDENTIFIER, 'repeat'),
        Token(TokenKind.INTEGER, '3'),
        Token(TokenKind.STRING_START, '\''),
        Token(TokenKind.STRING_CONTENTS, 'Two plus three equals:'),
        Token(TokenKind.STRING_ESCAPE, '\\'),
        Token(TokenKind.STRING_ESCAPE_CHARACTER, 'n'),
        Token(TokenKind.STRING_ESCAPE, '\\'),
        Token(TokenKind.STRING_ESCAPE_CHARACTER, 't'),
        Token(TokenKind.STRING_ESCAPE, '\\'),
        Token(TokenKind.OPEN_BRACKET, '('),
        Token(TokenKind.IDENTIFIER, 'add'),
        Token(TokenKind.INTEGER, '2'),
        Token(TokenKind.INTEGER, '3'),
        Token(TokenKind.CLOSE_BRACKET, ')'),
        Token(TokenKind.STRING_END, '.\''),
        Token(TokenKind.NEWLINE, '\r\n'),
        Token(TokenKind.NEWLINE, '\n'),
        Token(TokenKind.EQUALS, '='),
    ]
    from pprint import pprint
    pprint(list(zip(actual, expected)))
    assert actual == expected

if __name__ == '__main__':
    _main()