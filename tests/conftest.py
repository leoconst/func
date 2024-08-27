import pytest
import unittest.mock


@pytest.fixture
def mocker():
    mocker = _Mocker()
    yield mocker
    mocker.close()

class _Mocker:

    def __init__(self):
        self._patches = []

    def patch(self, *positionals, **keywords):
        patch = unittest.mock.patch(*positionals, **keywords)
        self._patches.append(patch)
        mock = patch.start()
        return mock

    def close(self):
        for patch in self._patches:
            patch.stop()
