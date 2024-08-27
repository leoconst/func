import argparse
import sys
from pathlib import Path

from . import repl, run_file, __name__ as program_name


def main():
    options = parse_command_line_arguments()
    result = run(options)
    sys.exit(result)

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument('--file', type=Path)
    return parser.parse_args()

def run(options):
    if options.file is None:
        repl()
    else:
        return run_file_safe(options)

def run_file_safe(options):
    try:
        run_file(options.file)
    except Exception as exception:
        return f'Error: {exception}'


if __name__ == '__main__':
    main()
