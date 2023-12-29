from __future__ import annotations

from dataclasses import dataclass
from functools import reduce

from .tokenising import *


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

def parse(tokens):
    tokens = Tokens(tokens)
    result = _parse_module(tokens)
    tokens.expect_end_of_source()
    return result

def _parse_module(tokens):
    bindings = []
    first = True
    while tokens.peek() is not _END_OF_SOURCE:
        if not first:
            tokens.expect(TokenKind.NEWLINE)
        first = False
        binding = _parse_binding(tokens)
        bindings.append(binding)
    return ModuleSyntax(bindings)

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
    return tokens.branch('an expression', {
        TokenKind.INTEGER: _parse_integer,
        TokenKind.IDENTIFIER: _parse_identifier,
        TokenKind.STRING: _parse_string,
        TokenKind.OPEN_BRACKET: _parse_bracketed_expression,
    })

def _parse_bracketed_expression(tokens, _):
    expression = _parse_expression(tokens)
    tokens.expect(TokenKind.CLOSE_BRACKET)
    return expression

def _parse_integer(tokens, integer):
    return IntegerExpressionSyntax(integer.value)

def _parse_identifier(tokens, identifier):
    return IdentifierExpressionSyntax(identifier.value)
 
def _parse_string(tokens, string):
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
        self._expect(
            lambda token: token is _END_OF_SOURCE,
            lambda: _END_OF_SOURCE_DESCRIPTION)

    def _expect(self, predicate, describer):
        token = self._get_next()
        if not predicate(token):
            raise self._error(describer(), token)
        return token

    def branch(self, description, branches):
        next_token = self._get_next()
        if next_token is not _END_OF_SOURCE:
            if (branch := branches.get(next_token.kind)) is not None:
                return branch(self, next_token)
        raise self._error(description, next_token)

    def zero_or_more(self, parser):
        while (result := self._try(parser)) is not None:
            yield result

    def peek(self):
        try:
            token = self._tokens[self._position]
        except IndexError:
            token = next(self._token_iterator, _END_OF_SOURCE)
            self._tokens.append(token)
        return token

    def _try(self, parser):
        saved_position = self._position
        try:
            return parser(self)
        except ParseError:
            self._position = saved_position
            return None

    def _get_next(self):
        token = self.peek()
        self._position += 1
        return token

    def _error(self, description, actual):
        return ParseError(
            f'Expected {description}, got {self._describe_token(actual)}')

    def _describe_token(self, token):
        if token is _END_OF_SOURCE:
            return _END_OF_SOURCE_DESCRIPTION
        return self._describe_token_kind(token.kind)

    def _describe_token_kind(self, token_kind):
        return _TOKEN_KIND_DESCRIPTIONS[token_kind]

_TOKEN_KIND_DESCRIPTIONS = {
    TokenKind.STRING: 'a string',
    TokenKind.IDENTIFIER: 'an identifier',
    TokenKind.INTEGER: 'an integer',
    TokenKind.EQUALS: 'an equals symbol',
    TokenKind.NEWLINE: 'a newline',
    TokenKind.OPEN_BRACKET: 'an opening bracket',
    TokenKind.CLOSE_BRACKET: 'a closing bracket',
}
_END_OF_SOURCE = object()
_END_OF_SOURCE_DESCRIPTION = 'end-of-source'
