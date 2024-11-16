from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction
from load_store import LoadStoreInstruction
from three_reg import ThreeRegInstruction
from rules import RenamingRules

class SingleInOrder_Renaming(InstructionScheduler):
    def __init__(self, functional_units=1):
        super().__init__(functional_units)
        self.renaming_rules = RenamingRules()
    
    # Same format as before
    def schedule(self):
        if len(self.instructions_in_progress) < self.functional_units and self.instructions:
            instr = self.instructions[0]
            if self.__is_ready_to_execute(instr):
                # Issue instruction, if ready
                self._schedule_instruction(instr)
                self.instructions.remove(instr) 
        
    def __is_ready_to_execute(self, instr : Instruction):
        instr.update_registers(self.renaming_rules.rename_map)

        if instr.op != "STORE" and instr.dest in self.renaming_rules.rename_map:
            self.renaming_rules.remove_rule(instr.dest)
        
        return self.__check_dependencies(instr) == DependencyType.NONE
    
    def __check_dependencies(self, instruction):
        for instr in self.instructions_in_progress:
            # RAW Dependency (Read-After-Write)
            if isinstance(instruction, ThreeRegInstruction):
                if instr.dest in [instruction.src1, instruction.src2]:
                    return DependencyType.RAW
            
            # RAW Dependency (Store Edition), treat the 'dest' register as a source
            if isinstance(instruction, LoadStoreInstruction) and instruction.op == "STORE":
                if instr.dest == instruction.dest:
                    return DependencyType.RAW
            
            # WAR Dependency (Write-After-Read) - try to solve with renaming 
            if isinstance(instr, ThreeRegInstruction):
                if instruction.dest in [instr.src1, instr.src2]:
                    if not self.renaming_rules.create_rule(instruction.dest):
                        return DependencyType.WAR
                    else:        
                        # We could create a renaming rule, apply to the destination register
                        instruction.dest = self.renaming_rules.rename_map[instruction.dest]
            
            # WAW Dependency (Write-After-Write) = try to solve with renaming
            if instruction.op != "STORE" and instruction.dest == instr.dest:
                if not self.renaming_rules.create_rule(instruction.dest):
                    return DependencyType.WAW
                else:
                    instruction.dest = self.renaming_rules.rename_map[instruction.dest]
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