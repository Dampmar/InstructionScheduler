from scheduler import InstructionScheduler, DependencyType
from three_reg import ThreeRegInstruction
from instruction import Instruction
from load_store import LoadStoreInstruction

class SuperscalarOutOrder(InstructionScheduler):
    def __init__(self, functional_units, max_issue):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue            # Issue slots available
        self.pending_instructions = []                  # Pending instructions list 
    
    def schedule(self):
        attempted_issues = 0
        # Try to issue pending instructions first from the pending instructions list
        for pending in self.pending_instructions[:]:
            # Check capacity
            if len(self.instructions_in_progress) < self.functional_units:
                # Check if the pending instruction is ready to execute, dependencies have been resolved
                if self.__is_ready_to_execute_from_pending_instructions(pending):
                    # Schedule the instruction, and remove it from the list 
                    self._schedule_instruction(pending)
                    self.pending_instructions.remove(pending)

        # Try to issue new instructions that haven't been overlooked before
        for instruction in self.instructions[:]:
            # Check capacity
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                # Check if it can be scheduled
                if self.__is_ready_to_execute_from_instructions(instruction):
                    # Schedule the instruction and remove it from the list
                    self._schedule_instruction(instruction)
                    self.instructions.remove(instruction)
                else:
                    # Add it to pending instructions to wait for dependencies to resolve
                    self.pending_instructions.append(instruction)
                    self.instructions.remove(instruction)
    
    def __is_ready_to_execute_from_instructions(self, instruction):
        """
        To check if an instruction from the main list can be issued:
            1. It shouldn't have any dependencies with in-progress instructions
            2. It shouldn't have any dependencies with pending instructions
        This checking prevents data hazards from propagating or for instructions to be performed without the correct values
        """
        if self.__check_dependencies(instruction, self.instructions_in_progress) != DependencyType.NONE:
            return False

        if self.__check_dependencies(instruction, self.pending_instructions) != DependencyType.NONE:
            return False
        
        return True
    
    def __is_ready_to_execute_from_pending_instructions(self, instruction):
        """
        To schedule an instruction from the pending instructions list 
            - It shouldn't write to a register before past instructions write to that same register
            - It shouldn't write to a register before past instructions read from that same register
        These two cases would break the logic due to altering the end results of procedures, thus we must revise them
        """
        if self.__check_dependencies(instruction, self.instructions_in_progress) != DependencyType.NONE:
            return False
        
        # Different Format since it should only check instructions that came before itself
        if self.__check_dependencies(instruction, self.pending_instructions) != DependencyType.NONE:
            return False
        
        return True

    # Check data dependencies between instruction and list of instructions
    def __check_dependencies(self, instruction, list_of_instructions):
        for instr in list_of_instructions:
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
        """
        This method is in charge of retiring instructions out of order, achieves this by:
            1. Iterating through all instructions in progress.
            2. Checking if the instruction is modifying a register that is being read to or written by past instructions (This would break the programs desired functionality).
            3. If not, it may retire.
        """
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
                if instr.dest == instruction.dest and instruction.op != 'STORE':
                    return False
            
        return True 

    # Overwritten method, we must check that pending instructions are also scheduled and completed.
    def run(self):
        while self.instructions or self.instructions_in_progress or self.pending_instructions:
            self.execute_cycle()