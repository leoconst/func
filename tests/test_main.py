import testing

from pathlib import Path

import func.__main__ as func_main


def test_run_repl(mocker):
    repl = mocker.patch('func.__main__.repl')
    with testing.raises(SystemExit, message=''):
        func_main.main()
    repl.assert_called_with()

def test_run_with_file(mocker):
    path = '/a/path'
    mocker.patch('sys.argv', ['', '--file', path])
    run_file = mocker.patch('func.__main__.run_file')
    with testing.raises(SystemExit, message=''):
        func_main.main()
    run_file.assert_called_with(Path(path))

def test_run_with_file_raises_exception(mocker):
    error_message = 'An error message'
    mocker.patch('sys.argv', ['', '--file', 'PATH'])
    mocker.patch('func.__main__.run_file',
        side_effect=Exception(error_message))
    with testing.raises(SystemExit, message=f'Error: {error_message}'):
        func_main.main()
