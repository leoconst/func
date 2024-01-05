import pytest

from func.compiler import *
from func.analysis import *


def test_no_main_binding():
    module = Module({})
    with pytest.raises(CompilationError, match='No main binding defined'):
        compile_(module)
