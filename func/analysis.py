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
class Call(Expression):
    callable_: Expression
    argument: Expression

class AnalysisError(Exception):
    pass

def analyse(module):
    bindings = {}
    for binding in module.bindings:
        name = binding.name
        if name in bindings:
            raise AnalysisError(f"Duplicate binding name: '{name}'")
        value = _analyse_expression(binding.value)
        bindings[name] = value
    return Module(bindings)

def _analyse_expression(expression):
    match expression:
        case syntax.Integer(string):
            return Integer(int(string))
        case syntax.String(parts):
            string_parts = list(map(_analyse_string_part, parts))
            return String(string_parts)
        case syntax.Identifier(name):
            return Identifier(name)
        case syntax.Call(callable_, argument):
            return Call(
                _analyse_expression(callable_),
                _analyse_expression(argument))

def _analyse_string_part(part):
    match part:
        case str() as string:
            return string
        case syntax.Expression() as expression:
            return _analyse_expression(expression)
        case _:
            raise TypeError(f'Unknown string part: {part}')
