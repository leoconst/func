from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


def tokenise(source):
    source = _Source(source)
    context = _Context()
    return _tokenise_with_context(source, context)

def _tokenise_with_context(source, context):
    for raw_kind, value in source.get_next_raw_tokens():
        match raw_kind:
            case _RawTokenKind.MISMATCH:
                raise TokeniseError(f'Unexpected character: {value!r}')
            case _RawTokenKind.IGNORED:
                continue
            case _RawTokenKind.STRING_DELIMITER:
                yield _tokenise_string(source)
                yield from _tokenise_with_context(source, context)
                return
            case _RawTokenKind.OPEN_BRACKET:
                context.bracket_depth += 1
            case _RawTokenKind.CLOSE_BRACKET:
                context.bracket_depth -= 1
        kind = TokenKind[raw_kind.name]
        yield PlainToken(kind, value)

class Token:
    pass

@dataclass
class PlainToken(Token):
    kind: TokenKind
    value: str

class TokenKind(Enum):
    STRING = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    EQUALS = auto()
    NEWLINE = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()

@dataclass
class StringToken(Token):
    kind = TokenKind.STRING
    parts: list[str|list[Token]]

class TokeniseError(Exception):
    pass

_STRING_DELIMETER = '\''

class _RawTokenKind(Enum):
    STRING_DELIMITER = _STRING_DELIMETER
    IDENTIFIER = r'[A-Za-z_][A-Za-z0-9_]*'
    INTEGER = r'[0-9]+'
    EQUALS = r'='
    NEWLINE = r'\n|\r\n'
    OPEN_BRACKET = r'\('
    CLOSE_BRACKET = r'\)'
    IGNORED = r'[ \t]+'
    MISMATCH = r'.'

_RAW_TOKEN_RE = re.compile(
    r'|'.join(rf'(?P<{raw_token_kind.name}>{raw_token_kind.value})'
        for raw_token_kind in _RawTokenKind), re.DOTALL)

def _tokenise_string(source):
    token_builder = _StringTokenBuilder()
    while True:
        head = source.get_next_character('inside string')
        if head == _STRING_DELIMETER:
            return token_builder.build()
        if head == '\\':
            _tokenise_escape(source, token_builder)
        else:
            token_builder.add_plain_character(head)

def _tokenise_escape(source, token_builder):
    head = source.get_next_character('immediately after string escape')
    if head == '(':
        _add_expression_escape_part(source, token_builder)
    elif head in _CHARACTER_ESCAPES:
        _add_escaped_character(token_builder, head)
    else:
        raise TokeniseError(f'Invalid escape character: {head!r}')

def _add_expression_escape_part(source, token_builder):
    token_builder.add_plain_part_if_any()
    tokens = list(_tokenise_until_brackets_balanced(source))
    token_builder.add_expression_escape_part(tokens)

def _tokenise_until_brackets_balanced(source):
    context = _Context(bracket_depth=1)
    for token in _tokenise_with_context(source, context):
        if context.bracket_depth <= 0:
            break
        yield token
    else:
        raise _end_of_source_error('inside expression escape')

def _add_escaped_character(token_builder, character):
    escaped_character = _CHARACTER_ESCAPES[character]
    token_builder.add_plain_character(escaped_character)

_CHARACTER_ESCAPES = {
    'n': '\n',
    't': '\t',
    '\'': '\'',
}

def _end_of_source_error(location):
    return TokeniseError(f'Unexpected end-of-source {location}')

class _StringTokenBuilder:

    def __init__(self):
        self._plain_characters = []
        self._parts = []

    def add_plain_character(self, character):
        self._plain_characters.append(character)

    def add_plain_part_if_any(self):
        if self._plain_characters:
            plain_string = ''.join(self._plain_characters)
            self._parts.append(plain_string)
            self._plain_characters.clear()

    def add_expression_escape_part(self, tokens):
        self._parts.append(tokens)        

    def build(self):
        self.add_plain_part_if_any()
        return StringToken(self._parts)

class _Source:

    def __init__(self, source):
        self._source = source
        self._position = 0

    def get_next_character(self, location):
        try:
            head = self._source[self._position]
        except IndexError:
            raise _end_of_source_error(location)
        else:
            self._position += 1
            return head

    def get_next_raw_tokens(self):
        remainder = self._source[self._position:]
        for match in _RAW_TOKEN_RE.finditer(remainder):
            kind = _RawTokenKind[match.lastgroup]
            value = match.group()
            self._position += len(value)
            yield (kind, value)

@dataclass
class _Context:
    bracket_depth: int = 0
