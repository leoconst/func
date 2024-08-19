import re

import pytest


def raises(exception, *, message):
    match = fr'^{re.escape(message)}$'
    return pytest.raises(exception, match=match)
