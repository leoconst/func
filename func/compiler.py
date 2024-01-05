from .analysis import *


def compile_(module):
    try:
        main = module.bindings['main']
    except KeyError:
        raise CompilationError('No main binding defined')

class CompilationError(Exception):
    pass
