from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


def tokenise(source):
    return _tokenise_with_context(_Source(source), _Context())

def _tokenise_with_context(source, context):
    for raw_kind, value in _get_raw_tokens(source):
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

def _get_raw_tokens(source):
    for match in source.finditer_tail(_RAW_TOKEN_RE):
        kind = _RawTokenKind[match.lastgroup]
        value = match.group()
        yield (kind, value)

def _tokenise_string(source):
    string_tokeniser = _StringTokeniser(source)
    return string_tokeniser.tokenise()

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

class _StringTokeniser:

    def __init__(self, source):
        self._source = source
        self._plain_characters = []
        self._parts = []

    def tokenise(self):
        while True:
            head = self._read_head('inside string')
            if head == _STRING_DELIMETER:
                return self._complete_token()
            if head == '\\':
                self._tokenise_escape()
            else:
                self._add_plain_character(head)

    def _complete_token(self):
        self._add_plain_part_if_any()
        return StringToken(self._parts)

    def _tokenise_escape(self):
        head = self._read_head('immediately after string escape')
        if head == '(':
            self._add_expression_escape_tokens_part()
        elif head in _CHARACTER_ESCAPES:
            self._add_escaped_character(head)
        else:
            raise TokeniseError(f'Invalid escape character: {head!r}')

    def _add_expression_escape_tokens_part(self):
        self._add_plain_part_if_any()
        tokens = []
        context = _Context(bracket_depth=1)
        for token in _tokenise_with_context(self._source, context):
            if context.bracket_depth <= 0:
                break
            tokens.append(token)
        else:
            raise _end_of_source_error('inside escape expression')
        self._parts.append(tokens)

    def _add_escaped_character(self, character):
        escaped_character = _CHARACTER_ESCAPES[character]
        self._add_plain_character(escaped_character)

    def _add_plain_character(self, character):
        self._plain_characters.append(character)

    def _add_plain_part_if_any(self):
        if self._plain_characters:
            plain_string = ''.join(self._plain_characters)
            self._parts.append(plain_string)
            self._plain_characters.clear()

    def _read_head(self, location):
        return self._source.get_next(location)

def _end_of_source_error(location):
    return TokeniseError(f'Unexpected end of source {location}')

_CHARACTER_ESCAPES = {
    'n': '\n',
    't': '\t',
    '\'': '\'',
}

class _Source:

    def __init__(self, source):
        self._source = source
        self._position = 0

    def get_next(self, location):
        try:
            head = self._source[self._position]
        except IndexError:
            raise _end_of_source_error(location)
        else:
            self._position += 1
            return head

    def finditer_tail(self, pattern):
        tail = self._source[self._position:]
        for match in pattern.finditer(tail):
            self._position += len(match.group())
            yield match

@dataclass
class _Context:
    bracket_depth: int = 0


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
