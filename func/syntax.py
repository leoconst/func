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

@dataclass
class Lambda(Expression):
    parameter: str
    body: Expression

def parse(tokens):
    tokens = Tokens(tokens)
    result = _parse_module(tokens)
    tokens.assert_empty()
    return result

def _parse_module(tokens):
    bindings = list(_parse_module_bindings(tokens))
    return Module(bindings)

def _parse_module_bindings(tokens):
    first = True
    while (next_token := tokens.peek()) is not _END_OF_SOURCE:
        if not first:
            tokens.expect(TokenKind.NEWLINE)
        first = False
        yield _parse_binding(tokens)

def _parse_binding(tokens):
    identifier = tokens.expect(TokenKind.IDENTIFIER)
    name = identifier.value
    tokens.expect(TokenKind.EQUALS)
    value = _parse_expression(tokens)
    return Binding(name, value)

def _parse_expression(tokens):
    branches = {
        TokenKind.INTEGER: _accept_integer,
        TokenKind.IDENTIFIER: _accept_identifier,
        TokenKind.STRING_DELIMITER: lambda _: _accept_string(tokens),
        TokenKind.LAMBDA: lambda _: _accept_lambda(tokens),
        TokenKind.OPEN_BRACKET: lambda _: _accept_bracketed_expression(tokens),
    }
    first = tokens.branch('an expression', branches)
    arguments = []
    while (argument := tokens.try_branch(branches)) is not None:
        arguments.append(argument)
    return reduce(Call, arguments, first)

def _accept_lambda(tokens):
    parameter = tokens.expect(TokenKind.IDENTIFIER).value
    tokens.expect(TokenKind.ARROW)
    body = _parse_expression(tokens)
    return Lambda(parameter, body)

def _accept_bracketed_expression(tokens):
    expression = _parse_expression(tokens)
    tokens.expect(TokenKind.CLOSE_BRACKET)
    return expression

def _accept_integer(integer):
    return Integer(integer.value)

def _accept_identifier(identifier):
    return Identifier(identifier.value)
 
def _accept_string(tokens):
    parts = list(_parse_string_parts(tokens))
    return String(parts)

def _parse_string_parts(tokens):
    while True:
        token = tokens.get_next()
        match token.kind:
            case TokenKind.STRING_DELIMITER:
                return
            case TokenKind.STRING_CONTENT:
                yield token.value
            case TokenKind.OPEN_BRACKET:
                yield _accept_bracketed_expression(tokens)
            case _:
                raise TypeError(
                    f'Unexpected token when parsing string: {token}')

class ParseError(Exception):
    pass

class Tokens:

    def __init__(self, tokens):
        self._tokens = tokens
        self._next_token = None

    def expect(self, token_kind):
        token = self.get_next()
        if token.kind != token_kind:
            description = _describe_token_kind(token_kind)
            raise _error(description, token)
        return token

    def assert_empty(self):
        next_token = self.get_next()
        if next_token is not _END_OF_SOURCE:
            raise RuntimeError(f'Expected no more tokens but got {next_token}')

    def branch(self, description, branches):
        def fallback(next_token):
            raise _error(description, next_token)
        return self._branch_or(branches, fallback)

    def try_branch(self, branches):
        start_token = self.peek()
        def fallback(next_token):
            self._next_token = start_token
            return None
        return self._branch_or(branches, fallback)

    def _branch_or(self, branches, fallback):
        next_token = self.get_next()
        if (branch := branches.get(next_token.kind)) is not None:
            return branch(next_token)
        return fallback(next_token)

    def get_next(self):
        if self._next_token is not None:
            next_token = self._next_token
            self._next_token = None
            return next_token
        return self._get_next_token()

    def peek(self):
        if self._next_token is None:
            self._next_token = self._get_next_token()
        return self._next_token

    def _get_next_token(self):
        return next(self._tokens, _END_OF_SOURCE)

def _error(description, actual):
    actual_description = _describe_token_kind(actual.kind)
    return ParseError(f'Expected {description}, got {actual_description}')

def _describe_token_kind(token_kind):
    return _TOKEN_KIND_DESCRIPTIONS[token_kind]

class _EndOfSource:
    kind = object()
_END_OF_SOURCE = _EndOfSource()

_TOKEN_KIND_DESCRIPTIONS = {
    TokenKind.STRING_DELIMITER: 'a string',
    TokenKind.IDENTIFIER: 'an identifier',
    TokenKind.INTEGER: 'an integer',
    TokenKind.EQUALS: 'an equals symbol',
    TokenKind.LAMBDA: 'the beginning of a lambda',
    TokenKind.ARROW: 'an arrow',
    TokenKind.NEWLINE: 'a newline',
    TokenKind.OPEN_BRACKET: 'an opening bracket',
    TokenKind.CLOSE_BRACKET: 'a closing bracket',
    _EndOfSource.kind: 'end-of-source',
}
