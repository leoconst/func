from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


def tokenise(source):
    return _tokenise_with_position(source, _PositionContext(source))

def _tokenise_with_position(source, position):
    while True:
        for kind, value, end in _get_raw_tokens(source):
            if kind == _RawTokenKind.STRING_DELIMITER:
                string_tokeniser = _StringTokeniser(source[end:])
                string_token, source = string_tokeniser.tokenise()
                position.tail = source
                yield string_token
                break
            plain_token = _plain_token_from_raw(kind, value)
            if plain_token is not None:
                position.tail = source[end:]
                yield plain_token
        else:
            # There are no more tokens
            return

def _get_raw_tokens(source):
    for match in _RAW_TOKEN_RE.finditer(source):
        kind = _RawTokenKind[match.lastgroup]
        value = match.group()
        end = match.end()
        yield (kind, value, end)

def _plain_token_from_raw(raw_kind, value):
    match raw_kind:
        case _RawTokenKind.MISMATCH:
            raise TokeniseError(f'Unexpected character: {value!r}')
        case _RawTokenKind.IGNORED:
            return
        case other:
            return PlainToken(TokenKind[other.name], value)

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

@dataclass
class _PositionContext:
    tail: str

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

class _StringTokeniser:

    def __init__(self, source):
        self._source = source
        self._plain_characters = []
        self._parts = []

    def tokenise(self):
        while True:
            head = self._split_head('inside string')
            if head == _STRING_DELIMETER:
                return self._complete_token()
            if head == '\\':
                self._tokenise_escape()
            else:
                self._add_plain_character(head)

    def _complete_token(self):
        self._add_plain_part_if_any()
        string_token = StringToken(self._parts)
        return (string_token, self._source)

    def _tokenise_escape(self):
        head = self._split_head('immediately after string escape')
        if head == '(':
            self._add_expression_escape_tokens_part()
        elif head in _CHARACTER_ESCAPES:
            self._add_escaped_character(head)
        else:
            raise TokeniseError(f'Invalid escape character: {head!r}')

    def _add_expression_escape_tokens_part(self):
        self._add_plain_part_if_any()
        source = self._source
        tokens = []
        position = _PositionContext(source)
        for token in _tokenise_with_position(source, position):
            if token.kind == TokenKind.CLOSE_BRACKET:
                break
            tokens.append(token)
        else:
            raise self._end_of_source_error('inside escape expression')
        self._source = position.tail
        self._parts.append(tokens)

    def _add_escaped_character(self, character):
        escaped_character = _CHARACTER_ESCAPES[character]
        self._add_plain_character(escaped_character)

    def _add_plain_character(self, character):
        self._plain_characters.append(character)

    def _add_plain_part_if_any(self):
        plain_string = ''.join(self._plain_characters)
        self._parts.append(plain_string)
        self._plain_characters.clear()

    def _split_head(self, location):
        source = self._source
        if not source:
            raise self._end_of_source_error(location)
        self._source = source[1:]
        return source[0]

    def _end_of_source_error(self, location):
        return TokeniseError(f'Unexpected end of source {location}')

_CHARACTER_ESCAPES = {
    'n': '\n',
    't': '\t',
    '\'': '\'',
}


def _main():
    source = (" \t repeat 3 '\\'Two plus three\\' equals:"
        "\\n\\t\\(add\t2 '3').'  \r\n\n= \t")
    actual = list(tokenise(source))
    expected = [
        PlainToken(TokenKind.IDENTIFIER, 'repeat'),
        PlainToken(TokenKind.INTEGER, '3'),
        StringToken([
            '\'Two plus three\' equals:\n\t',
            [
                PlainToken(TokenKind.IDENTIFIER, 'add'),
                PlainToken(TokenKind.INTEGER, '2'),
                StringToken([
                    '3',
                ]),
            ],
            '.'
        ]),
        PlainToken(TokenKind.NEWLINE, '\r\n'),
        PlainToken(TokenKind.NEWLINE, '\n'),
        PlainToken(TokenKind.EQUALS, '='),
    ]
    from pprint import pprint
    pprint(list(zip(actual, expected)))
    assert actual == expected

if __name__ == '__main__':
    _main()