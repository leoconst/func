import pytest

from func.repl import repl

from io import StringIO


@pytest.mark.parametrize('inputs, expected_output', [
    ([], ''),
    (["print 'Hello!'"], 'Hello!\n'),
    (["'Hello there'"], ''),
    (['num = 37', 'print (integer_to_string num)'], '37\n'),
])
def test_success(capsys, mock_inputs, inputs, expected_output):
    mock_inputs(inputs)
    repl()
    captured = capsys.readouterr()
    assert captured.out == expected_output
    assert captured.err == ''

@pytest.mark.parametrize('inputs, expected_error', [
    (['hello'], "Unbound name: 'hello'\n"),
    (['!'], "Unexpected character: '!'\n"),
])
def test_failure(capsys, mock_inputs, inputs, expected_error):
    mock_inputs(inputs)
    repl()
    captured = capsys.readouterr()
    assert captured.out == f'Error: {expected_error}'
    assert captured.err == ''


@pytest.fixture
def mock_inputs(mocker):
    def _patch_input(inputs):
        inputs_iter = iter(inputs)
        def fake_input(_prompt):
            try:
                return next(inputs_iter)
            except StopIteration:
                raise KeyboardInterrupt()
        mocker.patch('builtins.input', fake_input)
    return _patch_input
