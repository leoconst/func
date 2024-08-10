from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import Any, Callable, Iterator

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

@dataclass
class IfElse(Expression):
    condition: Expression
    true: Expression
    false: Expression

def parse(tokens: Iterator[Token]) -> Module:
    wrapped_tokens = Tokens(tokens)
    return _parse_module(wrapped_tokens)

def _parse_module(tokens: Tokens) -> Module:
    bindings = list(_parse_module_bindings(tokens))
    return Module(bindings)

def _parse_module_bindings(tokens: Tokens) -> Iterator[Binding]:
    first = True
    while tokens.peek() is not _END_OF_SOURCE:
        if not first:
            tokens.expect(TokenKind.NEWLINE)
        first = False
        yield _parse_binding(tokens)

def _parse_binding(tokens: Tokens) -> Binding:
    identifier = tokens.expect(TokenKind.IDENTIFIER)
    name = identifier.value
    tokens.expect(TokenKind.EQUALS)
    value = _parse_expression(tokens)
    return Binding(name, value)

def _parse_expression(tokens: Tokens) -> Expression:
    branches: _Branches[Expression] = {
        TokenKind.INTEGER: _accept_integer,
        TokenKind.IDENTIFIER: _accept_identifier,
        TokenKind.STRING_DELIMITER: lambda _: _accept_string(tokens),
        TokenKind.LAMBDA: lambda _: _accept_lambda(tokens),
        TokenKind.IF: lambda _: _accept_if_else(tokens),
        TokenKind.OPEN_BRACKET: lambda _: _accept_bracketed_expression(tokens),
    }
    first = tokens.branch(branches, 'an expression')
    arguments = _parse_expression_arguments(tokens, branches)
    return reduce(Call, arguments, first)

def _parse_expression_arguments(
        tokens: Tokens,
        branches: _Branches[Expression]) -> Iterator[Expression]:
    while (argument := tokens.try_branch(branches)) is not None:
        yield argument

def _accept_lambda(tokens: Tokens) -> Lambda:
    parameter = tokens.expect(TokenKind.IDENTIFIER).value
    tokens.expect(TokenKind.ARROW)
    body = _parse_expression(tokens)
    return Lambda(parameter, body)

def _accept_if_else(tokens: Tokens) -> IfElse:
    condition = _parse_expression(tokens)
    tokens.expect(TokenKind.THEN)
    true = _parse_expression(tokens)
    tokens.expect(TokenKind.ELSE)
    false = _parse_expression(tokens)
    return IfElse(condition, true, false)

def _accept_bracketed_expression(tokens: Tokens) -> Expression:
    expression = _parse_expression(tokens)
    tokens.expect(TokenKind.CLOSE_BRACKET)
    return expression

def _accept_integer(integer: _NextToken) -> Integer:
    return Integer(integer.value)

def _accept_identifier(identifier: _NextToken) -> Identifier:
    return Identifier(identifier.value)
 
def _accept_string(tokens: Tokens) -> String:
    parts = list(_parse_string_parts(tokens))
    return String(parts)

def _parse_string_parts(tokens: Tokens) -> Iterator[str|Expression]:
    while True:
        token = tokens.get_next()
        match token.kind:
            case TokenKind.STRING_DELIMITER:
                return
            case TokenKind.STRING_CONTENT:
                yield token.value  # type: ignore[union-attr]
            case TokenKind.STRING_EXPRESSION_ESCAPE_START:
                yield _accept_string_expression_escape(tokens)
            case _:
                raise TypeError(f'Unexpected token in string: {token}')

def _accept_string_expression_escape(tokens: Tokens) -> Expression:
    expression = _parse_expression(tokens)
    tokens.expect(TokenKind.STRING_EXPRESSION_ESCAPE_END)
    return expression

class ParseError(Exception):
    pass

class Tokens:

    def __init__(self, tokens: Iterator[Token]) -> None:
        self._tokens = tokens
        self._next_token: _NextToken|None = None

    def expect(self, token_kind: TokenKind) -> Token:
        token = self.get_next()
        if token.kind != token_kind:
            description = _describe_token_kind(token_kind)
            raise _error(description, token)
        return token  # type: ignore[return-value]

    def branch[T](self, branches: _Branches[T], expectation: str) -> T:
        token = self.get_next()
        def fallback() -> T:
            raise _error(expectation, token)
        return _try_branch(branches, token, fallback)

    def try_branch[T](self, branches: _Branches[T]) -> T:
        start_token = self.get_next()
        def fallback() -> T:  # type: ignore[return]
            self._next_token = start_token
        return _try_branch(branches, start_token, fallback)

    def get_next(self) -> _NextToken:
        if self._next_token is not None:
            next_token = self._next_token
            self._next_token = None
            return next_token
        return self._get_next_token()

    def peek(self) -> _NextToken:
        if self._next_token is None:
            self._next_token = self._get_next_token()
        return self._next_token

    def _get_next_token(self) -> Token|_EndOfSource:
        return next(self._tokens, _END_OF_SOURCE)

type _NextToken = Token|_EndOfSource
type _Branches[T] = dict[TokenKind|_EndOfSourceKind, Callable[[_NextToken], T]]

def _try_branch[T](
        branches: _Branches[T],
        token: _NextToken,
        fallback: Callable[[], T]) -> T:
    if (branch := branches.get(token.kind)) is not None:
        return branch(token)
    return fallback()

def _error(description: str, actual: _NextToken) -> ParseError:
    actual_description = _describe_token_kind(actual.kind)
    return ParseError(f'Expected {description}, got {actual_description}')

def _describe_token_kind(token_kind: TokenKind|_EndOfSourceKind) -> str:
    return _TOKEN_KIND_DESCRIPTIONS[token_kind]

class _EndOfSourceKind:
    pass
class _EndOfSource:
    kind = _EndOfSourceKind()
_END_OF_SOURCE = _EndOfSource()

_TOKEN_KIND_DESCRIPTIONS = {
    TokenKind.STRING_DELIMITER: 'a string',
    TokenKind.STRING_EXPRESSION_ESCAPE_END: 'the end of an expression escape',
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
