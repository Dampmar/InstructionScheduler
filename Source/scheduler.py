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
        self.instructions = []                      # All instructions
        self.functional_units = functional_units    # Number of functional units
        self.current_cycle = 0                      # Current Cycle when Scheduling
        self.instructions_in_progress = []          # Instructions being executed in functional units
        self.logger = []                            # Logger to keep track of instructions
    
    def add_instruction(self, instruction):
        self.instructions.append(instruction)
    
    # Method should be implemented in subclass, every instructions scheduler format schedules instructions differently
    def schedule(self):
        raise NotImplementedError("Implemented in Subclass")
    
    # Method should be implemented in subclass, again every scheduler retires them differently
    def _retire_instructions(self):
        raise NotImplementedError("Implemented in Subclass")

    # Execute a cycle => increment cycle, schedule instructions, and retire them
    def execute_cycle(self):
        self.current_cycle += 1
        self.schedule()
        self._retire_instructions()

    # This method is in charge of coordinating the overall scheduling
    def run(self):
        while self.instructions or self.instructions_in_progress:
            self.execute_cycle()
    
    # Scheduling of instructions is the same for all
    def _schedule_instruction(self, instr : Instruction):
        instr.issue_cycle = self.current_cycle
        instr.exp_completion = self.current_cycle + instr.latency()
        instr.started = True 
        self.instructions_in_progress.append(instr)