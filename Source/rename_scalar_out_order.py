from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction
from load_store import LoadStoreInstruction
from three_reg import ThreeRegInstruction
from rules import RenamingRules

class SuperscalarOutOrder_Renaming(InstructionScheduler):
    def __init__(self, functional_units, max_issue):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue
        self.pending_instructions = []
        self.renaming_rules = RenamingRules()

    def schedule(self):
        attempted_issues = 0
        # Try to issue pending instructions first from the pending instructions list
        for pending in self.pending_instructions[:]:
            # Check capacity
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                # Check if the pending instruction is ready to execute, dependencies have been resolved
                if self.__is_ready_to_execute_from_pending_instructions(pending):
                    # Schedule the instruction
                    self._schedule_instruction(pending)
                    self.pending_instructions.remove(pending)
        
        # Try to issue new instructions that haven't been overlooked before
        for instruction in self.instructions[:]:
            # Check capacity
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                # Check if it can be scheduled
                if self.__is_ready_to_execute_from_instructions(instruction):
                    # Schedule the instruction 
                    self._schedule_instruction(instruction)
                    self.instructions.remove(instruction)
                else:
                    # Else, add it to pending instructions to wait for dependencies to resolve
                    self.pending_instructions.append(instruction)
                    self.instructions.remove(instruction)
        
    def __is_ready_to_execute_from_instructions(self, instruction):
        # Apply Renaming Rules
        instruction.update_registers(self.renaming_rules.rename_map)

        if instruction.dest in self.renaming_rules.rename_map and instruction.op != "STORE":
            self.renaming_rules.remove_rule(instruction.dest)
        
        # Check dependencies with pending instructions first
        for instr in self.pending_instructions:
            # Raw Dependency Checking 
            if isinstance(instruction, ThreeRegInstruction) and instr.dest in [instruction.src1, instruction.src2]:
                return False
            if isinstance(instruction, LoadStoreInstruction) and instruction.op == "STORE" and instr.dest == instruction.dest:
                return False
            
            # WAR Dependency Checking 
            if isinstance(instr, ThreeRegInstruction) and instruction.dest in [instr.src1, instr.src2]:
                if not self.renaming_rules.create_rule(instruction.dest):
                    return False
                else:
                    instruction.dest = self.renaming_rules.rename_map[instruction.dest]
            """
            if isinstance(instruction, LoadStoreInstruction) and instruction.op == "STORE":
                if instr.dest == instruction.dest:
                    return False 
            """
            
            # WAW Dependency Checking 
            if instruction.dest == instr.dest:
                if not self.renaming_rules.create_rule(instruction.dest):
                    return False
                else:
                    instruction.dest = self.renaming_rules.rename_map[instruction.dest]
                #return False 
        
        if self._check_dependencies(instruction) != DependencyType.NONE:
            return False 
        else:
            return True 
    
    def __is_ready_to_execute_from_pending_instructions(self, instruction):
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
                        if not self.renaming_rules.create_rule(instruction.dest):
                            return False
                        else:
                            instruction.dest = self.renaming_rules.rename_map[instruction.dest]
                if instr.op == "STORE":
                    if instr.dest == instruction.dest:
                        if not self.renaming_rules.create_rule(instruction.dest):
                            return False
                        else:
                            instruction.dest = self.renaming_rules.rename_map[instruction.dest]
                
                # WAW Dependency Checking 
                if instruction.dest == instr.dest:
                    if not self.renaming_rules.create_rule(instruction.dest):
                        return False
                    else:
                        instruction.dest = self.renaming_rules.rename_map[instruction.dest]
                    #return False
        
        if self._check_dependencies(instruction) != DependencyType.NONE:
            return False
        else:
            return True 
        

    def _check_dependencies(self, instruction):
        for instr in self.instructions_in_progress:
            # RAW Dependency (Read-After-Write)
            if isinstance(instruction, ThreeRegInstruction):
                if instr.dest in [instruction.src1, instruction.src2]:
                    return DependencyType.RAW
        
            # For STORE instructions, treat the 'dest' register as a source
            if isinstance(instruction, LoadStoreInstruction) and instruction.op == "STORE":
                if instr.dest == instruction.dest:
                    return DependencyType.RAW  # Reading from a register that is being written to by another instruction

            # WAR Dependency (Write-After-Read) - try to solve with renaming
            if isinstance(instr, ThreeRegInstruction):
                if instruction.dest in [instr.src1, instr.src2]:
                    if not self.renaming_rules.create_rule(instruction.dest):
                        return DependencyType.WAR
                    else:
                        instruction.dest = self.renaming_rules.rename_map[instruction.dest]
            if instr.op == "STORE" and instr.dest == instruction.dest:
                if not self.renaming_rules.create_rule(instruction.dest):
                    return DependencyType.WAR
                else:
                    instruction.dest = self.renaming_rules.rename_map[instruction.dest]
        
            # WAW Dependency (Write-After-Write) - try to solve with renaming
            if instruction.op != "STORE" and instruction.dest == instr.dest:
                if not self.renaming_rules.create_rule(instruction.dest):
                    return DependencyType.WAW
                else:
                    instruction.dest = self.renaming_rules.rename_map[instruction.dest]
    
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
