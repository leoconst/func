import tests

tests.enable_module_imports()
from func.tokenising import *


def test_empty():
    assert list(tokenise('')) == []

def test_example():
    source = '''\
 \t repeat 3 '\\'Two plus three\\' equals:\\n\\t\\(add\t2 '3').'  \r\n\n= \t\
'''
    actual = list(tokenise(source))
    expected = [
        PlainToken(TokenKind.IDENTIFIER, 'repeat'),
        PlainToken(TokenKind.INTEGER, '3'),
        StringToken([
            '\'Two plus three\' equals:\n\t',
            [
                PlainToken(TokenKind.IDENTIFIER, 'add'),
                PlainToken(TokenKind.INTEGER, '2'),
                StringToken([
                    '3',
                ]),
            ],
            '.'
        ]),
        PlainToken(TokenKind.NEWLINE, '\r\n'),
        PlainToken(TokenKind.NEWLINE, '\n'),
        PlainToken(TokenKind.EQUALS, '='),
    ]
    assert actual == expected


def main():
    tests.run()

if __name__ == '__main__':
    main()
