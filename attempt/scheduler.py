from enum import Enum, auto

class DependencyType(Enum):
    NONE = auto()
    RAW = auto()
    WAR = auto()
    WAW = auto()

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
        #self._retire_instructions()
        self.schedule()
        self._retire_instructions()

    # Run while instructions being processed 
    def run(self):
        while self.instructions or self.instructions_in_progress:
            self.execute_cycle()