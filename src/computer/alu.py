ALU_OPERATIONS = [
    # ADD - 0
    lambda x, y: x + y,
    # SUBTRACT - 1
    lambda x, y: x - y,
    # MULTIPLY - 2
    lambda x, y: x * y,
    # DIVIDE - 3
    lambda x, y: x // y,
    # MODULO - 4
    lambda x, y: x % y,
    # NOT EQUAL - 5
    lambda x, y: x != y,
    # EQUAL - 6
    lambda x, y: x == y,
    # LESS THAN - 7
    lambda x, y: x < y,
    # GREATER THAN - 8
    lambda x, y: x > y,
]

MAX_INT = 2**31 - 1
MIN_INT = -(2**31)

class ALU:
    def __init__(self):
        self.negative_flag = 0  
        self.zero_flag = 0  
        self.overflow_flag = 0  
        self.result = 0  
        self.first_operand = 0  
        self.second_operand = 0  

    def execute_operation(self, operation_index):
        operation = ALU_OPERATIONS[operation_index]
        result = operation(self.first_operand, self.second_operand)
        self.result = self.apply_flags(result)

    def apply_flags(self, result):
        self.negative_flag = 0
        self.zero_flag = 0
        self.overflow_flag = 0

        if result < 0:
            self.negative_flag = 1

        if result == 0:
            self.zero_flag = 1

        if result < MIN_INT:
            result %= abs(MIN_INT)
            self.overflow_flag = 1
        elif result > MAX_INT:
            result %= MAX_INT
            self.overflow_flag = 1

        return result
