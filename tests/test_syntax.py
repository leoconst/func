import pytest

from func.syntax import *
from func.tokens import tokenise


@pytest.mark.parametrize('source, expected', [
    (
        '',
        Module([])
    ),
    (
        'hello = world',
        Module([
            Binding(
                'hello',
                Identifier('world')
            )
        ])
    ),
    (
        "indentifier_calls = a b c\nstring_calls = 'a' 'b' 'c'",
        Module([
            Binding(
                'indentifier_calls',
                Call(
                    Call(
                        Identifier('a'),
                        Identifier('b')
                    ),
                    Identifier('c')
                )
            ),
            Binding(
                'string_calls',
                Call(
                    Call(
                        String(['a']),
                        String(['b'])
                    ),
                    String(['c'])
                )
            ),
        ])
    ),
    (
        "name = 'World'\ngreet = print 'Hello, \\(name)!'",
        Module([
            Binding(
                'name',
                String(['World'])
            ),
            Binding(
                'greet',
                Call(
                    Identifier('print'),
                    String([
                        'Hello, ',
                        Identifier('name'),
                        '!',
                    ])
                )
            ),
        ])
    ),
    (
        'var = (3)',
        Module([
            Binding(
                'var',
                Integer('3')
            ),
        ])
    ),
    (
        'var = (a b)',
        Module([
            Binding(
                'var',
                Call(
                    Identifier('a'),
                    Identifier('b')
                )
            ),
        ])
    ),
    (
        'var = (a b) (c d)',
        Module([
            Binding(
                'var',
                Call(
                    Call(
                        Identifier('a'),
                        Identifier('b')
                    ),
                    Call(
                        Identifier('c'),
                        Identifier('d')
                    )
                )
            ),
        ])
    ),
    (
        'var = a (b c d)',
        Module([
            Binding(
                'var',
                Call(
                    Identifier('a'),
                    Call(
                        Call(
                            Identifier('b'),
                            Identifier('c')
                        ),
                        Identifier('d')
                    )
                )
            ),
        ])
    ),
    (
        'var = λa -> b',
        Module([
            Binding(
                'var',
                Lambda(
                    'a',
                    Identifier('b')
                )
            ),
        ])
    ),
    (
        'conditional = if condition then truth else lies',
        Module([
            Binding(
                'conditional',
                IfElse(
                    Identifier('condition'),
                    Identifier('truth'),
                    Identifier('lies')
                )
            ),
        ])
    ),
    (
        "conditional = if yes then 'yes' else repeat 'no' 3",
        Module([
            Binding(
                'conditional',
                IfElse(
                    Identifier('yes'),
                    String(['yes']),
                    Call(
                        Call(
                            Identifier('repeat'),
                            String(['no'])
                        ),
                        Integer('3')
                    )
                )
            ),
        ])
    ),
])
def test_success(source, expected):
    tokens = tokenise(source)
    actual = parse(tokens)
    assert actual == expected

@pytest.mark.parametrize('source, expectation, reality', [
    ('var', 'an equals symbol', 'end-of-source'),
    ('var =', 'an expression', 'end-of-source'),
    ('var = =', 'an expression', 'an equals symbol'),
    ('call me', 'an equals symbol', 'an identifier'),
    ("val = call this 'thing' now =", 'a newline', 'an equals symbol'),
    ('name = value\n', 'an identifier', 'end-of-source'),
    ("number = 3\n'not a binding'", 'an identifier', 'a string'),
    ("number = 3\nstring = ''\n", 'an identifier', 'end-of-source'),
    ('=', 'an identifier', 'an equals symbol'),
    ("''", 'an identifier', 'a string'),
    ("'string'", 'an identifier', 'a string'),
    ('100', 'an identifier', 'an integer'),
    ('var = 1 =', 'a newline', 'an equals symbol'),
    ('(', 'an identifier', 'an opening bracket'),
    ('value = (', 'an expression', 'end-of-source'),
    ('value = )', 'an expression', 'a closing bracket'),
    ('value = (hello', 'a closing bracket', 'end-of-source'),
    ('value = (3 (', 'an expression', 'end-of-source'),
    ('value = ()', 'an expression', 'a closing bracket'),
    ('value = (a b c (d e', 'a closing bracket', 'end-of-source'),
    ('value = λ', 'an identifier', 'end-of-source'),
    ('value = λa', 'an arrow', 'end-of-source'),
    ('value = λa ->', 'an expression', 'end-of-source'),
    ('λ', 'an identifier', 'the beginning of a lambda'),
    (
        "var = 'hello\\()world'",
        'an expression',
        'the end of an expression escape'
    ),
])
def test_failure(source, expectation, reality):
    tokens = tokenise(source)
    expected_error_message = f'Expected {expectation}, got {reality}'
    with pytest.raises(ParseError, match=expected_error_message):
        parse(tokens)
