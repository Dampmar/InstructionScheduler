class Instruction:
    def __init__(self, dest, op):
        self.dest = dest
        self.op = op
        self.issue_cycle = None
        self.complete_cycle = None
        self.started = False
    
    def print_instruction(self):
        raise NotImplementedError('Must be implemented in subclasses')

    def latency(self):
        if self.op in ['+', '-']:
            return 1
        elif self.op == '*':
            return 2
        elif self.op in ['LOAD', 'Store']:
            return 3
        else:
            return 1
    
    def log_status(self):
        raise NotImplementedError('Must be implemented in subclasses')
        
# Load/Store Instruction Class
class LoadStoreInstruction(Instruction):
    def __init__(self, dest, operation):
        super().__init__(dest, operation)
    
    def print_instruction(self):
        print(f"{self.dest} = {self.op}")
    
    def log_status(self):
        if self.op == 'LOAD':
            status = (f"Instruction {self.dest} = {self.op}    | Issue Cycle = {self.issue_cycle} | Retired Cycle = {self.complete_cycle}")
        elif self.op == 'STORE':
            status = (f"Instruction {self.dest} = {self.op}   | Issue Cycle = {self.issue_cycle} | Retired Cycle = {self.complete_cycle}")
        return status

# Three-Register Instruction Class
class ThreeRegInstruction(Instruction):
    def __init__(self, dest, operation, src1, src2):
        super().__init__(dest, operation)
        self.src1 = src1
        self.src2 = src2
        
    def print_instruction(self):
        print(f"{self.dest} = {self.src1} {self.op} {self.src2}")
    
    def log_status(self):
        status = (f"Instruction {self.dest} = {self.src1} {self.op} {self.src2} | Issue Cycle = {self.issue_cycle} | Retired Cycle = {self.complete_cycle}")
        return status 