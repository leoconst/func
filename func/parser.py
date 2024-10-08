from dataclasses import dataclass
from functools import reduce

from .tokens import ConstantTokenKind, ValueTokenKind
from .syntax import *


def parse(tokens):
    tokens = _Tokens(tokens)
    return _parse_module(tokens)

def parse_binding(tokens):
    tokens = _Tokens(tokens)
    return _parse_binding(tokens)

def parse_expression(tokens):
    tokens = _Tokens(tokens)
    return _parse_expression(tokens)

def _parse_module(tokens):
    bindings = list(_parse_module_bindings(tokens))
    return Module(bindings)

def _parse_module_bindings(tokens):
    first = True
    while tokens.peek() is not _END_OF_SOURCE:
        if not first:
            tokens.expect(ConstantTokenKind.NEWLINE)
        first = False
        yield _parse_binding(tokens)

def _parse_binding(tokens):
    identifier = tokens.expect(ValueTokenKind.IDENTIFIER)
    name = identifier.value
    tokens.expect(ConstantTokenKind.EQUALS)
    value = _parse_expression(tokens)
    return Binding(name, value)

def _parse_expression(tokens):
    branches = {
        ValueTokenKind.INTEGER:
            _accept_integer,
        ValueTokenKind.IDENTIFIER:
            _accept_identifier,
        ConstantTokenKind.STRING_DELIMITER:
            lambda _: _accept_string(tokens),
        ConstantTokenKind.LAMBDA:
            lambda _: _accept_lambda(tokens),
        ConstantTokenKind.IF:
            lambda _: _accept_if_else(tokens),
        ConstantTokenKind.OPEN_BRACKET:
            lambda _: _accept_bracketed_expression(tokens),
    }
    first = tokens.branch(branches, 'an expression')
    arguments = _parse_expression_arguments(tokens, branches)
    return reduce(Call, arguments, first)

def _parse_expression_arguments(tokens, branches):
    while (argument := tokens.try_branch(branches)) is not None:
        yield argument

def _accept_lambda(tokens):
    parameter = tokens.expect(ValueTokenKind.IDENTIFIER).value
    tokens.expect(ConstantTokenKind.ARROW)
    body = _parse_expression(tokens)
    return Lambda(parameter, body)

def _accept_if_else(tokens):
    condition = _parse_expression(tokens)
    tokens.expect(ConstantTokenKind.THEN)
    true = _parse_expression(tokens)
    tokens.expect(ConstantTokenKind.ELSE)
    false = _parse_expression(tokens)
    return IfElse(condition, true, false)

def _accept_bracketed_expression(tokens):
    expression = _parse_expression(tokens)
    tokens.expect(ConstantTokenKind.CLOSE_BRACKET)
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
            case ConstantTokenKind.STRING_DELIMITER:
                return
            case ValueTokenKind.STRING_CONTENT:
                yield token.value
            case ConstantTokenKind.STRING_EXPRESSION_ESCAPE_START:
                yield _accept_string_expression_escape(tokens)
            case _:
                raise TypeError(f'Unexpected token in string: {token}')

def _accept_string_expression_escape(tokens):
    expression = _parse_expression(tokens)
    tokens.expect(ConstantTokenKind.STRING_EXPRESSION_ESCAPE_END)
    return expression

class ParseError(Exception):
    pass

class _Tokens:

    def __init__(self, tokens):
        self._tokens = tokens
        self._next_token = None

    def expect(self, token_kind):
        token = self.get_next()
        if token.kind != token_kind:
            description = _describe_token_kind(token_kind)
            raise _error(description, token)
        return token

    def branch(self, branches, expectation):
        token = self.get_next()
        def fallback():
            raise _error(expectation, token)
        return _try_branch(branches, token, fallback)

    def try_branch(self, branches):
        start_token = self.get_next()
        def fallback():
            self._next_token = start_token
        return _try_branch(branches, start_token, fallback)

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

def _try_branch(branches, token, fallback):
    if (branch := branches.get(token.kind)) is not None:
        return branch(token)
    return fallback()

def _error(description, actual):
    actual_description = _describe_token_kind(actual.kind)
    return ParseError(f'Expected {description}, got {actual_description}')

def _describe_token_kind(token_kind):
    return _TOKEN_KIND_DESCRIPTIONS[token_kind]

class _EndOfSource:
    kind = object()
_END_OF_SOURCE = _EndOfSource()

_TOKEN_KIND_DESCRIPTIONS = {
    ValueTokenKind.IDENTIFIER:
        'an identifier',
    ValueTokenKind.INTEGER:
        'an integer',
    ConstantTokenKind.STRING_DELIMITER:
        'a string',
    ConstantTokenKind.STRING_EXPRESSION_ESCAPE_END:
        'the end of an expression escape',
    ConstantTokenKind.EQUALS:
        'an equals symbol',
    ConstantTokenKind.LAMBDA:
        'the beginning of a lambda',
    ConstantTokenKind.ARROW:
        'an arrow',
    ConstantTokenKind.NEWLINE:
        'a newline',
    ConstantTokenKind.OPEN_BRACKET:
        'an opening bracket',
    ConstantTokenKind.CLOSE_BRACKET:
        'a closing bracket',
    _EndOfSource.kind:
        'end-of-source',
}
