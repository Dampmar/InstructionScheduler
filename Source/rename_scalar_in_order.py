from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction
from load_store import LoadStoreInstruction
from three_reg import ThreeRegInstruction
from rules import RenamingRules

class SuperscalarInOrder_Renaming(InstructionScheduler):
    def __init__(self, functional_units=4, max_issue=2):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue                # Issue Slots
        self.renaming_rules = RenamingRules()               # Renaming Rules
    
    def schedule(self):
        """Same format as the one with no renaming"""
        attempted_issues = 0
        for instruction in self.instructions[:]:
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                if self.__is_ready_to_execute(instruction):
                    self._schedule_instruction(instruction)
                    self.instructions.remove(instruction)
                else:
                    break

    def __is_ready_to_execute(self, instr : Instruction):
        """Method has been modified to update registers, based on renmaing rules; and remove rules that no longer apply"""
        instr.update_registers(self.renaming_rules.rename_map)

        if instr.op != "STORE" and instr.dest in self.renaming_rules.rename_map:
            self.renaming_rules.remove_rule(instr.dest)
        
        return self.__check_dependencies(instr) == DependencyType.NONE
    
    def __check_dependencies(self, instruction):
        for instr in self.instructions_in_progress:
            if instr.op == 'STORE' and instruction.op == "STORE":
                continue
            # RAW Dependency (Read-After-Write)
            if isinstance(instruction, ThreeRegInstruction):
                if instr.dest in [instruction.src1, instruction.src2] and instr.op !=  "STORE":
                    return DependencyType.RAW
        
            # For STORE instructions, treat the 'dest' register as a source
            if isinstance(instruction, LoadStoreInstruction) and instruction.op == "STORE":
                if instr.dest == instruction.dest:
                    return DependencyType.RAW  # Reading from a register that is being written to by another instruction

            # WAR Dependency (Write-After-Read) - try to solve with renaming
            if isinstance(instr, ThreeRegInstruction):
                if instruction.dest in [instr.src1, instr.src2] and instruction.op != "STORE":
                    if not self.renaming_rules.create_rule(instruction.dest):
                        return DependencyType.WAR
                    else:
                        instruction.dest = self.renaming_rules.rename_map[instruction.dest]
            if instr.op == "STORE" and instr.dest == instruction.dest and instruction.op != "STORE":
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
        # Check for completed instructions 
        for instr in self.instructions_in_progress[:]:
            if self.current_cycle >= instr.exp_completion:
                instr.retire(self.current_cycle)
                self.logger.append(f"{instr.log_status()}")
                self.instructions_in_progress.remove(instr)
            else:
                break