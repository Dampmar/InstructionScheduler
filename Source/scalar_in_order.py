from scheduler import InstructionScheduler, DependencyType
from three_reg import ThreeRegInstruction
from instruction import Instruction
from load_store import LoadStoreInstruction

class SuperscalarInOrder(InstructionScheduler):
    def __init__(self, functional_units=4, max_issue=2):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue                # Issue Slots available 
    
    def schedule(self):
        """ This method looks to schedule instructions, iteratively unless it has no more issue slots, or if there is no more space """
        attempted_issues = 0
        for instruction in self.instructions[:]:
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                if self.__is_ready_to_execute(instruction):
                    self._schedule_instruction(instruction)
                    self.instructions.remove(instruction)
                else:
                    break
    
    def __is_ready_to_execute(self, instruction):
        """Can only issue an instruction if it has no data dependencies with in-progress instructions"""
        return self.__check_dependencies(instruction) == DependencyType.NONE

    def __check_dependencies(self, instruction):
        for instr in self.instructions_in_progress:
            if instr == instruction:
                return DependencyType.NONE
            
            if instr.op == 'STORE' and instruction.op == "STORE":
                continue

            # RAW Dependency Checking 
            if isinstance(instruction, ThreeRegInstruction):
                if instr.dest in [instruction.src1, instruction.src2] and instr.op !=  "STORE":
                    return DependencyType.RAW
            if isinstance(instruction, LoadStoreInstruction) and instruction.op == "STORE":
                if instr.dest == instruction.dest:
                    return DependencyType.RAW
            
            # WAR Dependency Checking 
            if isinstance(instr, ThreeRegInstruction): 
                if instruction.dest in [instr.src1, instr.src2] and instruction.op != "STORE":
                    return DependencyType.WAR
            if instr.op == "STORE" and instr.dest == instruction.dest:
                    return DependencyType.WAR
            
            # WAW Dependency Checking 
            if instruction.op != "STORE" and instruction.dest == instr.dest:
                return DependencyType.WAW

        return DependencyType.NONE
    
    def _retire_instructions(self):
        """In-order retirement"""
        # Check for completed instructions 
        for instr in self.instructions_in_progress[:]:
            if self.current_cycle >= instr.exp_completion:
                instr.retire(self.current_cycle)
                self.logger.append(f"{instr.log_status()}")
                self.instructions_in_progress.remove(instr)
            else:
                break