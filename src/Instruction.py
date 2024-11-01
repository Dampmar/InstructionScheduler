class Instruction:
    def __init__(self, dest, op):
        self.dest = dest
        self.op = op
        self.issue_cycle = None
        self.complete_cycle = None
        self.started = False
    
    def print_instruction(self):
        pass

# Load/Store Instruction Class
class LoadStoreInstruction(Instruction):
    def __init__(self, dest, operation):
        super().__init__(dest, operation)
    
    def print_instruction(self):
        print(f"{self.dest} = {self.op}")

# Three-Register Instruction Class
class ThreeRegInstruction(Instruction):
    def __init__(self, dest, operation, src1, src2):
        super().__init__(dest, operation)
        self.src1 = src1
        self.src2 = src2
        
    def print_instruction(self):
        print(f"{self.dest} = {self.src1} {self.op} {self.src2}")