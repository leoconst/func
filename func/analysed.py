from __future__ import annotations

from dataclasses import dataclass

from .types import Type
from .opcodes import Opcode


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

@dataclass
class Raw(Expression):
    type: Type
    opcodes: list[Opcode]
