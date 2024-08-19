from array import array

from .opcodes import Opcode


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
            case Opcode.SET:
                address = len(self._heap)
                length = self._next()
                self._heap.append(length)
                for _ in range(length):
                    value = self._next()
                    self._heap.append(value)
                self._push(address)
            case Opcode.ADD:
                first = self._pop()
                second = self._pop()
                result = first + second
                self._push(result)
            case Opcode.JUMP:
                jump = self._next()
                self._program_pointer += jump
            case Opcode.JUMP_IF:
                condition = self._pop()
                jump = self._next()
                if condition != 0:
                    self._program_pointer += jump
            case Opcode.PRINT:
                address = self._pop()
                length = self._heap[address]
                start = address + 1
                end = start + length
                raw = bytes(self._heap[start:end])
                string = raw.decode('utf8')
                print(string)
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
