from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import Iterable

from tokenising import *


@dataclass
class BindingSyntax:
    name: str
    value: ExpressionSyntax

class ExpressionSyntax:
    pass

@dataclass
class CallExpressionSyntax(ExpressionSyntax):
    callable_: ExpressionSyntax
    argument: ExpressionSyntax

@dataclass
class IdentifierExpressionSyntax(ExpressionSyntax):
    name: str

@dataclass
class IntegerExpressionSyntax(ExpressionSyntax):
    digits: str

@dataclass
class StringExpressionSyntax(ExpressionSyntax):
    parts: Iterable[str|ExpressionSyntax]

def parse(source):
    token_iterable = tokenise(source)
    tokens = Tokens(token_iterable)
    result = _parse_binding(tokens)
    tokens.expect_end_of_source()
    return result

def _parse_binding(tokens):
    name = tokens.expect(IdentifierToken).name
    tokens.expect(EqualsToken)
    value = _parse_expression(tokens)
    return BindingSyntax(name, value)

def _parse_expression(tokens):
    first = _parse_single_expression(tokens)
    arguments = tokens.zero_or_more(_parse_single_expression)
    return reduce(CallExpressionSyntax, arguments, first)

def _parse_single_expression(tokens):
    return tokens.branch('an expression',
        _parse_integer,
        _parse_identifier,
        _parse_string)

def _parse_integer(tokens):
    integer_token = tokens.expect(IntegerToken)
    return IntegerExpressionSyntax(integer_token.digits)

def _parse_identifier(tokens):
    identifier_token = tokens.expect(IdentifierToken)
    return IdentifierExpressionSyntax(identifier_token.name)

def _parse_string(tokens):
    string_token = tokens.expect(StringToken)
    parts = list(map(_convert_string_token_part, string_token.parts))
    return StringExpressionSyntax(parts)

def _convert_string_token_part(string_token_part):
    match string_token_part:
        case PlainStringTokenPart(contents):
            return contents
        case CharacterEscapeStringTokenPart(escape):
            return _ESCAPE_CHARACTERS[escape]
        case ExpressionEscapeStringTokenPart(tokens):
            return _parse_expression(Tokens(tokens))

_ESCAPE_CHARACTERS = {
    CharacterEscape.NEWLINE: '\n',
    CharacterEscape.TAB: '\t',
}

class ParseError(Exception):
    pass

class Tokens:

    def __init__(self, token_iterable):
        self._tokens = []
        self._position = 0
        self._token_iterator = iter(token_iterable)

    def expect(self, token_type):
        return self._expect(
            lambda token: isinstance(token, token_type),
            lambda: self._describe_token_type(token_type))

    def expect_end_of_source(self):
        return self._expect(
            lambda token: token is _END_OF_SOURCE,
            lambda: _END_OF_SOURCE_DESCRIPTION)

    def _expect(self, predicate, describer):
        token = self._get_next()
        if not predicate(token):
            raise self._error(describer(), token)
        return token

    def branch(self, description, *branches):
        for branch in branches:
            result = self._try(branch)
            if result is not None:
                return result
        raise self._error(description, self._get_next())

    def zero_or_more(self, parser):
        while (result := self._try(parser)) is not None:
            yield result

    def _try(self, parser):
        saved_position = self._position
        try:
            return parser(self)
        except ParseError:
            self._position = saved_position
            return None

    def _get_next(self):
        try:
            token = self._tokens[self._position]
        except IndexError:
            token = next(self._token_iterator, _END_OF_SOURCE)
            self._tokens.append(token)
        self._position += 1
        return token

    def _error(self, description, actual):
        return ParseError(
            f'Expected {description}, got {self._describe_token(actual)}')

    def _describe_token(self, token):
        if token is _END_OF_SOURCE:
            return _END_OF_SOURCE_DESCRIPTION
        return self._describe_token_type(token.__class__)

    def _describe_token_type(self, token_type):
        return _TOKEN_TYPE_DESCRIPTIONS[token_type]

_TOKEN_TYPE_DESCRIPTIONS = {
    IntegerToken: 'an integer',
    IdentifierToken: 'an identifier',
    StringToken: 'a string',
    EqualsToken: 'an equals symbol'
}
_END_OF_SOURCE = object()
_END_OF_SOURCE_DESCRIPTION = 'end of source'

def _main():
    import io
    source = io.StringIO("greet = print 'Hello, \\(name)!'")
    actual = parse(source)
    expected = BindingSyntax(
        'greet',
        CallExpressionSyntax(
            IdentifierExpressionSyntax('print'),
            StringExpressionSyntax([
                'Hello, ',
                IdentifierExpressionSyntax('name'),
                '!'])))
    from pprint import pprint
    pprint(actual)
    assert actual == expected

if __name__ == '__main__':
    _main()