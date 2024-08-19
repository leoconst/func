from .repl import repl
from .runtime import execute
from .compiler import compile_, BUILTINS
from .analysis import analyse
from .syntax import parse
from .tokeniser import tokenise


def run_file(path):
    with open(path) as file:
        source = file.read()
        run_source(source)

def run_source(source):
    tokens = tokenise(source)
    syntax = parse(tokens)
    module = analyse(syntax, BUILTINS)
    program = compile_(module)
    execute(program)
