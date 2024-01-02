from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


def tokenise(source):
    source = _Source(source)
    context = _Context()
    return _tokenise_with_context(source, context)

def _tokenise_with_context(source, context):
    tokens = source.get_next_raw_tokens()
    while token := next(tokens, False):
        raw_kind, value = token
        match raw_kind:
            case _RawTokenKind.MISMATCH:
                raise TokeniseError(f'Unexpected character: {value!r}')
            case _RawTokenKind.IGNORED:
                continue
            case _RawTokenKind.OPEN_BRACKET:
                context.bracket_depth += 1
            case _RawTokenKind.CLOSE_BRACKET:
                context.bracket_depth -= 1
        kind = TokenKind[raw_kind.name]
        yield Token(kind, value)
        if kind == TokenKind.STRING_DELIMITER:
            yield from _tokenise_string(source)
            tokens = source.get_next_raw_tokens()

@dataclass
class Token:
    kind: TokenKind
    value: str

class TokenKind(Enum):
    STRING_DELIMITER = auto()
    STRING_CONTENT = auto()
    STRING_EXPRESSION_START = auto()
    STRING_EXPRESSION_END = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    EQUALS = auto()
    LAMBDA = auto()
    ARROW = auto()
    NEWLINE = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()

class TokeniseError(Exception):
    pass

_STRING_DELIMETER = '\''

class _RawTokenKind(Enum):
    STRING_DELIMITER = _STRING_DELIMETER
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
    while (head := source.get_next_character('inside string')) != _STRING_DELIMETER:
        if head == '\\':
            head = source.get_next_character('immediately after string escape')
            if head == '(':
                yield from _add_expression_escape_part(source, content_builder)
            elif head in _CHARACTER_ESCAPES:
                _add_escaped_character(content_builder, head)
            else:
                raise TokeniseError(f'Invalid escape character: {head!r}')
        else:
            content_builder.add_character(head)
    yield from content_builder.token()
    yield Token(TokenKind.STRING_DELIMITER, "'")

def _add_expression_escape_part(source, content_builder):
    yield from content_builder.token()
    yield Token(TokenKind.STRING_EXPRESSION_START, '(')
    yield from _tokenise_until_brackets_balanced(source)
    yield Token(TokenKind.STRING_EXPRESSION_END, ')')

def _tokenise_until_brackets_balanced(source):
    context = _Context(bracket_depth=1)
    for token in _tokenise_with_context(source, context):
        if context.bracket_depth <= 0:
            break
        yield token
    else:
        raise _end_of_source_error('inside expression escape')

def _add_escaped_character(content_builder, character):
    escaped_character = _CHARACTER_ESCAPES[character]
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
