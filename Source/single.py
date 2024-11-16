from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction
from load_store import LoadStoreInstruction
from three_reg import ThreeRegInstruction

class SingleInOrder(InstructionScheduler):
    def __init__(self, functional_units=1):
        super().__init__(functional_units)
    
    # Method for scheduling instructions 
    def schedule(self):
        # Check for open functional units, and for instructions to schedule 
        if len(self.instructions_in_progress) < self.functional_units and self.instructions:
            instr = self.instructions[0]
            if self.__is_ready_to_execute(instr):
                self._schedule_instruction(instr)
                self.instructions.remove(instr)
    
    def __is_ready_to_execute(self, instruction):
        return self.__check_dependencies(instruction) == DependencyType.NONE
    
    def __check_dependencies(self, instruction):
        for instr in self.instructions_in_progress:
            # RAW (read-after-write) Dependency Checking 
            if (isinstance(instruction, ThreeRegInstruction)) and instr.dest in [instruction.src1, instruction.src2]:
                return DependencyType.RAW
            if instruction.op == "STORE" and instr.dest == instruction.dest:
                return DependencyType.RAW
            
            # WAR (write-after-read) Dependency Checking
            if isinstance(instr, ThreeRegInstruction) and instruction.dest in [instr.src1, instr.src2]:
                return DependencyType.WAW
            
            # WAW (write-after-write) Dependency Checking
            if instruction.dest == instr.dest:
                return DependencyType.WAW

        return DependencyType.NONE
    
    def _retire_instructions(self):
        # Check for completed instructions 
        for instr in self.instructions_in_progress[:]:
            if self.current_cycle >= instr.exp_completion:
                instr.retire(self.current_cycle)
                self.logger.append(f"{instr.log_status()}")
                self.instructions_in_progress.remove(instr)
            else:
                break