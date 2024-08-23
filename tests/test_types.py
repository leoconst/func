import pytest

from func.types import *


@pytest.mark.parametrize('type, expected', [
    (INTEGER, 'Integer'),
    (STRING, 'String'),
    (UNIT, 'Unit'),
    (Named('bleh'), 'bleh'),
    (Callable(Named('a'), Named('b')), 'a -> b'),
    (Callable(INTEGER, Callable(STRING, UNIT)), 'Integer -> String -> Unit'),
])
def test_str(type, expected):
    actual = str(type)
    assert actual == expected
