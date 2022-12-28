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
                string_token, source = _tokenise_string(source[end:])
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
    contents: list[str|list[Token]]

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

def _tokenise_string(source):
    contents, source = _tokenise_string_contents(source)
    return (StringToken(contents), source)

def _tokenise_string_contents(source):
    plain_characters = []
    contents = []
    def maybe_commit_plain_token():
        if plain_characters:
            plain_string = ''.join(plain_characters)
            contents.append(plain_string)
            plain_characters.clear()
    while True:
        head_and_tail = _read_head_or_raise(source, 'string')
        head, source = head_and_tail
        if head == _STRING_DELIMETER:
            maybe_commit_plain_token()
            return (contents, source)
        if head == '\\':
            maybe_commit_plain_token()
            escaped, source = _tokenise_escape(source)
            contents.append(escaped)
        else:
            plain_characters.append(head)

def _tokenise_escape(source):
    head, source = _read_head_or_raise(source, 'string escape')
    if head == '(':
        return _tokenise_expression_escape(source)
    if head in _CHARACTER_ESCAPES:
        return (_CHARACTER_ESCAPES[head], source)
    raise ValueError(f'Invalid escape character: {head!r}')

_CHARACTER_ESCAPES = {
    'n': '\n',
    't': '\t',
    '\'': '\'',
}

def _tokenise_expression_escape(source):
    tokens = []
    position = _PositionContext(source)
    for token in _tokenise_with_position(source, position):
        if token.kind == TokenKind.CLOSE_BRACKET:
            break
        tokens.append(token)
    else:
        raise TokeniseError(
            'Unexpected end of string while parsing escape expression')
    return (tokens, position.tail)

def _read_head_or_raise(source, location):
    head_and_tail = _read_head(source)
    if head_and_tail is None:
        raise TokeniseError(f'Unexpected end of source inside {location}')
    return head_and_tail

def _read_head(source):
    if not source:
        return None
    return (source[0], source[1:])


def _main():
    source = " \t repeat 3 '\\'Two plus three\\' equals:\\n\\t\\(add\t2 '3').'  \r\n\n= \t"
    actual = list(tokenise(source))
    expected = [
        PlainToken(TokenKind.IDENTIFIER, 'repeat'),
        PlainToken(TokenKind.INTEGER, '3'),
        StringToken([
            '\'',
            'Two plus three',
            '\'',
            ' equals:',
            '\n',
            '\t',
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