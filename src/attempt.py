from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction, ThreeRegInstruction, LoadStoreInstruction

class SuperscalarOutOrder(InstructionScheduler):
    def __init__(self, functional_units=4, max_issue=2):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue
        self.pending_instructions = []

    def schedule(self):
        attempted_issues = 0

        # Try to issue pending instructions first
        for pending in self.pending_instructions[:]:
            if (len(self.instructions_in_progress) < self.functional_units and 
                attempted_issues < self.max_issue_per_cycle):
                if self.__is_ready_to_execute(pending):
                    self.__issue_instruction(pending)
                    self.pending_instructions.remove(pending)
                    attempted_issues += 1
                
        # Try to issue new instructions
        for instruction in self.instructions[:]:
            if (len(self.instructions_in_progress) < self.functional_units and 
                attempted_issues < self.max_issue_per_cycle):
                if self.__is_ready_to_execute(instruction):
                    self.__issue_instruction(instruction)
                    self.instructions.remove(instruction)
                else:
                    # Add to pending if can't issue due to dependencies
                    self.pending_instructions.append(instruction)
                    self.instructions.remove(instruction)
                attempted_issues += 1

    def __issue_instruction(self, instruction):
        """Issue an instruction"""
        instruction.issue_cycle = self.current_cycle
        instruction.exp_completion = self.current_cycle + instruction.latency()
        instruction.started = True
        self.instructions_in_progress.append(instruction)

    def __is_ready_to_execute(self, instruction):
        """Check if instruction is ready to execute by checking all dependencies"""
        all_instructions = self.instructions_in_progress + self.pending_instructions
        
        # Check RAW dependencies
        if isinstance(instruction, ThreeRegInstruction):
            for instr in all_instructions:
                if instr.dest in [instruction.src1, instruction.src2]:
                    return False

        # Check WAW dependencies
        earlier_instructions = [i for i in all_instructions 
                              if i.issue_cycle < self.current_cycle]
        for instr in earlier_instructions:
            if instruction.dest == instr.dest:
                return False

        # Check WAR dependencies
        for instr in earlier_instructions:
            if isinstance(instr, ThreeRegInstruction):
                if instruction.dest in [instr.src1, instr.src2]:
                    return False

        return True

    def _retire_instructions(self):
        """Retire completed instructions"""
        i = 0
        while i < len(self.instructions_in_progress):
            instr = self.instructions_in_progress[i]
            if self.current_cycle >= instr.exp_completion:
                # Check if there are any earlier instructions that should retire first
                earlier_incomplete = False
                for other in self.instructions_in_progress:
                    if (other.issue_cycle < instr.issue_cycle and 
                        self.current_cycle < other.exp_completion):
                        earlier_incomplete = True
                        break
                
                if not earlier_incomplete:
                    instr.retire(self.current_cycle)
                    self.logger.append(f"{instr.log_status()}")
                    self.instructions_in_progress.pop(i)
                    continue
            i += 1

    def run(self):
        while (self.instructions or self.instructions_in_progress or 
               self.pending_instructions):
            self.execute_cycle()