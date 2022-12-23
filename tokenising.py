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
    if head == STRING_DELIMITER:
        return _tokenise_string(tail)
    if _is_identifier_character(head):
        return _tokenise_identifier(head, tail)
    if _is_integer_character(head):
        return _tokenise_integer(head, tail)
    if head == stoppage_character:
        return (None, tail)
    raise ValueError(f'Invalid character: {head!r}')

def _skip_ignored(source):
    while source and source[0] in _WHITESPACE:
        source = source[1:]
    return source

_WHITESPACE = (' ', '\t')

def _tokenise_string(source):
    parts, tail = _tokenise_string_parts(source)
    return (StringToken(parts), tail)

def _tokenise_string_parts(source):
    plain_characters = []
    parts = []
    def commit_plain_token():
        if plain_characters:
            parts.append(PlainStringTokenPart(''.join(plain_characters)))
            plain_characters.clear()
    while True:
        head, source = _split_first_character(source, 'string')
        if head == STRING_DELIMITER:
            commit_plain_token()
            return (parts, source)    
        if head == '\\':
            commit_plain_token()
            escape_token, source = _tokenise_string_escape(source)
            parts.append(escape_token)
        else:
            plain_characters.append(head)

STRING_DELIMITER = "'"

def _tokenise_string_escape(source):
    head, tail = _split_first_character(source, 'string escape')
    if head == '(':
        tokens, tail = _tokenise_until(
            tail,
            on_end_of_source=_throw_for_end_of_source,
            stoppage_character=_ESCAPE_EXPRESSION_STOPPAGE_CHARACTER)
        return (ExpressionEscapeStringTokenPart(tokens), tail)
    if head in _CHARACTER_ESCAPES:
        return (CharacterEscapeStringTokenPart(_CHARACTER_ESCAPES[head]), tail)
    raise ValueError(f'Invalid escape character: {head!r}')

def _throw_for_end_of_source():
    raise ValueError(f'Unexpected end of source inside escape expression, '
        f'expected {_ESCAPE_EXPRESSION_STOPPAGE_CHARACTER!r}')

_ESCAPE_EXPRESSION_STOPPAGE_CHARACTER = ')'

_CHARACTER_ESCAPES = {
    'n': CharacterEscape.NEWLINE,
    't': CharacterEscape.TAB,
}

def _tokenise_identifier(first, tail):
    return _tokenise_characters_where(
        first,
        tail,
        _is_identifier_character,
        IdentifierToken)

def _is_identifier_character(character):
    return 'a' <= character <= 'z'

def _tokenise_integer(first, tail):
    return _tokenise_characters_where(
        first,
        tail,
        _is_integer_character,
        IntegerToken)

def _is_integer_character(character):
    return '0' <= character <= '9'

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