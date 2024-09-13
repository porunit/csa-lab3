import logging
from alu import ALU
from controls import JumpOperation, AluOperation, AddressRegisterControl, DataStackControl, IOOperation, MemoryControl, ProgramCounterControl, TopOfStackControl
from exceptions import StackOverflowError

STACK_SIZE = 64
VAR_MEMORY_SIZE = 150
INSTRUCTION_LIMIT = 100000

class Stack:
    stack = None
    max_size = None

    def __init__(self, max_size):
        self.stack = []
        self.max_size = max_size

    def push(self, arg):
        if len(self.stack) == self.max_size:
            raise StackOverflowError(self.max_size)
        if arg is not None:
            self.stack.append(arg)

    def pop(self):
        if len(self.stack) == 0:
            return None
        value = self.stack[-1]
        self.stack.pop()
        return value


class Memory:
    def __init__(self, code, var_memory_start):
        self.var_memory_start = var_memory_start
        self.memory = [0] * (len(code) + 1)
        self.current_value = 0
        self.memory[0] = var_memory_start
        for index, instruction in enumerate(code, 1):
            self.memory[index] = instruction

    def read(self, address):
        self.current_value = self.memory[address]

    def write(self, address):
        self.memory[address] = self.current_value

class DataPath:
    def __init__(self, code, input_buffer, var_memory_start):
        self.data_stack = Stack(STACK_SIZE)
        self.alu = ALU()
        self.instruction_register = {}
        self.buffer_register = 0
        self.memory = Memory(code, var_memory_start)
        self.address_register = None
        self.pc = 1
        self.top_of_stack = None
        self.input_buffer = input_buffer
        self.output_buffer = []

    def push_to_stack(self):
        self.data_stack.push(self.top_of_stack)

    def pop_from_stack(self):
        return self.data_stack.pop()

    def write_to_buffer_register(self):
        self.buffer_register = self.pop_from_stack()

    def load_memory_to_instruction_register(self):
        if isinstance(self.memory.current_value, int):
            self.instruction_register = {"arg": self.memory.current_value}
        else:
            self.instruction_register = self.memory.current_value

    def control_top_of_stack(self, signal):
        match signal:
            case TopOfStackControl.ALU:
                self.top_of_stack = self.alu.result
            case TopOfStackControl.BUFFER:
                self.top_of_stack = self.buffer_register
            case TopOfStackControl.MEMORY:
                self.top_of_stack = self.memory.memory[self.address_register]
            case TopOfStackControl.IMMEDIATE:
                self.top_of_stack = int(self.instruction_register["arg"])
            case TopOfStackControl.IMMEDIATE_WITH_OFFSET:
                self.top_of_stack = int(self.instruction_register["arg"]) + self.memory.var_memory_start

    def control_program_counter(self, signal):
        match signal:
            case ProgramCounterControl.IMMEDIATE:
                self.pc = self.instruction_register["arg"]
            case ProgramCounterControl.INCREMENT:
                self.pc += 1

    def load_alu_values(self):
        self.alu.first_operand = self.top_of_stack
        self.alu.second_operand = self.data_stack.pop()

    def execute_alu_operation(self, signal):
        self.alu.perform_operation(signal.value)

    def control_address_register(self, signal):
        match signal:
            case AddressRegisterControl.PC:
                self.address_register = self.pc
            case AddressRegisterControl.TOP_OF_STACK:
                self.address_register = self.top_of_stack

    def control_data_stack(self, signal):
        match signal:
            case DataStackControl.PUSH:
                self.push_to_stack()
            case DataStackControl.POP:
                self.pop_from_stack()

    def control_memory(self, signal):
        match signal:
            case MemoryControl.READ:
                self.memory.read(self.address_register)
            case MemoryControl.WRITE:
                self.memory.write(self.address_register)
            case MemoryControl.STORE_TOP_OF_STACK:
                self.memory.current_value = self.top_of_stack

    def control_io(self, signal):
        match signal:
            case IOOperation.PRINT:
                self.output_buffer.append(str(self.top_of_stack))
                logging.debug(f"Output: {''.join(self.output_buffer)} << {str(self.top_of_stack)}")
            case IOOperation.READ:
                if not self.input_buffer:
                    logging.warning("No input from user!")
                    self.top_of_stack = 0
                else:
                    self.top_of_stack = ord(self.input_buffer.pop(0))
                    logging.debug(f"Input: {chr(self.top_of_stack)}")
            case IOOperation.EMIT:
                self.output_buffer.append(chr(self.top_of_stack))
                logging.debug(f"Output: {''.join(self.output_buffer)} << {chr(self.top_of_stack)}")

    def handle_jump(self, signal):
        match signal:
            case JumpOperation.IF_ZERO:
                if self.alu.zero_flag == 1:
                    self.pc = self.top_of_stack
            case JumpOperation.UNCONDITIONAL:
                self.pc = self.top_of_stack


class Memory:
    def __init__(self, code, var_memory_start):
        self.var_memory_start = var_memory_start
        self.memory = [0] * (len(code) + 1)
        self.current_value = 0
        self.memory[0] = var_memory_start
        for index, instruction in enumerate(code, 1):
            self.memory[index] = instruction

    def read(self, address):
        self.current_value = self.memory[address]

    def write(self, address):
        self.memory[address] = self.current_value

class DataPath:
    def __init__(self, code, input_buffer, var_memory_start):
        self.data_stack = Stack(STACK_SIZE)
        self.alu = ALU()
        self.instruction_register = {}
        self.buffer_register = 0
        self.memory = Memory(code, var_memory_start)
        self.address_register = None
        self.pc = 1
        self.top_of_stack = None
        self.input_buffer = input_buffer
        self.output_buffer = []

    def push_to_stack(self):
        self.data_stack.push(self.top_of_stack)

    def pop_from_stack(self):
        return self.data_stack.pop()

    def write_to_buffer_register(self):
        self.buffer_register = self.pop_from_stack()

    def load_memory_to_instruction_register(self):
        if isinstance(self.memory.current_value, int):
            self.instruction_register = {"arg": self.memory.current_value}
        else:
            self.instruction_register = self.memory.current_value

    def control_top_of_stack(self, signal):
        match signal:
            case TopOfStackControl.ALU:
                self.top_of_stack = self.alu.result
            case TopOfStackControl.BUFFER:
                self.top_of_stack = self.buffer_register
            case TopOfStackControl.MEMORY:
                self.top_of_stack = self.memory.memory[self.address_register]
            case TopOfStackControl.IMMEDIATE:
                self.top_of_stack = int(self.instruction_register["arg"])
            case TopOfStackControl.IMMEDIATE_WITH_OFFSET:
                self.top_of_stack = int(self.instruction_register["arg"]) + self.memory.var_memory_start

    def control_program_counter(self, signal):
        match signal:
            case ProgramCounterControl.IMMEDIATE:
                self.pc = self.instruction_register["arg"]
            case ProgramCounterControl.INCREMENT:
                self.pc += 1

    def load_alu_values(self):
        self.alu.first_operand = self.top_of_stack
        self.alu.second_operand = self.data_stack.pop()

    def execute_alu_operation(self, signal):
        self.alu.perform_operation(signal.value)

    def control_address_register(self, signal):
        match signal:
            case AddressRegisterControl.PC:
                self.address_register = self.pc
            case AddressRegisterControl.TOP_OF_STACK:
                self.address_register = self.top_of_stack

    def control_data_stack(self, signal):
        match signal:
            case DataStackControl.PUSH:
                self.push_to_stack()
            case DataStackControl.POP:
                self.pop_from_stack()

    def control_memory(self, signal):
        match signal:
            case MemoryControl.READ:
                self.memory.read(self.address_register)
            case MemoryControl.WRITE:
                self.memory.write(self.address_register)
            case MemoryControl.STORE_TOP_OF_STACK:
                self.memory.current_value = self.top_of_stack

    def control_io(self, signal):
        match signal:
            case IOOperation.PRINT:
                self.output_buffer.append(str(self.top_of_stack))
                logging.debug(f"Output: {''.join(self.output_buffer)} << {str(self.top_of_stack)}")
            case IOOperation.READ:
                if not self.input_buffer:
                    logging.warning("No input from user!")
                    self.top_of_stack = 0
                else:
                    self.top_of_stack = ord(self.input_buffer.pop(0))
                    logging.debug(f"Input: {chr(self.top_of_stack)}")
            case IOOperation.EMIT:
                self.output_buffer.append(chr(self.top_of_stack))
                logging.debug(f"Output: {''.join(self.output_buffer)} << {chr(self.top_of_stack)}")

    def handle_jump(self, signal):
        match signal:
            case JumpOperation.IF_ZERO:
                if self.alu.zero_flag == 1:
                    self.pc = self.top_of_stack
            case JumpOperation.UNCONDITIONAL:
                self.pc = self.top_of_stack
