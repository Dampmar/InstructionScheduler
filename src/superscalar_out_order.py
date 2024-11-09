from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction, ThreeRegInstruction, LoadStoreInstruction

class SuperscalarOutOrder(InstructionScheduler):
    def __init__(self, functional_units=4, max_issue=2):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue
        self.pending_instructions = []

    def schedule(self):
        attempted_issues = 0

        # Try to issue pending instructions first from the pending instructions list

        for pending in self.pending_instructions[:]:
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                if self.__is_ready_to_execute_from_pending_instructions(pending):
                    pending.issue_cycle = self.current_cycle
                    pending.exp_completion = self.current_cycle + pending.latency()
                    pending.started = True 
                    self.instructions_in_progress.append(pending)
                    self.pending_instructions.remove(pending)
                    attempted_issues+=1
                    print("issuing")
                
        # Issue new instructions from the main list if there is still capacity
        for instruction in self.instructions[:]:
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                if self.__is_ready_to_execute_from_instructions(instruction):
                    instruction.issue_cycle = self.current_cycle
                    instruction.exp_completion = self.current_cycle + instruction.latency()
                    instruction.started = True
                    self.instructions_in_progress.append(instruction)
                    self.instructions.remove(instruction)
                    print("issuing")
                else:
                    self.pending_instructions.append(instruction)
                    self.instructions.remove(instruction)
                    print("pending")
    
    def __is_ready_to_execute_from_instructions(self, instruction):
        """
        Checks if the given instruction is ready to execute. 
        It needs to check for dependencies with both in-progress and pending instructions.
        """
        # Check for dependencies against currently executing instructions
        if self.check_dependencies(instruction, self.instructions_in_progress) != DependencyType.NONE:
            return False

        # Check for dependencies against other pending instructions
        if self.check_dependencies(instruction, self.pending_instructions) != DependencyType.NONE:
            return False
        
        return True
    
    def __is_ready_to_execute_from_pending_instructions(self, instruction):
        # Check for dependencies against currently executing instructions
        if self.check_dependencies(instruction, self.instructions_in_progress) != DependencyType.NONE:
            return False
        
        return True

    def check_dependencies(self, instruction, other_instructions):
        """ Check if the given instruction has any unresolved dependencies """
        for instr in other_instructions:
            # RAW: Reading a register that is still being written 
            if isinstance(instruction, ThreeRegInstruction):
                if instr.dest in [instruction.src1, instruction.src2]:
                    return DependencyType.RAW
            # WAR Dependency: Writing to a register that is being read by another instruction
            if isinstance(instr, ThreeRegInstruction):
                if instruction.dest in [instr.src1, instr.src2]:
                    return DependencyType.WAR

            # WAW Dependency: Writing to a register that another instruction is writing to
            if instruction.dest == instr.dest:
                return DependencyType.WAW

        return DependencyType.NONE
    
    def _retire_instructions(self):
        """ Retire instructions once they are completed and have no unresolved dependencies """
        i = 0
        while i < len(self.instructions_in_progress):
            instr = self.instructions_in_progress[i]
            if self.current_cycle >= instr.exp_completion and self.__can_retire_instructions(instr):
                instr.retire(self.current_cycle)
                self.logger.append(f"{instr.log_status()}")
                self.instructions_in_progress.pop(i)
            else: 
                i += 1

    def __can_retire_instructions(self, instruction):
        """Determine if the instruction can retire without conflicts."""
        for instr in self.instructions_in_progress:
            if instr.issue_cycle < instruction.issue_cycle:
                # Check for WAW and WAR hazards, before retiring
                if instr.dest == instruction.dest:
                    return False 
                if isinstance(instr, ThreeRegInstruction):
                    if instruction.dest in [instr.src1, instr.src2]:
                        return False
        
        return True 
    
    # Run while instructions being processed 
    def run(self):
        while self.instructions or self.instructions_in_progress or self.pending_instructions:
            self.execute_cycle()
        print("done")