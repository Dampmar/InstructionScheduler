class Instruction:
    def __init__(self, dest, op):
        self.dest = dest
        self.op = op
        self.issue_cycle = None 
        self.exp_completion = None 
        self.started = False 
        self.retired_cycle : int = 0 
    
    # Print method should be defined based on instruction type 
    def print_instruction(self):
        raise NotImplementedError("Must be implemented in subclass")
    
    # Latencies of instructions based on operation type 
    def latency(self):
        if self.op in ['+', '-']:
            return 1
            # return 2 used to test with class examples
        elif self.op == '*':
            return 2
            # return 3 used to test with class examples 
        elif self.op in ['LOAD', 'STORE']:
            return 3
        else:
            raise NotImplementedError("Invalid instruction type")
        
    # Log status of instruction, what is logged to display the results 
    def log_status(self):
        raise NotImplementedError("Must be implemented in subclass")
    
    # Method to retire instructions called in scheduler's 
    def retire(self, cycle):
        self.retired_cycle = cycle

# Load/Store Instruction format => R1 = LOAD, R2 = STORE, etc...
class LoadStoreInstruction(Instruction):
    def __init__(self, dest, operation):
        super().__init__(dest, operation)
    
    def print_instruction(self):
        print(f"{self.dest} = {self.op}")
    
    def log_status(self):
        status = (f'Instruction {self.dest} = {self.op} | Cycle = {self.issue_cycle} | Retired Cycle = {self.retired_cycle}')
        return status 

# Three Register Instructions [+,-,*] format => R1 = R2 + R3, etc...
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
    
    # Update the registers based on the renaming rules 
    def update_registers(self, renaming_rules):
        if self.src1 in renaming_rules:
            self.src1 = renaming_rules[self.src1]
        if self.src2 in renaming_rules:
            self.src2 = renaming_rules[self.src2]