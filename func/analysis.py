from __future__ import annotations

from dataclasses import dataclass

from . import syntax


@dataclass
class Module:
    bindings: dict[str, Expression]

class Expression:
    pass

@dataclass
class Integer(Expression):
    value: int

@dataclass
class String(Expression):
    parts: list[str|Expression]

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Lambda(Expression):
    parameter: str
    body: Expression

@dataclass
class Call(Expression):
    callable_: Expression
    argument: Expression

@dataclass
class IfElse(Expression):
    condition: Expression
    true: Expression
    false: Expression

class AnalysisError(Exception):
    pass

def analyse(module, additional_names=()):
    bindings = module.bindings
    names = _analyse_names(bindings, additional_names)
    bindings = {binding.name: _analyse_expression(binding.value, names)
        for binding in bindings}
    return Module(bindings)

def _analyse_names(bindings, additional_names):
    names = set(additional_names)
    for binding in bindings:
        name = binding.name
        if name in names:
            raise AnalysisError(f"Duplicate binding name: '{name}'")
        names.add(name)
    return names

def _analyse_expression(expression, names):
    match expression:
        case syntax.Integer(string):
            return Integer(int(string))
        case syntax.String(parts):
            return _analyse_string(parts, names)
        case syntax.Identifier(name):
            return _analyse_identifier(name, names)
        case syntax.Call(callable_, argument):
            return _analyse_call(callable_, argument, names)
        case syntax.Lambda(parameter, body):
            return _analyse_lambda(parameter, body, names)
        case syntax.IfElse(condition, true, false):
            return _analyse_if_else(condition, true, false, names)
        case _:
            raise TypeError(f"Unknown expression: {expression}")

def _analyse_identifier(name, names):
    if name not in names:
        raise AnalysisError(f"Unbound name: '{name}'")
    return Identifier(name)

def _analyse_call(callable_, argument, names):
    return Call(
        _analyse_expression(callable_, names),
        _analyse_expression(argument, names))

def _analyse_lambda(parameter, body, names):
    all_names = {parameter, *names}
    return Lambda(parameter, _analyse_expression(body, all_names))

def _analyse_if_else(condition, true, false, names):
    return IfElse(
        _analyse_expression(condition, names),
        _analyse_expression(true, names),
        _analyse_expression(false, names))

def _analyse_string(parts, names):
    parts = list(map(lambda part: _analyse_string_part(part, names), parts))
    return String(parts)

def _analyse_string_part(part, names):
    match part:
        case str() as string:
            return string
        case syntax.Expression() as expression:
            return _analyse_expression(expression, names)
        case _:
            raise TypeError(f'Unknown string part: {part}')