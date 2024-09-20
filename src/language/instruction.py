import json
from collections import namedtuple
from enum import Enum


class Opcode(str, Enum):
    SUM = "sum"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"

    DUP = "dup"
    PUSH = "push"
    DROP = "drop"
    SWAP = "swap"

    NOT_EQ = "not_eq"
    EQ = "eq"
    MORE = "more"
    LESS = "less"

    PRINT = "print"
    EMIT = "emit"
    READ = "read"
    ADDR_ON_TOP = "addr_on_top"
    SAVE_VAR = "save_var"
    VAR_ON_TOP = "var_on_top"

    JZS = "jzs"
    JMP = "jmp"
    HALT = "halt"

    def __str__(self):
        return str(self.value)

class Instruction(namedtuple("Instruction", "line_number word_number symbol")):
    """Описание инструкции в виде (номер строки, номер слова в строке, символ)"""


def save_instructions_to_file(filename, instructions):
    with open(filename, "w", encoding="utf-8") as file:
        json_instructions = [json.dumps(instruction) for instruction in instructions]
        file.write("[" + ",\n".join(json_instructions) + "]")


def load_instructions_from_file(filename):
    with open(filename, encoding="utf-8") as file:
        instructions = json.loads(file.read())
    
    for instruction in instructions:
        if "opcode" in instruction:
            instruction["opcode"] = Opcode(instruction["opcode"])

        if "term" in instruction:
            instruction["term"] = Instruction(
                instruction["term"][0], instruction["term"][1], instruction["term"][2]
            )
    return instructions
