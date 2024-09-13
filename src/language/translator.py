import sys

sys.path.append('..')
from exceptions import (
    BranchesNotBalancedError,
    ClosingBranchError,
    ClosingLoopError,
    EndingProcedureError,
    InputError,
    LoopError,
    ProcedureError,
    BufferError,
    ProcedureInBranchError,
    ProcedureInLoopError,
    TranslatorArgumentsError,
)
from instruction import Opcode, Instruction, save_instructions_to_file

token_set = {
    "+", "-", "*", "/", "mod", "dup", "drop", "swap", "begin", "until", "=", "!=", ">", "<", ".", "exit", "!", "@", "#", "if", "else", "endif", "emit"
}

control_flow_commands = {"if", "else", "endif", "begin", "until"}

variable_table = {}
buffer_declaration_list = []

def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def get_opcode_for_symbol(symbol):
    return {
        "+": Opcode.SUM.value,
        "-": Opcode.SUB.value,
        "*": Opcode.MUL.value,
        "/": Opcode.DIV.value,
        "mod": Opcode.MOD.value,
        "dup": Opcode.DUP.value,
        "drop": Opcode.DROP.value,
        "swap": Opcode.SWAP.value,
        "=": Opcode.EQ.value,
        ">": Opcode.MORE.value,
        "<": Opcode.LESS.value,
        ".": Opcode.PRINT.value,
        "exit": Opcode.HALT.value,
        "!": Opcode.SAVE_VAR.value,
        "@": Opcode.VAR_ON_TOP.value,
        "#": Opcode.READ.value,
        "emit": Opcode.EMIT.value,
        "!=": Opcode.NOT_EQ.value,
    }.get(symbol)

def parse_code_to_terms(text):
    variable_counter = 1
    terms = []
    procedures = {}
    in_procedure = False
    waiting_for_procedure_name = False
    branch_depth = 0
    loop_depth = 0
    procedure_name = ""
    
    for line_number, line in enumerate(text.split("\n"), 1):
        if line.strip():
            tokens = line.strip().split(" ")
            for word_number, token in enumerate(tokens, 1):
                if waiting_for_procedure_name:
                    procedure_name = str(token)
                    procedures[procedure_name] = []
                    waiting_for_procedure_name = False
                elif is_integer(token) or token in token_set:
                    if in_procedure:
                        procedures[procedure_name].append(Instruction(line_number, word_number, token))
                    else:
                        terms.append(Instruction(line_number, word_number, token))
                elif token == "buffer":
                    if tokens[1] not in variable_table:
                        variable_table[tokens[1]] = variable_counter
                        buffer_declaration_list.extend([token] * int(tokens[2]))
                        variable_counter += int(tokens[2])
                        break
                    if in_procedure:
                        raise BufferError()
                elif token == ":":
                    if branch_depth == 0 and loop_depth == 0:
                        if not in_procedure:
                            in_procedure = True
                            waiting_for_procedure_name = True
                        else:
                            raise ProcedureError(line_number, word_number, token)
                    else:
                        if branch_depth == 0:
                            raise ProcedureInBranchError(line_number, word_number, token)
                        if loop_depth == 0:
                            raise ProcedureInLoopError(line_number, word_number, token)
                elif token == ";":
                    if branch_depth == 0 and loop_depth == 0:
                        if in_procedure:
                            in_procedure = False
                        else:
                            raise EndingProcedureError(line_number, word_number, token)
                    else:
                        if branch_depth == 0:
                            raise ClosingBranchError(line_number, word_number, token)
                        if loop_depth == 0:
                            raise ClosingLoopError(line_number, word_number, token)
                elif token in procedures:
                    for term in procedures[token]:
                        terms.append(term)
                elif token.startswith('."'):
                    break
                else:
                    if tokens[-1] in {"!", "@"}:
                        if len(tokens) in {2, 3}:
                            if token not in variable_table:
                                variable_table[token] = variable_counter
                                buffer_declaration_list.append(token)
                                variable_counter += 1
                            if in_procedure:
                                procedures[procedure_name].append(Instruction(line_number, word_number, token))
                            else:
                                terms.append(Instruction(line_number, word_number, token))
                        if len(tokens) == 5:
                            if in_procedure:
                                procedures[procedure_name].append(Instruction(line_number, word_number, line.strip()))
                                break
                            terms.append(Instruction(line_number, word_number, line.strip()))
                            break
                    else:
                        raise InputError(line_number, word_number, token)

                if token == "if":
                    branch_depth -= 1
                if token == "endif":
                    branch_depth += 1
                if token == "begin":
                    loop_depth -= 1
                if token == "until":
                    loop_depth += 1

            if line.startswith('."'):
                variable_table[line[3:-1]] = variable_counter
                variable_counter += len(line[3:-1])
                terms.append(Instruction(line_number, 1, line))

    if branch_depth < 0:
        raise BranchesNotBalancedError
    if loop_depth < 0:
        raise LoopError
    return terms

def generate_string_translation(string, index):
    operations = [
        {"index": index, "opcode": Opcode.ADDR_ON_TOP.value, "arg": variable_table[string]},
        {"index": index + 1, "opcode": Opcode.PUSH.value, "arg": 1},
        {"index": index + 2, "opcode": Opcode.SUM.value},
        {"index": index + 3, "opcode": Opcode.DUP.value},
        {"index": index + 4, "opcode": Opcode.VAR_ON_TOP.value},
        {"index": index + 5, "opcode": Opcode.EMIT.value},
        {"index": index + 6, "opcode": Opcode.DUP.value},
        {"index": index + 7, "opcode": Opcode.ADDR_ON_TOP.value, "arg": variable_table[string]},
        {"index": index + 8, "opcode": Opcode.SWAP.value},
        {"index": index + 9, "opcode": Opcode.SUB.value},
        {"index": index + 10, "opcode": Opcode.ADDR_ON_TOP.value, "arg": variable_table[string]},
        {"index": index + 11, "opcode": Opcode.VAR_ON_TOP.value},
        {"index": index + 12, "opcode": Opcode.SUB.value},
        {"index": index + 13, "opcode": Opcode.PUSH.value, "arg": 0},
        {"index": index + 14, "opcode": Opcode.EQ.value},
        {"index": index + 15, "opcode": Opcode.JZS.value, "arg": index}
    ]
    return operations, index + len(operations)

def translate_string_to_memory(string):
    memory_init = [{"adr": variable_table[string], "arg": len(string)}]
    memory_init.extend([{"adr": variable_table[string] + i, "arg": ord(c)} for i, c in enumerate(string, 1)])
    return memory_init

def translate_text(text):
    string_literals = []
    terms = parse_code_to_terms(text)
    machine_code = []
    jump_stack = []
    is_else_block = False
    index = 0

    for term in terms:
        tokens = term.symbol.split(" ")
        if tokens[0] == "if":
            machine_code.append(None)
            jump_stack.append(index)
        elif tokens[0] == "else":
            if_index = jump_stack.pop()
            machine_code[if_index] = {
                "index": if_index,
                "opcode": Opcode.JZS.value,
                "arg": index + 1,
                "term": terms[if_index],
            }
            machine_code.append(None)
            jump_stack.append(index)
            is_else_block = True
        elif tokens[0] == "endif":
            if_index = jump_stack.pop()
            index -= 1
            if is_else_block:
                machine_code[if_index] = {"index": if_index, "opcode": Opcode.JMP.value, "arg": index + 1}
            else:
                machine_code[if_index] = {"index": if_index, "opcode": Opcode.JZS.value, "arg": index + 1}
        elif tokens[0] == "begin":
            jump_stack.append(index)
            index -= 1
        elif tokens[0] == "until":
            begin_index = jump_stack.pop()
            machine_code.append({"index": index, "opcode": Opcode.JZS.value, "arg": begin_index})
        elif is_integer(tokens[0]):
            machine_code.append({"index": index, "opcode": Opcode.PUSH.value, "arg": tokens[0], "term": term})
        elif tokens[0] in variable_table:
            if len(tokens) == 5:
                machine_code.extend([
                    {"index": index, "opcode": Opcode.ADDR_ON_TOP.value, "arg": variable_table[tokens[1]], "term": Instruction(term.line, 2, tokens[1])},
                    {"index": index + 1, "opcode": Opcode.VAR_ON_TOP.value, "term": Instruction(term.line, 3, tokens[2])},
                    {"index": index + 2, "opcode": Opcode.ADDR_ON_TOP.value, "arg": variable_table[tokens[0]], "term": Instruction(term.line, 1, tokens[0])},
                    {"index": index + 3, "opcode": Opcode.SUM.value, "term": Instruction(term.line, 4, tokens[3])},
                    {"index": index + 4, "opcode": Opcode.SAVE_VAR if tokens[4] == "!" else Opcode.VAR_ON_TOP.value, "term": Instruction(term.line, 5, tokens[4])},
                ])
                index += 4
            else:
                machine_code.append(
                    {"index": index, "opcode": Opcode.ADDR_ON_TOP.value, "arg": variable_table[tokens[0]], "term": term}
                )
        elif tokens[0] == '."':
            string_literals.append(" ".join(tokens)[3:-1])
            operations, index = generate_string_translation(" ".join(tokens)[3:-1], index)
            machine_code.extend(operations)
        else:
            machine_code.append({"index": index, "opcode": get_opcode_for_symbol(tokens[0]), "term": term})

        index += 1

    for buffer_var in buffer_declaration_list:
        machine_code.append({"index": index, "arg": 0})
        index += 1

    for string_literal in string_literals:
        machine_code.append({"index": index, "arg": len(string_literal)})
        for symbol_index, char in enumerate(string_literal, 1):
            machine_code.append({"index": index + symbol_index, "arg": ord(char)})

    return machine_code

def main(input_filepath, output_filepath):
    with open(input_filepath, encoding="utf-8") as file:
        source_code = file.read()

    compiled_code = translate_text(source_code)

    save_instructions_to_file(output_filepath, compiled_code)
    variable_table.clear()
    buffer_declaration_list.clear()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise TranslatorArgumentsError
    _, input_file, output_file = sys.argv
    main(input_file, output_file)
