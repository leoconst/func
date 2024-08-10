import argparse
import sys
from pathlib import Path

from . import run_file, __name__ as program_name


def parse_command_line_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('path', type=Path)
    return parser.parse_args()

def run(path: Path) -> str|None:
    try:
        run_file(path)
        return None
    except Exception as exception:
        return f'Error: {exception}'

options = parse_command_line_arguments()
result = run(options.path)
sys.exit(result)
