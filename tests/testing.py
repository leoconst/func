import re

import pytest


def raises(exception, *, message=None):
    keywords = {}
    if message is not None:
        match = fr'^{re.escape(message)}$'
        keywords['match'] = match
    return pytest.raises(exception, **keywords)
