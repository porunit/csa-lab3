from enum import Enum


class DataStackControl(Enum):
    Push = 0
    Pop = 1


class AddressRegisterControl(Enum):
    PC = 0
    TOS = 1


class InstructionRegisterControl(Enum):
    MEM = 0


class InstractionPointerControl(Enum):
    IR = 0
    INC = 1


class TopOfStackControl(Enum):
    MEM = 0
    IR = 1
    BR = 2
    ALU = 3
    IR_VAR = 4
    IO = 5


class ALUValuesControl(Enum):
    VAR = 0


class AluOperation(Enum):
    SUM = 0
    SUB = 1
    MUL = 2
    DIV = 3
    MOD = 4
    NOT_EQ = 5
    EQ = 6
    MORE = 7
    LESS = 8


class MemoryControl(Enum):
    READ = 0
    WRITE = 1
    TOS = 2


class MicrocodeAddressControl(Enum):
    IR = 0
    INC = 1
    ZERO = 2


class BufferRegisterControl(Enum):
    DS = 0


class FlagCheck(Enum):
    z = 0
    n = 1
    v = 2


class JumpOperation(Enum):
    JMP = 0
    JZS = 1


class IOOperation(Enum):
    PRINT = 0
    READ = 1
    EMIT = 2


class ProgramControl(Enum):
    HALT = 0


class InstructionControl(Enum):
    INC = 0
