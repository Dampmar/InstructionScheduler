class Instruction:
    def __init__(self, dest, op):
        self.dest = dest
        self.op = op
        self.issue_cycle : int = None 
        self.exp_completion : int = None 
        self.started : bool = False 
        self.retired_cycle : int = 0 
    
    def print_instruction(self):
        raise NotImplementedError("Must be implemented in subclass")

    # Method for saving scheduling information 
    def log_status(self):
        raise NotImplementedError("Must be implemented in subclass")
    
    def update_registers(self, renaming_rules):
        raise NotImplementedError("Must be implemented in subclass")
    
    # Method to retire instructions 
    def retire(self, cycle):
        self.retired_cycle = cycle

    # Method for retrieving instructions latencies 
    def latency(self):
        if self.op in ['+', '-']:
            return 1
            #return 2
        elif self.op == '*':
            return 2
            #return 3
        elif self.op in ['LOAD', 'STORE']:
            return 3
        else:
            raise NotImplementedError("Invalid instruction type")