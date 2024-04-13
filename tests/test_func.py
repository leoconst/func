import pytest

import func


@pytest.mark.parametrize('file_name, expected_output', [
    ('the_answer.func', '42\n'),
    ('hello_world.func', 'Hello, world!\n'),
    ('conditional.func', 'Okay\n'),
])
def test_run_file(capsys, file_name, expected_output):
    path = f'examples/{file_name}'
    func.run_file(path)
    captured = capsys.readouterr()
    assert captured.out == expected_output

@pytest.mark.parametrize('source, expected_output', [
    (
'''\
main = print (integer_to_string 0)\
''',
        '0\n'
    ),
    (
'''\
main = print answer
answer = integer_to_string (add1 x)
x = add1 40
add1 = add 1\
''',
        '42\n',
    ),
    (
'''\
main = print text
text = 'You said:\\n\\t\\'Anyone there?\\''\
''',
        "You said:\n\t'Anyone there?'\n"
    ),
    (
'''\
main = print ''\
''',
        '\n'
    ),
    (
'''\
main = print (integer_to_string if 1 then 4 else 3)\
''',
        '4\n'
    ),
    (
'''\
main = print (integer_to_string if 0 then 4 else 3)\
''',
        '3\n'
    ),
    (
'''\
main = print if 1 then 'Yes' else 'No'\
''',
        'Yes\n'
    ),
    (
'''\
main = print if 0 then 'Yes' else 'No'\
''',
        'No\n'
    ),
])
def test_run(capsys, source, expected_output):
    func.run_source(source)
    captured = capsys.readouterr()
    assert captured.out == expected_output
