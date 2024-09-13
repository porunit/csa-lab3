import logging
from typing import ClassVar
import sys
sys.path.append('../language')
sys.path.append('..')


from computer.memory import INSTRACTION_LIMIT
from exceptions import InvalidSignalError
from instruction import Opcode
from computer.controls import (
    JumpOperation,
    ProgramControl,
    AluOperation,
    ALUValuesControl,
    AddressRegisterControl,
    BufferRegisterControl,
    DataStackControl,
    InstructionControl,
    IOOperation,
    InstructionRegisterControl,
    MicrocodeAddressControl,
    MemoryControl,
    ProgramCounterControl,
    TopOfStackControl,
)


def opcode2microcode(opcode):
    return {
        Opcode.SUM: 2,
        Opcode.SUB: 4,
        Opcode.MUL: 6,
        Opcode.DIV: 8,
        Opcode.MOD: 10,
        Opcode.DUP: 12,
        Opcode.DROP: 14,
        Opcode.SWAP: 16,
        Opcode.EQ: 19,
        Opcode.MORE: 21,
        Opcode.LESS: 23,
        Opcode.PUSH: 25,
        Opcode.ADDR_ON_TOP: 27,
        Opcode.SAVE_VAR: 29,
        Opcode.VAR_ON_TOP: 32,
        Opcode.JZS: 35,
        Opcode.JMP: 38,
        Opcode.PRINT: 41,
        Opcode.READ: 44,
        Opcode.EMIT: 46,
        Opcode.HALT: 49,
        Opcode.NOT_EQ: 50,
    }.get(opcode)


microcode = [
    # Fetch next instraction - 0
    [AddressRegisterControl.PC, MemoryControl.READ, MicrocodeAddressControl.INC],
    [InstructionRegisterControl.MEM, InstructionControl.INC, MicrocodeAddressControl.IR],
    # SUM - 2
    [ALUValuesControl.VAR, AluOperation.SUM, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # SUB - 4
    [ALUValuesControl.VAR, AluOperation.SUB, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # MUL - 6
    [ALUValuesControl.VAR, AluOperation.MUL, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # DIV - 8
    [ALUValuesControl.VAR, AluOperation.DIV, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # MOD - 10
    [ALUValuesControl.VAR, AluOperation.MOD, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # DUP - 12
    [DataStackControl.Push, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # DROP - 14
    [DataStackControl.Pop, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # SWAP - 16
    [BufferRegisterControl.DS, MicrocodeAddressControl.INC],
    [DataStackControl.Push, TopOfStackControl.BR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # EQ - 19
    [ALUValuesControl.VAR, AluOperation.EQ, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # MORE - 21
    [ALUValuesControl.VAR, AluOperation.MORE, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # LESS - 23
    [ALUValuesControl.VAR, AluOperation.LESS, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # PUSH - 25
    [DataStackControl.Push, TopOfStackControl.IR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # ADR_ON_TOP - 27
    [DataStackControl.Push, TopOfStackControl.IR_VAR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # SAVE_VAR - 29
    [AddressRegisterControl.TOS, BufferRegisterControl.DS, TopOfStackControl.BR, MemoryControl.TOS, MicrocodeAddressControl.INC],
    [MemoryControl.WRITE, BufferRegisterControl.DS, TopOfStackControl.BR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # VAR_ON_TOP - 32
    [AddressRegisterControl.TOS, MemoryControl.READ, MicrocodeAddressControl.INC],
    [InstructionRegisterControl.MEM, TopOfStackControl.IR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # JZS - 35
    [DataStackControl.Push, TopOfStackControl.IR, JumpOperation.JZS, MicrocodeAddressControl.INC],
    [DataStackControl.Pop, BufferRegisterControl.DS, TopOfStackControl.BR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # JMP - 38
    [DataStackControl.Push, TopOfStackControl.IR, JumpOperation.JMP, MicrocodeAddressControl.INC],
    [BufferRegisterControl.DS, TopOfStackControl.BR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # PRINT - 41
    [IOOperation.PRINT, MicrocodeAddressControl.INC],
    [BufferRegisterControl.DS, TopOfStackControl.BR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # READ - 44
    [DataStackControl.Push, MicrocodeAddressControl.INC],
    [IOOperation.READ, InstructionControl.INC, ProgramCounterControl.INC, MicrocodeAddressControl.ZERO],
    # EMIT - 46
    [IOOperation.EMIT, MicrocodeAddressControl.INC],
    [BufferRegisterControl.DS, TopOfStackControl.BR, MicrocodeAddressControl.INC],
    [ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
    # HALT - 49
    [InstructionControl.INC, ProgramControl.HALT],
    # NOT_EQ - 50
    [ALUValuesControl.VAR, AluOperation.NOT_EQ, MicrocodeAddressControl.INC],
    [TopOfStackControl.ALU, ProgramCounterControl.INC, InstructionControl.INC, MicrocodeAddressControl.ZERO],
]


class ControlUnit:
    mc_adr = None
    datapath = None
    tick = None
    instraction_count = None
    signal_handlers: ClassVar[dict] = {}

    def __init__(self, datapath):
        self.mc_adr = 0
        self.datapath = datapath
        self.tick = 0
        self.instraction_count = 0
        self.signal_handlers = {
            AddressRegisterControl: [getattr(self.datapath, "address_register_latch"), 2],
            MemoryControl: [getattr(self.datapath, "memory_latch"), 2],
            MicrocodeAddressControl: [getattr(self, "mc_adr_latch"), 2],
            InstructionRegisterControl: [getattr(self.datapath, "mem_value_to_ir"), 1],
            ALUValuesControl: [getattr(self.datapath, "alu_values_get"), 1],
            AluOperation: [getattr(self.datapath, "alu_latch"), 2],
            TopOfStackControl: [getattr(self.datapath, "tos_latch"), 2],
            ProgramCounterControl: [getattr(self.datapath, "pc_latch"), 2],
            DataStackControl: [getattr(self.datapath, "data_stack_latch"), 2],
            BufferRegisterControl: [getattr(self.datapath, "write_buffer_register"), 1],
            IOOperation: [getattr(self.datapath, "io_latch"), 2],
            JumpOperation: [getattr(self.datapath, "jump"), 2],
            InstructionControl: [getattr(self, "inc_instraction_count"), 1],
        }

    def __repr__(self, signal):
        return (
            "TICK: {:4} PC: {:3} ADDR: {:3} mcADDR: {:2} SIGNAL: {:15} TOS: {:6} Z: {:1} N: {:1} V: {:1}\n" "DS: {}"
        ).format(
            str(self.tick),
            str(self.datapath.pc),
            str(self.datapath.address_register),
            str(self.mc_adr),
            str(signal),
            str(self.datapath.top_of_stack) if self.datapath.top_of_stack is not None else "0",
            str(self.datapath.alu.z_flag),
            str(self.datapath.alu.n_flag),
            str(self.datapath.alu.v_flag),
            self.datapath.data_stack.stack,
        )

    def inc_tick(self):
        self.tick += 1

    def inc_instraction_count(self):
        self.instraction_count += 1

    def execute_instraction(self, signals):
        for signal in signals:
            handler_name = self.signal_handlers.get(type(signal))
            if handler_name:
                if handler_name[1] == 2:
                    handler_name[0](signal)
                else:
                    handler_name[0]()
            else:
                if isinstance(signal, ProgramControl):
                    raise StopIteration
                raise InvalidSignalError(signal)
            logging.debug("%s", self.__repr__(signal))
            self.inc_tick()

    def mc_adr_latch(self, signal):
        match signal:
            case MicrocodeAddressControl.IR:
                self.mc_adr = opcode2microcode(self.datapath.instraction_register["opcode"])
            case MicrocodeAddressControl.INC:
                self.mc_adr += 1
            case MicrocodeAddressControl.ZERO:
                self.mc_adr = 0

    def run_machine(self):
        try:
            while self.instraction_count < INSTRACTION_LIMIT:
                self.execute_instraction(microcode[self.mc_adr])
        except StopIteration:
            pass
        except OSError:
            pass
        output = ""
        for stroka in "".join(self.datapath.output_buffer).split("\n"):
            tabs = 4 * '\t'
            output += f"{tabs}{stroka}\n"
        logging.debug("output_buffer: \n" + output[0:-1])
        return self.datapath.output_buffer, self.instraction_count, self.tick
