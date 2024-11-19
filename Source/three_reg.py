from instruction import Instruction

# Three Register Instructions [+,-,*] format => R1 = R2 + R3, etc...
class ThreeRegInstruction(Instruction):
    def __init__(self, dest, operation, src1, src2):
        super().__init__(dest, operation)
        self.src1 = src1                    # Adding Source Register 1
        self.src2 = src2                    # Adding Source Register 2
    
    # Printing instructions for debugging 
    def print_instruction(self):
        print(f"{self.dest} = {self.src1} {self.op} {self.src2}")
    
    # Update the registers based on the renaming rules 
    def update_registers(self, renaming_rules):
        if self.src1 in renaming_rules:
            self.src1 = renaming_rules[self.src1]
        if self.src2 in renaming_rules:
            self.src2 = renaming_rules[self.src2]
            
    def log_status(self):
        status = (f"Instruction {self.dest} = {self.src1} {self.op} {self.src2} | Issue Cycle = {self.issue_cycle} | Retired Cycle = {self.retired_cycle}")
        return status 
    