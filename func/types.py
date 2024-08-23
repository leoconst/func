from __future__ import annotations

from dataclasses import dataclass


class Type:
    pass

@dataclass
class Named(Type):
    name: str

    def __str__(self):
        return self.name

@dataclass
class Callable(Type):
    parameter: Type
    return_: Type

    def __str__(self):
        return f'{self.parameter} -> {self.return_}'

INTEGER = Named('Integer')
STRING = Named('String')
UNIT = Named('Unit')
