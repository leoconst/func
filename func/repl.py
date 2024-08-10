from .runtime import execute
from .compiler import compile_, BUILTINS
from .analysis import analyse
from .syntax import parse_binding, parse_expression, ParseError, Binding, Module
from .tokens import tokenise, TokeniseError


def repl():
    bindings = []

    while True:
        try:
            line = input('>>> ')
        except KeyboardInterrupt:
            return

        try:
            tokens = list(tokenise(line))

            try:
                binding = parse_binding(iter(tokens))
            except ParseError:
                expression = parse_expression(iter(tokens))
                main = Binding('main', expression)
                module = Module([main, *bindings])
                analysed = analyse(module, BUILTINS)
                program = compile_(analysed)
                execute(program)
            else:
                bindings.append(binding)

        except Exception as exception:
            print(f'Error: {exception}')
