from .runtime import execute
from .compiler import compile_, BUILTINS
from .analysed import Expression, Module
from .analyser import analyse_expression
from .parser import parse_binding, parse_expression, ParseError
from .tokeniser import tokenise, TokeniseError


def repl():
    bindings = BUILTINS.copy()
    while (line := _get_next_line()) is not None:
        try:
            match _process_line(line, bindings):
                case (name, value):
                    bindings[name] = value
                case Expression() as expression:
                    _execute(expression, bindings)
                case other:
                    raise TypeError(f'Unknown: {other}')
        except Exception as exception:
            print(f'Error: {exception}')

def _get_next_line():
    try:
        return input('>>> ')
    except KeyboardInterrupt:
        return None

def _process_line(line, bindings):
    tokens = list(tokenise(line))
    try:
        syntax_binding = parse_binding(iter(tokens))
    except ParseError:
        syntax_expression = parse_expression(iter(tokens))
        return analyse_expression(syntax_expression, bindings)
    else:
        name = syntax_binding.name
        value = analyse_expression(syntax_binding.value, bindings)
        return (name, value)

def _execute(main, bindings):
    module = Module({'main': main, **bindings})
    program = compile_(module)
    execute(program)
