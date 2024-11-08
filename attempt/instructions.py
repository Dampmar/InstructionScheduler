class Instruction:
    def __init__(self, dest, op):
        self.dest = dest
        self.op = op 
        self.issue_cycle = None
        self.exp_completion = None 
        self.started = False 
        self.retired_cycle : int = 0 
    
    def print_instruction(self):
        raise NotImplementedError("Implemented in subclass")
    
    def latency(self):
        if self.op in ['+', '-']:
            return 2
            return 1
        elif self.op == '*':
            return 3 
            return 2
        elif self.op in ['LOAD', 'STORE']:
            return 3
        else:
            raise NotImplementedError("Invalid instructions type")
    
    def log_status(self):
        raise NotImplementedError("Implemented in subclass")
    
    def retire(self, cycle: int):
        self.retired_cycle = cycle

class LoadStoreInstruction(Instruction):
    def __init__(self, dest, operation):
        super().__init__(dest, operation)
    
    def print_instruction(self):
        print(f"{self.dest} = {self.op}")
    
    def log_status(self):
        status = (f'Instruction {self.dest} = {self.op} | Cycle = {self.issue_cycle} | Retired Cycle = {self.retired_cycle}')
        return status 

class ThreeRegInstruction(Instruction):
    def __init__(self, dest, operation, src1, src2):
        super().__init__(dest, operation)
        self.src1 = src1
        self.src2 = src2 
    
    def print_instruction(self):
        print(f"{self.dest} = {self.src1} {self.op} {self.src2}")
    
    def log_status(self):
        status = (f"Instruction {self.dest} = {self.src1} {self.op} {self.src2} | Issue Cycle = {self.issue_cycle} | Retired Cycle = {self.retired_cycle}")
        return status 