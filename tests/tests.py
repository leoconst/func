import pytest
import os
import sys


def enable_module_imports():
    sys.path.insert(
        0,
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run():
    sys.exit(pytest.main())


def _main():
    run()

if __name__ == '__main__':
    _main()
