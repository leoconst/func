from func.repl import repl

from io import StringIO


def test_keyboard_interrupt_aborts(mocker):
    _set_input(mocker, [])
    repl()

def test_print_expression_prints(capsys, mocker):
    _set_input(mocker, ["print 'Hello!'"])
    repl()
    captured = capsys.readouterr()
    assert captured.out == 'Hello!\n'

def test_other_expression_prints_nothing(capsys, mocker):
    _set_input(mocker, ["'Hello there'"])
    repl()
    captured = capsys.readouterr()
    assert captured.out == ''

def test_binding_added_to_namespace(capsys, mocker):
    _set_input(mocker, ['num = 37', 'print (integer_to_string num)'])
    repl()
    captured = capsys.readouterr()
    assert captured.out == '37\n'


def _set_input(mocker, inputs):
    inputs_iter = iter(inputs)
    def fake_input(_prompt):
        try:
            return next(inputs_iter)
        except StopIteration:
            raise KeyboardInterrupt()
    mocker.patch('builtins.input', fake_input)
