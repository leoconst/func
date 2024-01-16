from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


def tokenise(source):
    source = _Source(source)
    return _tokenise_with(source)

def _tokenise_with(source):
    tokens = source.get_next_raw_tokens()
    while token := next(tokens, False):
        raw_kind, value = token
        match raw_kind:
            case _RawTokenKind.MISMATCH:
                raise TokeniseError(f'Unexpected character: {value!r}')
            case _RawTokenKind.IGNORED:
                continue
        kind = TokenKind[raw_kind.name]
        yield _make_token(kind, value)
        if kind == TokenKind.STRING_DELIMITER:
            yield from _tokenise_string(source)
            tokens = source.get_next_raw_tokens()

def _make_token(kind, value):
    if kind in _VALUE_KINDS:
        return Token(kind, value)
    return Token(kind)

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

_VALUE_KINDS = {
    TokenKind.STRING_CONTENT,
    TokenKind.IDENTIFIER,
    TokenKind.INTEGER,
}

class TokeniseError(Exception):
    pass

_STRING_DELIMITER = '\''

class _RawTokenKind(Enum):
    IF = r'\bif\b'
    THEN = r'\bthen\b'
    ELSE = r'\belse\b'
    STRING_DELIMITER = _STRING_DELIMITER
    IDENTIFIER = r'[A-Za-z_][A-Za-z0-9_]*'
    INTEGER = r'[0-9]+'
    EQUALS = r'='
    LAMBDA = r'\\|λ'
    ARROW = r'->'
    NEWLINE = r'\n|\r\n'
    OPEN_BRACKET = r'\('
    CLOSE_BRACKET = r'\)'
    IGNORED = r'[ \t]+'
    MISMATCH = r'.'

_RAW_TOKEN_RE = re.compile(
    r'|'.join(rf'(?P<{raw_token_kind.name}>{raw_token_kind.value})'
        for raw_token_kind in _RawTokenKind), re.DOTALL)

def _tokenise_string(source):
    content_builder = _StringContentBuilder()
    while True:
        head = source.get_next_character('inside string')
        if head == _STRING_DELIMITER:
            break
        if head == '\\':
            yield from _handle_escape(source, content_builder)
        else:
            content_builder.add_character(head)
    yield from content_builder.token()
    yield Token(TokenKind.STRING_DELIMITER)

def _handle_escape(source, content_builder):
    character = source.get_next_character('immediately after string escape')
    if character == '(':
        yield from _handle_expression_escape(source, content_builder)
    else:
        _handle_character_escape(content_builder, character)

def _handle_expression_escape(source, content_builder):
    yield from content_builder.token()
    yield Token(TokenKind.STRING_EXPRESSION_ESCAPE_START)
    yield from _tokenise_until_brackets_balanced(source)
    yield Token(TokenKind.STRING_EXPRESSION_ESCAPE_END)

def _tokenise_until_brackets_balanced(source):
    bracket_depth = 0
    for token in _tokenise_with(source):
        match token.kind:
            case TokenKind.OPEN_BRACKET:
                bracket_depth += 1
            case TokenKind.CLOSE_BRACKET:
                if bracket_depth <= 1:
                    break
                bracket_depth -= 1
        yield token
    else:
        raise _end_of_source_error('inside expression escape')

def _handle_character_escape(content_builder, character):
    try:
        escaped_character = _CHARACTER_ESCAPES[character]
    except KeyError:
        raise TokeniseError(f'Invalid escape character: {character!r}')
    content_builder.add_character(escaped_character)

_CHARACTER_ESCAPES = {
    'n': '\n',
    't': '\t',
    '\'': '\'',
}

def _end_of_source_error(location):
    return TokeniseError(f'Unexpected end-of-source {location}')

class _StringContentBuilder:

    def __init__(self):
        self._characters = []

    def add_character(self, character):
        self._characters.append(character)

    def token(self):
        characters = self._characters
        if characters:
            content = ''.join(characters)
            characters.clear()
            yield Token(TokenKind.STRING_CONTENT, content)

class _Source:

    def __init__(self, source):
        self._source = source
        self._position = 0

    def get_next_character(self, location):
        try:
            character = self._source[self._position]
        except IndexError:
            raise _end_of_source_error(location)
        self._position += 1
        return character

    def get_next_raw_tokens(self):
        remainder = self._source[self._position:]
        for match in _RAW_TOKEN_RE.finditer(remainder):
            kind = _RawTokenKind[match.lastgroup]
            value = match.group()
            self._position += len(value)
            yield (kind, value)
