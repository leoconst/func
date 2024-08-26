# Func
Func is a toy functional programming language.

I'm using this project as an outlet to play around with language
design/implementation.

## Features
- Basic types: `Integer`, `String`
- Functions with partial application
- A command-line [REPL][1] (Read-Eval-Print Loop)

## Example
The code:
```func
main = print answer
answer = integer_to_string (add1 x)
x = add (add 10 25) (add1 5)
add1 = add 1
```
prints the line `42` to the standard output.

## How do I?

### Install:
1. Install [Python][2] if you haven't already
2. Clone the [repository][3]

### Run:
1. Open a terminal
2. Navigate to the repository folder
3. Either:
	- Run the REPL: `python -m func`
	- Run a Func file: `python -m func --file <PATH>`
	- Run the tests:
		1. Navigate to the `tests` folder
		2. Run `python .`

[1]: https://en.wikipedia.org/wiki/Read–eval–print_loop
[2]: https://www.python.org
[3]: https://github.com/leoconst/func
