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
        self._call_stack = []

    def run(self):
        while (opcode := self._next()) is not None:
            self._advance(opcode)

    def _advance(self, opcode):
        match opcode:
            case Opcode.END:
                self._program_pointer = len(self._program)
            case Opcode.PUSH:
                value = self._next()
                self._push(value)
            case Opcode.COPY:
                value = self._pop()
                self._push(value)
                self._push(value)
            case Opcode.MOVE:
                value = self._pop()
                index = self._next()
                end_index = len(self._stack) - index
                self._stack.insert(end_index, value)
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
            case Opcode.MULTIPLY:
                first = self._pop()
                second = self._pop()
                result = first*second
                self._push(result)
            case Opcode.DECREMENT:
                value = self._pop()
                value -= 1
                self._push(value)
            case Opcode.LESS_THAN_OR_EQUAL:
                first = self._pop()
                second = self._pop()
                result = first <= second
                self._push(result)
            case Opcode.JUMP_IF:
                condition = self._pop()
                address = self._next()
                if condition:
                    self._program_pointer = address
            case Opcode.CALL:
                new_location = self._next()
                return_location = self._program_pointer
                self._call_stack.append(return_location)
                self._program_pointer = new_location
            case Opcode.RETURN:
                previous_location = self._call_stack.pop()
                self._program_pointer = previous_location
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
