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
    tokens, tail = _tokenise_until(source, on_end_of_source=lambda: None)
    if tail:
        raise ValueError(f'Untokenised tail: {tail!r}')
    return tokens

def _tokenise_until(source, *, on_end_of_source, stoppage_character=None):
    tokens = []
    tail = source
    while True:
        token, tail = _next_token(tail, on_end_of_source, stoppage_character)
        if token is None:
            break
        tokens.append(token)
    return (tokens, tail)

def _next_token(source, on_end_of_source, stoppage_character):
    source = _skip_ignored(source)
    if not source:
        return (on_end_of_source(), source)
    head = source[0]
    tail = source[1:]
    for tokeniser in _TOKENISERS:
        if tokeniser.enter(head):
            return tokeniser.tokenise(head, tail)
    if head == stoppage_character:
        return (None, tail)
    raise ValueError(f'Invalid character: {head!r}')

def _skip_ignored(source):
    while source and source[0] in _WHITESPACE:
        source = source[1:]
    return source

_WHITESPACE = (' ', '\t')

class StringTokeniser:

    def enter(self, character):
        return character == _STRING_DELIMITER

    def tokenise(self, head, tail):
        parts, tail = self._tokenise_parts(tail)
        return (StringToken(parts), tail)

    def _tokenise_parts(self, source):
        plain_characters = []
        parts = []
        def commit_plain_token():
            if plain_characters:
                parts.append(PlainStringTokenPart(''.join(plain_characters)))
                plain_characters.clear()
        while True:
            head, source = _split_first_character(source, 'string')
            if head == _STRING_DELIMITER:
                commit_plain_token()
                return (parts, source)    
            if head == '\\':
                commit_plain_token()
                escape_token, source = self._tokenise_escape(source)
                parts.append(escape_token)
            else:
                plain_characters.append(head)

    def _tokenise_escape(self, source):
        head, tail = _split_first_character(source, 'string escape')
        if head == '(':
            tokens, tail = _tokenise_until(
                tail,
                on_end_of_source=self._throw_for_end_of_source,
                stoppage_character=_ESCAPE_EXPRESSION_STOPPAGE_CHARACTER)
            return (ExpressionEscapeStringTokenPart(tokens), tail)
        if head in _CHARACTER_ESCAPES:
            return (CharacterEscapeStringTokenPart(_CHARACTER_ESCAPES[head]), tail)
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
    characters = [first]
    while tail:
        head = tail[0]
        if not predicate(head):
            break
        characters.append(head)
        tail = tail[1:]
    return (wrapper(''.join(characters)), tail)

def _split_first_character(string, location):
    if not string:
        raise ValueError(f'Unexpected end of source inside {location}')
    return (string[0], string[1:])


def _main():
    source = " \t repeat 3 'Two plus three equals:\\n\\t\\(add\t2 3).'   \t\t"
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