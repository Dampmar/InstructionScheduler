from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction, ThreeRegInstruction, LoadStoreInstruction
from rules import RenamingRules

class SingleInOrder_Renaming(InstructionScheduler):
    def __init__(self, functional_units=1):
        super().__init__(functional_units)
        self.renaming_rules = RenamingRules()
    
    # Same format as before
    def schedule(self):
        if len(self.instructions_in_progress) < self.functional_units and self.instructions:
            issued_instruction = self.instructions[0]
            if self.__is_ready_to_execute(issued_instruction):
                # Issue instruction, if ready
                issued_instruction.issue_cycle = self.current_cycle
                issued_instruction.exp_completion = self.current_cycle + issued_instruction.latency()
                issued_instruction.started = True
                self.instructions_in_progress.append(issued_instruction)
                self.instructions.remove(issued_instruction) 
    
    def __is_ready_to_execute(self, instruction):
        # Modify the Source Registers for Three Register Instructions
        if (isinstance(instruction, ThreeRegInstruction)):
            instruction.update_registers(self.renaming_rules.rename_map)
        
        # Modify the Source Register for STORE instructions
        if isinstance(instruction, LoadStoreInstruction) and (instruction.op == "STORE"):
            instruction.update_register(self.renaming_rules.rename_map)
        # Check if the instruction Destination is in the rename map if not a STORE instruction
        elif instruction.dest in self.renaming_rules.rename_map:
            self.renaming_rules.remove_rule(instruction.dest)
        
        return self._check_dependencies(instruction) == DependencyType.NONE
    
    def _check_dependencies(self, instruction):
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