import pytest

from func.repl import repl

from io import StringIO


def test_keyboard_interrupt_aborts(mock_inputs):
    mock_inputs()
    repl()

def test_print_expression_prints(capsys, mock_inputs):
    mock_inputs("print 'Hello!'")
    repl()
    captured = capsys.readouterr()
    assert captured.out == 'Hello!\n'

def test_other_expression_prints_nothing(capsys, mock_inputs):
    mock_inputs("'Hello there'")
    repl()
    captured = capsys.readouterr()
    assert captured.out == ''

def test_binding_added_to_namespace(capsys, mock_inputs):
    mock_inputs('num = 37', 'print (integer_to_string num)')
    repl()
    captured = capsys.readouterr()
    assert captured.out == '37\n'


@pytest.fixture
def mock_inputs(mocker):
    def _patch_input(*inputs):
        inputs_iter = iter(inputs)
        def fake_input(_prompt):
            try:
                return next(inputs_iter)
            except StopIteration:
                raise KeyboardInterrupt()
        mocker.patch('builtins.input', fake_input)
    return _patch_input
