from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction, ThreeRegInstruction, LoadStoreInstruction

class SuperscalarInOrder(InstructionScheduler):
    def __init__(self, functional_units=4, max_issue=2):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue

    def schedule(self):
        attempted_issues = 0
        scheduled_instructions = []

        for instruction in self.instructions:
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                if self.__is_ready_to_execute(instruction):
                    instruction.issue_cycle = self.current_cycle 
                    instruction.exp_completion = self.current_cycle + instruction.latency()
                    instruction.started = True 
                    self.instructions_in_progress.append(instruction)
                    scheduled_instructions.append(instruction)
                else:
                    break
        
        for instruction in scheduled_instructions:
            self.instructions.remove(instruction)
        
    def __is_ready_to_execute(self, instruction):
        return self.check_dependencies(instruction) == DependencyType.NONE
    
    def check_dependencies(self, instruction):
        for instr in self.instructions_in_progress:
            # RAW: if current instruction uses a register being written by an executing instruction
            if isinstance(instruction, ThreeRegInstruction):
                if instr.dest in [instruction.src1, instruction.src2]:
                    return DependencyType.RAW
            
            # WAR: If current instruction writes to a register being read by an executing instruction 
            if isinstance(instr, ThreeRegInstruction):
                if instruction.dest in [instr.src1, instr.src2]:
                    return DependencyType.WAR
            
            # WAW: If current instruction writes to a register being written by an executing instruction
            if instruction.dest == instr.dest:
                return DependencyType.WAW
        
        return DependencyType.NONE
    
    def _retire_instructions(self):
        # Completed instructions 
        completed = []

        # Check for completed instructions 
        for instr in self.instructions_in_progress:
            if self.current_cycle >= instr.exp_completion:
                instr.retire(self.current_cycle)            # Retire instruction
                self.logger.append(f"{instr.log_status()}")    # Log the status 
                completed.append(instr)
            else:
                break
            
        # Officially remove those instructions from in progress 
        for instr in completed:
            self.instructions_in_progress.remove(instr)