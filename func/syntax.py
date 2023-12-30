from __future__ import annotations

from dataclasses import dataclass
from functools import reduce

from .tokens import *


@dataclass
class Module:
    bindings: list[Binding]

@dataclass
class Binding:
    name: str
    value: Expression

class Expression:
    pass

@dataclass
class Call(Expression):
    callable_: Expression
    argument: Expression

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Integer(Expression):
    digits: str

@dataclass
class String(Expression):
    parts: list[str|Expression]

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
    return Module(bindings)

def _parse_binding(tokens):
    name = tokens.expect(TokenKind.IDENTIFIER).value
    tokens.expect(TokenKind.EQUALS)
    value = _parse_expression(tokens)
    return Binding(name, value)

def _parse_expression(tokens):
    branches = {
        TokenKind.INTEGER: _accept_integer,
        TokenKind.IDENTIFIER: _accept_identifier,
        TokenKind.STRING: _accept_string,
        TokenKind.OPEN_BRACKET: lambda _: _accept_bracketed_expression(tokens),
    }
    first = tokens.branch('an expression', branches)
    arguments = []
    while (argument := tokens.try_branch(branches)) is not None:
        arguments.append(argument)
    return reduce(Call, arguments, first)

def _accept_bracketed_expression(tokens):
    expression = _parse_expression(tokens)
    tokens.expect(TokenKind.CLOSE_BRACKET)
    return expression

def _accept_integer(integer):
    return Integer(integer.value)

def _accept_identifier(identifier):
    return Identifier(identifier.value)
 
def _accept_string(string):
    parts = list(map(_parse_string_part, string.parts))
    return String(parts)

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
        def fallback(next_token):
            raise self._error(description, next_token)
        return self._branch_or(branches, fallback)

    def try_branch(self, branches):
        def fallback(next_token):
            self._position -= 1
            return None
        return self._branch_or(branches, fallback)

    def _branch_or(self, branches, fallback):
        next_token = self._get_next()
        if next_token is not _END_OF_SOURCE:
            if (branch := branches.get(next_token.kind)) is not None:
                return branch(next_token)
        return fallback(next_token)

    def peek(self):
        try:
            token = self._tokens[self._position]
        except IndexError:
            token = next(self._token_iterator, _END_OF_SOURCE)
            self._tokens.append(token)
        return token

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
