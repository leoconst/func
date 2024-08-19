from __future__ import annotations

from dataclasses import dataclass


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
