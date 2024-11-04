from Instruction import Instruction, LoadStoreInstruction, ThreeRegInstruction
from enum import Enum, auto
# Dependencies
class DependencyType(Enum):
    NONE = auto()
    RAW = auto()
    WAR = auto()
    WAW = auto()

# Parent Instruction Scheduler
class InstructionScheduler_NoRenaming:
    def __init__(self, functional_units=1):
        self.instructions = []
        self.funcUnits = functional_units
        self.cycle_count = 0
        self.currently_executing = []
        self.log = []
    
    def addInstruction(self, instruction):
        self.instructions.append(instruction)

    def schedule(self):
        raise NotImplementedError("Must be implemented in subclass")

    def execute_cycle(self):
        self.cycle_count += 1
        #self.log.append(f"Cycle {self.cycle_count} start:")
        self._check_completions()
        #self.log.append("  Executing Instructions:")
        self.schedule()
        #for instr in self.currently_executing:
        #    self.log.append(f"    {instr.log_status()}")
        #self.log.append(f"Cycle {self.cycle_count} end.")
    
    def _check_completions(self):
        completed = [instr
                     for instr in self.currently_executing
                     if self.cycle_count >= instr.complete_cycle]
        for instr in completed:
            self.log.append(f"{instr.log_status()}")

        self.currently_executing = [instr 
                                    for instr in self.currently_executing
                                    if self.cycle_count < instr.complete_cycle
                                    ]
    
    def is_ready_to_execute(self, instruction):
        dependency = self._check_dependencies(instruction)
        return dependency == DependencyType.NONE

    def _check_dependencies(self, instruction):
        for instr_inProcess in self.currently_executing:
            # RAW: If current instruction uses a register being written by an executing instruction
            if isinstance(instruction, ThreeRegInstruction):
                if instr_inProcess.dest in [instruction.src1, instruction.src2]:
                    return DependencyType.RAW
            
            # WAR: If current instruction writes to a register being read by an executing instruction
            if isinstance(instr_inProcess, ThreeRegInstruction):
                if instruction.dest in [instr_inProcess.src1, instr_inProcess.src2]:
                    return DependencyType.WAR
            
            # WAW: If current instruction writes to a register being written by an executing instruction
            if instruction.dest == instr_inProcess:
                return DependencyType.WAW
        
        return DependencyType.NONE
    
    def run(self):
        while self.instructions or self.currently_executing:
            self.execute_cycle()
