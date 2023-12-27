import tests

tests.enable_module_imports()
from func.tokenising import tokenise


def test_empty():
    assert list(tokenise('')) == []


def main():
    tests.run()

if __name__ == '__main__':
    main()
