from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction, ThreeRegInstruction, LoadStoreInstruction

class SuperscalarOutOrder(InstructionScheduler):
    def __init__(self, functional_units, max_issue):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue
        self.pending_instructions = []

    def schedule(self):
        attempted_issues = 0

        # Try to issue pending instructions first from the pending instructions list
        for pending in self.pending_instructions[:]:
            # Check capacity
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                # Check if the pending instruction is ready to execute, dependencies have been resolved
                if self.__is_ready_to_execute_from_pending_instructions(pending):
                    # Schedule the instruction
                    pending.issue_cycle = self.current_cycle
                    pending.exp_completion = self.current_cycle + pending.latency()
                    pending.started = True 
                    self.instructions_in_progress.append(pending)
                    self.pending_instructions.remove(pending)
                    #attempted_issues += 1
        
        # Try to issue new instructions that haven't been overlooked before
        for instruction in self.instructions[:]:
            # Check capacity
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                # Check if it can be scheduled
                if self.__is_ready_to_execute_from_instructions(instruction):
                    # Schedule the instruction 
                    instruction.issue_cycle = self.current_cycle
                    instruction.exp_completion = self.current_cycle + instruction.latency()
                    instruction.started = True
                    self.instructions_in_progress.append(instruction)
                    self.instructions.remove(instruction)
                else:
                    # Else, add it to pending instructions to wait for dependencies to resolve
                    self.pending_instructions.append(instruction)
                    self.instructions.remove(instruction)
        
    def __is_ready_to_execute_from_instructions(self, instruction):
        """
        To check an instruction from the main list:
            1. It shouldn't have any dependencies with any past instruction, has to revise both in-progress and pending instructions
        """
        if self._check_dependencies(instruction, self.instructions_in_progress) != DependencyType.NONE:
            return False

        if self._check_dependencies(instruction, self.pending_instructions) != DependencyType.NONE:
            return False
        
        return True
    
    def __is_ready_to_execute_from_pending_instructions(self, instruction):
        """
        To schedule an instruction from the pending instructions list 
            - It shouldn't write to a register before past instructions write to that same register
            - It shouldn't write to a register before past instructions read from that same register
        These two cases would break the logic due to altering the end results of procedures, thus we must revise them
        """
        if self._check_dependencies(instruction, self.instructions_in_progress) != DependencyType.NONE:
            return False
        
        # Check for data handling hazards, from the cases stated above
        for instr in self.pending_instructions:
            if instr == instruction:
                break
            else:
                # RAW Dependency Checking
                if isinstance(instruction, ThreeRegInstruction):
                    if instr.dest in [instruction.src1, instruction.src2]:
                        return False
                if isinstance(instr, LoadStoreInstruction) and instr.op == "STORE":
                    if instr.dest == instruction.dest:
                        return False
                
                # WAR Dependency Checking 
                if isinstance(instr, ThreeRegInstruction):
                    if instruction.dest in [instr.src1, instr.src2]:
                        return False
                if isinstance(instruction, LoadStoreInstruction) and instruction.op == "STORE":
                    if instr.dest == instruction.dest:
                        return False
                
                # WAW Dependency Checking 
                if instruction.dest == instr.dest:
                    return False
        
        return True
        
    
    def _check_dependencies(self, instruction, list_of_instructions):
        for instr in list_of_instructions:
            # RAW Dependency Checking 
            if isinstance(instruction, ThreeRegInstruction) and instr.dest in [instruction.src1, instruction.src2]:
                return DependencyType.RAW
            if isinstance(instruction, LoadStoreInstruction) and instruction.op == "STORE" and instr.dest == instruction.dest:
                return DependencyType.RAW
            
            # WAR Dependency Checking 
            if isinstance(instr, ThreeRegInstruction) and instruction.dest in [instr.src1, instr.src2]:
                return DependencyType.WAR
            if isinstance(instruction, LoadStoreInstruction) and instr.op == "STORE":
                if instr.dest == instruction.dest:
                    return DependencyType.WAR
            
            # WAW Dependency Checking 
            if instruction.dest == instr.dest:
                    return DependencyType.WAW

        return DependencyType.NONE
    
    def _retire_instructions(self):
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
        for instr in self.instructions_in_progress:
            if instr.issue_cycle < instruction.issue_cycle:
                if isinstance(instr, ThreeRegInstruction) and instruction.dest in [instr.src1, instr.src2]:
                    return False
                if instr.dest == instruction.dest:
                    return False
            
        return True 
    
    def run(self):
        while self.instructions or self.instructions_in_progress or self.pending_instructions:
            self.execute_cycle()