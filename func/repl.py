from .runtime import execute
from .compiler import compile_, BUILTINS
from .analysis import analyse, Module as Module, analyse_expression
from .syntax import parse_binding, parse_expression, ParseError
from .tokens import tokenise, TokeniseError


def repl():
    bindings = dict(BUILTINS)

    def analyse_new_expression(expression):
        return analyse_expression(expression, bindings)

    while True:
        try:
            line = input('>>> ')
        except KeyboardInterrupt:
            return

        try:
            tokens = list(tokenise(line))

            try:
                syntax_binding = parse_binding(iter(tokens))
            except ParseError:
                syntax_expression = parse_expression(iter(tokens))
                analysed_expression = analyse_new_expression(syntax_expression)
                module = Module({'main': analysed_expression, **bindings})
                program = compile_(module)
                execute(program)
            else:
                analysed_value = analyse_new_expression(syntax_binding.value)
                bindings[syntax_binding.name] = analysed_value

        except Exception as exception:
            print(f'Error: {exception}')
