import pytest

from func.tokenising import tokenise
from func.parsing import parse
from func.analysis import *


def test_success():
    syntax = _get_syntax('name0 = 0\nname1 = 1')
    expected = Module({
        'name0': Integer(0),
        'name1': Integer(1),
    })
    actual = analyse(syntax)
    assert actual == expected

def test_duplicate_binding_name():
    syntax = _get_syntax('name = 0\nname = 1')
    with pytest.raises(AnalysisError, match="Duplicate binding name: 'name'"):
        analyse(syntax)

def _get_syntax(source):
    tokens = tokenise(source)
    return parse(tokens)
