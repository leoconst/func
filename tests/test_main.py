import testing
from unittest.mock import patch

from pathlib import Path

import func.__main__ as func_main


def test_run_repl():
    result = object()
    with patch('func.__main__.repl') as repl:
        with testing.raises(SystemExit):
            func_main.main()
    repl.assert_called_with()

def test_run_with_file(monkeypatch):
    path = '/a/path'
    monkeypatch.setattr('sys.argv', ['', '--file', path])
    with patch('func.__main__.run_file') as run_file:
        with testing.raises(SystemExit):
            func_main.main()
    run_file.assert_called_with(Path(path))

def test_run_with_file_raises_exception(monkeypatch):
    error_message = 'An error message'
    monkeypatch.setattr('sys.argv', ['', '--file', 'PATH'])
    with patch('func.__main__.run_file', side_effect=Exception(error_message)):
        with testing.raises(SystemExit, message=f'Error: {error_message}'):
            func_main.main()

def raise_(exception):
    raise exception
