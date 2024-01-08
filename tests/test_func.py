import pytest

import func


def test_run_file(capsys):
    path = 'examples/the_answer.func'
    expected_output = '42\n'
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
main = print 'Hello!'\
''',
        'Hello!\n',
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
])
def test_run(capsys, source, expected_output):
    func.run_source(source)
    captured = capsys.readouterr()
    assert captured.out == expected_output
