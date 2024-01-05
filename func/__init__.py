from .runtime import execute
from .compiler import compile_, BUILTINS
from .analysis import analyse
from .syntax import parse
from .tokens import tokenise


def run(source):
    tokens = tokenise(source)
    syntax = parse(tokens)
    module = analyse(syntax, BUILTINS)
    program = compile_(module)
    execute(program)
