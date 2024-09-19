import logging
import sys
sys.path.append('..')

from computer import ControlUnit
from memory import DataPath
from exceptions import WrongMachineArgumentsError
from language.instruction import load_instructions_from_file


def main(code_file, input_file):
    code = load_instructions_from_file(code_file)
    with open(input_file, encoding="utf-8") as file:
        inputs = file.read().strip()
        input_token = []
        for char in inputs:
            input_token.append(char)
    for line_number, line in enumerate(code, 0):
        if line["opcode"] == "halt":
            start_of_variables = line_number + 1
            break
    data_path = DataPath(code, input_token, start_of_variables)
    control_unit = ControlUnit(data_path)
    output, inst_count, tick_count = control_unit.run_machine()

    print(f"{''.join(output)}\n\ninstraction_count: {inst_count!s}\ntick: {tick_count!s}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise WrongMachineArgumentsError
    _, code_input, input_file_name, log_name = sys.argv
    logging.getLogger().setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(levelname)s]  %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_name, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    main(code_input, input_file_name)
