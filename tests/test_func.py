import pytest

import func


@pytest.mark.parametrize('source, expected_output', [
    (
        '''\
main = print 0\
''',
        '0\n'
    ),
    (
        '''\
main = print (add1 x)
x = add1 40
add1 = add 1\
''',
        '42\n',
    ),
])
def test_run(capsys, source, expected_output):
    func.run(source)
    captured = capsys.readouterr()
    assert captured.out == expected_output
