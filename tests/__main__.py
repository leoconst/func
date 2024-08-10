import pytest
import subprocess
import sys


print('Running tests...')
test_result = pytest.main()
if test_result != 0:
	sys.exit(test_result)

print('Running type check...')
type_check_result = subprocess.run(['mypy', '.',
	'--strict',
	'--enable-incomplete-feature', 'NewGenericSyntax']).returncode
if type_check_result != 0:
	sys.exit(type_check_result)
