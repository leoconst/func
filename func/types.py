from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Type:
    name: str

@dataclass
class Callable(Type):
    parameter: Type
    return_: Type

    def __init__(self, parameter, return_):
        super().__init__(f'{parameter.name} -> {return_.name}')
        self.parameter = parameter
        self.return_ = return_

INTEGER = Type('Integer')
STRING = Type('String')
