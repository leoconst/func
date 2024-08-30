from __future__ import annotations

from . import types
from .analysed import *


def get_type(expression):
    typer = _Typer()
    return typer.get_type(expression)

class _Typer:

    def __init__(self):
        self._seen_parameters = {}

    def get_type(self, expression):
        match expression:
            case Integer():
                return types.INTEGER
            case String():
                return types.STRING
            case Lambda() as lambda_:
                return self._get_lambda_type(lambda_)
            case Parameter() as parameter:
                return self._get_parameter_type(parameter)
            case Call() as call:
                return self._get_call_type(call)
            case IfElse() as if_else:
                return self._get_if_else_type(if_else)
            case Raw() as raw:
                return raw.type
            case _:
                raise TypeError(f'Cannot get type of expression: {expression}')

    def _get_lambda_type(self, lambda_):
        return_type = self.get_type(lambda_.body)
        name = lambda_.parameter
        parameter_type = self._get_seen_parameter(name)
        if parameter_type is None:
            parameter_type = types.Named(name)
        return types.Callable(parameter_type, return_type)

    def _get_parameter_type(self, parameter):
        type = self._get_seen_parameter(parameter.name)
        if type is None:
            raise TypeError_(f'Undefined parameter: {parameter.name}')
        return type

    def _get_call_type(self, call):
        return self._expect_callable(call.callable_, call.argument)

    def _get_if_else_type(self, if_else):
        self._expect(if_else.condition, 'if-else condition', types.INTEGER)
        if isinstance(if_else.true, Parameter):
            checked_branch, other_branch = if_else.false, if_else.true
        else:
            checked_branch, other_branch = if_else.true, if_else.false
        expected_type = self.get_type(checked_branch)
        self._expect(other_branch, 'both if-else branches', expected_type)
        return expected_type

    def _expect(self, expression, description, expected):
        match expression:
            case Parameter(name=name) if name not in self._seen_parameters:
                self._seen_parameters[name] = expected
            case _:
                actual = self.get_type(expression)
                if actual != expected:
                    raise TypeError_(f'Expected {description} to be of type'
                                     f' {expected}, got {actual}')

    def _expect_callable(self, callable_, argument):
        match callable_:
            case Parameter(name=name) if name not in self._seen_parameters:
                argument_type = self.get_type(argument)
                return_type = types.Named(name)
                callable_type = types.Callable(argument_type, return_type)
                self._seen_parameters[name] = callable_type
                return return_type
            case _:
                actual = self.get_type(callable_)
                if not isinstance(actual, types.Callable):
                    raise TypeError_('Expected expression of a callable type,'
                                    f' got {actual}')
                self._expect(argument, 'call argument', actual.parameter)
                return actual.return_

    def _get_seen_parameter(self, name):
        return self._seen_parameters.get(name, None)

class TypeError_(Exception):
    pass
