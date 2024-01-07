from array import array

from .compiler import Opcode


def execute(program):
    machine = _VirtualMachine(program)
    machine.run()

class _VirtualMachine:

    def __init__(self, program):
        self._program = program
        self._program_pointer = 0
        self._stack = []
        self._heap = array('B')

    def run(self):
        while (opcode := self._next()) is not None:
            self._advance(opcode)

    def _advance(self, opcode):
        match opcode:
            case Opcode.PUSH:
                value = self._next()
                self._push(value)
            case Opcode.ADD:
                first = self._pop()
                second = self._pop()
                result = first + second
                self._push(result)
            case Opcode.PRINT:
                value = self._pop()
                print(value)
            case Opcode.INTEGER_TO_STRING:
                number = self._pop()
                address = len(self._heap)
                string = str(number)
                raw = string.encode('utf8')
                length = len(raw)
                self._heap.append(length)
                self._heap.extend(raw)
                self._push(address)
            case _:
                raise ValueError(f'Unknown opcode: {opcode}')

    def _next(self):
        try:
            value = self._program[self._program_pointer]
        except IndexError:
            return None
        self._program_pointer += 1
        return value

    def _push(self, value):
        self._stack.append(value)

    def _pop(self):
        return self._stack.pop()
