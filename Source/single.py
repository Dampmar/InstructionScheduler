from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction, ThreeRegInstruction, LoadStoreInstruction

class SingleInOrder(InstructionScheduler):
    def __init__(self, functional_units=1):
        super().__init__(functional_units)

    def schedule(self):
        # Check if there are functional units available to process instruction and if there are instructions to execute, else wait 
        if len(self.instructions_in_progress) < self.functional_units and self.instructions:
            # Get first instruction and try and schedule it 
            issued_instruction = self.instructions[0]
            if self.__is_ready_to_execute(issued_instruction):
                # Set the issue_cycle and the expected_completion
                issued_instruction.issue_cycle = self.current_cycle
                issued_instruction.exp_completion = self.current_cycle + issued_instruction.latency()
                issued_instruction.started = True

                # Append the instructions to the instructions_in_progress of the scheduler
                self.instructions_in_progress.append(issued_instruction)

                # Remove the instructions 
                self.instructions.remove(issued_instruction)
                    

    def __is_ready_to_execute(self, instruction):
        return self._check_dependencies(instruction) == DependencyType.NONE

    def _check_dependencies(self, instruction):
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
                instr.retire(self.current_cycle)                # Retire instruction
                self.logger.append(f"{instr.log_status()}")     # Log the status 
                completed.append(instr)
            else:
                break
            
        # Officially remove those instructions from in progress 
        for instr in completed:
            self.instructions_in_progress.remove(instr)

