from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction, ThreeRegInstruction, LoadStoreInstruction
from rules import RenamingRules

class SuperscalarInOrder_Renaming(InstructionScheduler):
    def __init__(self, functional_units=4, max_issue=2):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue
        self.renaming_rules = RenamingRules()
    
    def schedule(self):
        attempted_issues = 0
        for instruction in self.instructions[:]:
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                if self.__is_ready_to_execute(instruction):
                    instruction.issue_cycle = self.current_cycle
                    instruction.exp_completion = self.current_cycle + instruction.latency()
                    instruction.started = True 
                    self.instructions_in_progress.append(instruction)
                    self.instructions.remove(instruction)
                else:
                    break
    
    def __is_ready_to_execute(self, instruction):
        if (isinstance(instruction, ThreeRegInstruction)):
            instruction.update_registers(self.renaming_rules.rename_map)
        
        if instruction.dest in self.renaming_rules.rename_map:
            self.renaming_rules.remove_rule(instruction.dest)
        
        return self._check_dependencies(instruction) == DependencyType.NONE
    
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
    
    def _check_dependencies(self, instruction):
        for instr in self.instructions_in_progress:
            # RAW is unsolvable
            if isinstance(instruction, ThreeRegInstruction):
                if instr.dest in [instruction.src1, instruction.src2]:
                    return DependencyType.RAW
            
            # WAR try and solve with a renaming rule 
            if isinstance(instr, ThreeRegInstruction):
                if instruction.dest in [instr.src1, instr.src2]:
                    if not self.renaming_rules.create_rule(instruction.dest):
                        return DependencyType.WAR
                    else:
                        instruction.dest = self.renaming_rules.rename_map[instruction.dest]
            
            # WAW try and solve with renaming 
            if instruction.dest == instr.dest:
                if not self.renaming_rules.create_rule(instruction.dest):
                    return DependencyType.WAW
                else:
                    instruction.dest = self.renaming_rules.rename_map[instruction.dest]
                
        return DependencyType.NONE