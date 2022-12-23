from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable


class Token:
    pass

@dataclass
class IdentifierToken(Token):
    name: str

@dataclass
class IntegerToken(Token):
    digits: str

@dataclass
class StringToken(Token):
    parts: Iterable[StringTokenPart]

class StringTokenPart:
    pass

@dataclass
class PlainStringTokenPart(StringTokenPart):
    contents: str

@dataclass
class CharacterEscapeStringTokenPart(StringTokenPart):
    escape: CharacterEscape

class CharacterEscape(Enum):
    NEWLINE = auto()
    TAB = auto()

@dataclass
class ExpressionEscapeStringTokenPart(StringTokenPart):
    tokens: Iterable[Token]

def tokenise(source):
    tokens = _tokenise_until(source, on_end_of_source=lambda: None)
    remainder = source.read() 
    if remainder:
        raise ValueError(f'Untokenised tail: {remainder!r}')
    return tokens

def _tokenise_until(source, *, on_end_of_source, stoppage_character=None):
    tokens = []
    while True:
        token = _next_token(source, on_end_of_source, stoppage_character)
        if token is None:
            break
        tokens.append(token)
    return tokens

def _next_token(source, on_end_of_source, stoppage_character):
    source = _skip_ignored(source)
    head = _read_head(source)
    if head is None:
        return on_end_of_source()
    for tokeniser in _TOKENISERS:
        if tokeniser.enter(head):
            return tokeniser.tokenise(head, source)
    if head == stoppage_character:
        return None
    raise ValueError(f'Invalid character: {head!r}')

def _skip_ignored(source):
    _characters_where(source, lambda character: character in _WHITESPACE)
    return source

def _characters_where(source, predicate):
    characters = []
    while True:
        position = source.tell()
        character = _read_head(source)
        if character is None:
            break
        if not predicate(character):
            source.seek(position)
            break
        characters.append(character)
    return ''.join(characters)

_WHITESPACE = (' ', '\t')

class StringTokeniser:

    def enter(self, character):
        return character == _STRING_DELIMITER

    def tokenise(self, head, tail):
        parts = self._tokenise_parts(tail)
        return StringToken(parts)

    def _tokenise_parts(self, source):
        plain_characters = []
        parts = []
        def commit_plain_token():
            if plain_characters:
                parts.append(PlainStringTokenPart(''.join(plain_characters)))
                plain_characters.clear()
        while True:
            head = _read_head_or_raise(source, 'string')
            if head == _STRING_DELIMITER:
                commit_plain_token()
                return parts
            if head == '\\':
                commit_plain_token()
                escape_token = self._tokenise_escape(source)
                parts.append(escape_token)
            else:
                plain_characters.append(head)

    def _tokenise_escape(self, source):
        head = _read_head_or_raise(source, 'string escape')
        if head == '(':
            tokens = _tokenise_until(
                source,
                on_end_of_source=self._throw_for_end_of_source,
                stoppage_character=_ESCAPE_EXPRESSION_STOPPAGE_CHARACTER)
            return ExpressionEscapeStringTokenPart(tokens)
        if head in _CHARACTER_ESCAPES:
            return CharacterEscapeStringTokenPart(_CHARACTER_ESCAPES[head])
        raise ValueError(f'Invalid escape character: {head!r}')

    def _throw_for_end_of_source(self):
        raise ValueError(f'Unexpected end of source inside escape expression, '
            f'expected {_ESCAPE_EXPRESSION_STOPPAGE_CHARACTER!r}')

_STRING_DELIMITER = "'"
_ESCAPE_EXPRESSION_STOPPAGE_CHARACTER = ')'
_CHARACTER_ESCAPES = {
    'n': CharacterEscape.NEWLINE,
    't': CharacterEscape.TAB,
}

class IntegerTokeniser:

    def enter(self, character):
        return self._is_integer_character(character)

    def tokenise(self, head, tail):
        return _tokenise_characters_where(
            head,
            tail,
            self._is_integer_character,
            IntegerToken)

    def _is_integer_character(self, character):
        return '0' <= character <= '9'

class IdentifierTokeniser:

    def enter(self, character):
        return self._is_identifier_character(character)

    def tokenise(self, head, tail):
        return _tokenise_characters_where(
            head,
            tail,
            self._is_identifier_character,
            IdentifierToken)

    def _is_identifier_character(self, character):
        return 'a' <= character <= 'z'

_TOKENISERS = [
    StringTokeniser(),
    IdentifierTokeniser(),
    IntegerTokeniser(),
]

def _tokenise_characters_where(first, tail, predicate, wrapper):
    characters = first + _characters_where(tail, predicate)
    return wrapper(''.join(characters))

def _read_head_or_raise(source, location):
    head = _read_head(source)
    if head is None:
        raise ValueError(f'Unexpected end of source inside {location}')
    return head

def _read_head(source):
    head = source.read(1)
    if not head:
        return None
    return head


def _main():
    import io
    source = io.StringIO(
        " \t repeat 3 'Two plus three equals:\\n\\t\\(add\t2 3).'   \t\t")
    actual = list(tokenise(source))

    expected = [
        IdentifierToken('repeat'),
        IntegerToken('3'),
        StringToken([
            PlainStringTokenPart('Two plus three equals:'),
            CharacterEscapeStringTokenPart(CharacterEscape.NEWLINE),
            CharacterEscapeStringTokenPart(CharacterEscape.TAB),
            ExpressionEscapeStringTokenPart([
                IdentifierToken('add'),
                IntegerToken('2'),
                IntegerToken('3'),
            ]),
            PlainStringTokenPart('.'),
        ]),
    ]
    from pprint import pprint
    pprint(actual)

    assert expected == actual

if __name__ == '__main__':
    _main()