from instruction import Instruction

# Load/Store Instruction format => R1 = LOAD, R2 = STORE, etc...
class LoadStoreInstruction(Instruction):
    def __init__(self, dest, operation):
        super().__init__(dest, operation)
    
    def print_instruction(self):
        print(f"{self.dest} = {self.op}")
    
    # Method used in register renaming 
    def update_registers(self, renaming_rules):
        if self.op == "STORE" and self.dest in renaming_rules:
            self.dest = renaming_rules[self.dest]
    
    # Overwritten method 
    def log_status(self):
        if self.op == "LOAD":
            status = (f'Instruction {self.dest} = {self.op}    | Issue Cycle = {self.issue_cycle} | Retired Cycle = {self.retired_cycle}')
        else:
            status = (f'Instruction {self.dest} = {self.op}   | Issue Cycle = {self.issue_cycle} | Retired Cycle = {self.retired_cycle}')
        return status 