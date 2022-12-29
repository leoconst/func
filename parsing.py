from __future__ import annotations

from dataclasses import dataclass
from functools import reduce

from tokenising import *


@dataclass
class ModuleSyntax:
    bindings: list[BindingSyntax]

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
    parts: list[str|ExpressionSyntax]

def parse(source):
    token_iterable = tokenise(source)
    tokens = Tokens(token_iterable)
    result = _parse_module(tokens)
    tokens.expect_end_of_source()
    return result

def _parse_module(tokens):
    bindings = tokens.separated(
        lambda tokens: tokens.expect(TokenKind.NEWLINE),
        _parse_binding)
    return ModuleSyntax(list(bindings))

def _parse_binding(tokens):
    name = tokens.expect(TokenKind.IDENTIFIER).value
    tokens.expect(TokenKind.EQUALS)
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
    integer_token = tokens.expect(TokenKind.INTEGER)
    return IntegerExpressionSyntax(integer_token.value)

def _parse_identifier(tokens):
    identifier_token = tokens.expect(TokenKind.IDENTIFIER)
    return IdentifierExpressionSyntax(identifier_token.value)
 
def _parse_string(tokens):
    string = tokens.expect(TokenKind.STRING)
    parts = list(map(_parse_string_part, string.parts))
    return StringExpressionSyntax(parts)

def _parse_string_part(part):
    match part:
        case str() as string:
            return string
        case list() as tokens:
            return _parse_expression(Tokens(tokens))
        case _:
            raise TypeError(f'Unknown string part: {part}')

class ParseError(Exception):
    pass

class Tokens:

    def __init__(self, token_iterable):
        self._tokens = []
        self._position = 0
        self._token_iterator = iter(token_iterable)

    def expect(self, token_kind):
        return self._expect(
            lambda token: (token is not _END_OF_SOURCE
                and token.kind == token_kind),
            lambda: self._describe_token_kind(token_kind))

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

    def separated(self, separator, item):
        first = self._try(item)
        if first is None:
            return
        yield first
        def parse_tail(tokens):
            separator(tokens)
            return item(tokens)
        yield from self.zero_or_more(parse_tail)

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
        return f'{self._describe_token_kind(token.kind)}'

    def _describe_token_kind(self, token_kind):
        return _TOKEN_KIND_DESCRIPTIONS[token_kind]

_TOKEN_KIND_DESCRIPTIONS = {
    TokenKind.STRING: 'a string',
    TokenKind.INTEGER: 'an integer',
    TokenKind.IDENTIFIER: 'an identifier',
    TokenKind.EQUALS: 'an equals symbol',
    TokenKind.NEWLINE: 'a newline',
}
_END_OF_SOURCE = object()
_END_OF_SOURCE_DESCRIPTION = 'end of source'

def _main():
    source = "name = 'World'\ngreet = print 'Hello, \\(name)!'"
    actual = parse(source)
    expected = ModuleSyntax([
        BindingSyntax(
            'name',
            StringExpressionSyntax([
                'World',
            ])
        ),
        BindingSyntax(
            'greet',
            CallExpressionSyntax(
                IdentifierExpressionSyntax('print'),
                StringExpressionSyntax([
                    'Hello, ',
                    IdentifierExpressionSyntax('name'),
                    '!',
                ])
            )
        ),
    ])
    from pprint import pprint
    pprint(actual)
    assert actual == expected

if __name__ == '__main__':
    _main()