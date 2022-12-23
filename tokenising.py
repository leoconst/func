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

@dataclass
class EqualsToken(Token):
    pass

def tokenise(source):
    yield from _tokenise_until(source, on_end_of_source=lambda: None)
    remainder = source.read() 
    if remainder:
        raise ValueError(f'Untokenised tail: {remainder!r}')

def _tokenise_until(source, *, on_end_of_source, stoppage_character=None):
    while ((token := _next_token(source, on_end_of_source, stoppage_character))
            is not None):
        yield token

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

class EqualsTokeniser:

    @staticmethod
    def enter(character):
        return character == '='

    @staticmethod
    def tokenise(head, tail):
        return EqualsToken()

class StringTokeniser:

    def enter(self, character):
        return character == _STRING_DELIMITER

    def tokenise(self, head, tail):
        parts = list(self._tokenise_parts(tail))
        return StringToken(parts)

    def _tokenise_parts(self, source):
        plain_characters = []
        def zero_or_one_plain_token():
            if plain_characters:
                plain_string = ''.join(plain_characters)
                yield PlainStringTokenPart(plain_string)
                plain_characters.clear()
        while True:
            head = _read_head_or_raise(source, 'string')
            if head == _STRING_DELIMITER:
                yield from zero_or_one_plain_token()
                return
            if head == '\\':
                yield from zero_or_one_plain_token()
                yield self._tokenise_escape(source)
            else:
                plain_characters.append(head)

    def _tokenise_escape(self, source):
        head = _read_head_or_raise(source, 'string escape')
        if head == '(':
            tokens = _tokenise_until(
                source,
                on_end_of_source=self._throw_for_end_of_source,
                stoppage_character=_ESCAPE_EXPRESSION_STOPPAGE_CHARACTER)
            token_list = list(tokens)
            return ExpressionEscapeStringTokenPart(token_list)
        if head in _CHARACTER_ESCAPES:
            return CharacterEscapeStringTokenPart(_CHARACTER_ESCAPES[head])
        raise ValueError(f'Invalid escape character: {head!r}')

    def _throw_for_end_of_source(self):
        raise ValueError('Unexpected end of source inside escape expression, '
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
        return self._is_letter_or_underscore(character)

    def tokenise(self, head, tail):
        return _tokenise_characters_where(
            head,
            tail,
            self._is_letter_or_underscore,
            IdentifierToken)

    def _is_letter_or_underscore(self, character):
        return ('a' <= character <= 'z'
            or 'A' <= character <= 'Z'
            or character == '_')

    def _is_identifier_tail_character(self, character):
        return (self._is_letter_or_underscore(character)
            or '0' <= character <= '9')

_TOKENISERS = [
    EqualsTokeniser,
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
    assert actual == expected

if __name__ == '__main__':
    _main()