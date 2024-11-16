from enum import Enum, auto
from instruction import Instruction

# Enum type for describing types of dependencies
class DependencyType(Enum):
    NONE = auto()
    RAW = auto()
    WAR = auto()
    WAW = auto()

# Common format for instruction schedulers 
class InstructionScheduler:
    def __init__(self, functional_units=1):
        self.instructions = []
        self.functional_units = functional_units
        self.current_cycle = 0
        self.instructions_in_progress = []
        self.logger = []
    
    def add_instruction(self, instruction):
        self.instructions.append(instruction)
    
    def schedule(self):
        raise NotImplementedError("Implemented in Subclass")
    
    def _retire_instructions(self):
        raise NotImplementedError("Implemented in Subclass")

    # Execute a cycle, increment, check for possible retirements, and schedule instructions
    def execute_cycle(self):
        self.current_cycle += 1
        self.schedule()
        self._retire_instructions()

    # Run while instructions being processed 
    def run(self):
        while self.instructions or self.instructions_in_progress:
            self.execute_cycle()
    
    # Method to schedule instructions 
    def _schedule_instruction(self, instr : Instruction):
        instr.issue_cycle = self.current_cycle
        instr.exp_completion = self.current_cycle + instr.latency()
        instr.started = True 
        self.instructions_in_progress.append(instr)