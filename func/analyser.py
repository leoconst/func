from .analysed import *
from . import syntax

from contextlib import contextmanager


class AnalysisError(Exception):
    pass

def analyse(module, additional_names=()):
    bindings = module.bindings
    scope = _make_scope(bindings, additional_names)
    bindings = {binding.name: _analyse_expression(binding.value, scope)
        for binding in bindings}
    return Module(bindings)

def analyse_expression(expression, additional_names=()):
    scope = _Scope.from_names(additional_names)
    return _analyse_expression(expression, scope)

def _make_scope(bindings, additional_names):
    names = set(additional_names)
    for binding in bindings:
        name = binding.name
        if name in names:
            raise AnalysisError(f"Duplicate binding name: '{name}'")
        names.add(name)
    return _Scope.from_names(names)

def _analyse_expression(expression, scope):
    match expression:
        case syntax.Integer(string):
            return Integer(int(string))
        case syntax.String(parts):
            return _analyse_string(parts, scope)
        case syntax.Identifier(name):
            return _analyse_identifier(name, scope)
        case syntax.Call(callable_, argument):
            return _analyse_call(callable_, argument, scope)
        case syntax.Lambda(parameter, body):
            return _analyse_lambda(parameter, body, scope)
        case syntax.IfElse(condition, true, false):
            return _analyse_if_else(condition, true, false, scope)
        case _:
            raise TypeError(f'Unknown expression: {expression}')

def _analyse_identifier(name, scope):
    if name in scope.parameters:
        return Parameter(name)
    if name in scope.names:
        return Reference(name)
    raise AnalysisError(f"Unbound name: '{name}'")

def _analyse_call(callable_, argument, scope):
    return Call(
        _analyse_expression(callable_, scope),
        _analyse_expression(argument, scope))

def _analyse_lambda(parameter, body, scope):
    with scope.add_parameter(parameter):
        return Lambda(parameter, _analyse_expression(body, scope))

def _analyse_if_else(condition, true, false, scope):
    return IfElse(
        _analyse_expression(condition, scope),
        _analyse_expression(true, scope),
        _analyse_expression(false, scope))

def _analyse_string(parts, scope):
    parts = list(map(lambda part: _analyse_string_part(part, scope), parts))
    return String(parts)

def _analyse_string_part(part, scope):
    match part:
        case str() as string:
            return string
        case syntax.Expression() as expression:
            return _analyse_expression(expression, scope)
        case _:
            raise TypeError(f'Unknown string part: {part}')

@dataclass
class _Scope:
    names: set[str]
    parameters: set[str]

    @classmethod
    def from_names(cls, names):
        return cls(set(names), set())

    @contextmanager
    def add_parameter(self, name):
        try:
            self.parameters.add(name)
            yield
        finally:
            self.parameters.remove(name)
