from scheduler import InstructionScheduler, DependencyType
from instructions import Instruction, ThreeRegInstruction, LoadStoreInstruction

class SuperscalarInOrder(InstructionScheduler):
    def __init__(self, max_issue=2, functional_units=4):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue
    
    def schedule(self):
        attempted_issues = 0
        scheduled_in_cycle = []
        
        # Loop through instructions, respecting max issue and functional units limits
        for instruction in self.instructions:
            # Check if scheduling is appropiate
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                if self.__is_ready_to_execute(instruction):
                    instruction.issue_cycle = self.current_cycle
                    instruction.exp_completion = self.current_cycle + instruction.latency()
                    instruction.started = True

                    self.instructions_in_progress.append(instruction)
                    scheduled_in_cycle.append(instruction)
            # Break if there is no space or the max number of issues has been tried
            else:
                break  
        
        # Remove scheduled instructions 
        #for instr in scheduled_in_cycle:
        #    self.instructions.remove(instr)
        #
        #    if len(self.instructions_in_progress) >= self.functional_units or  attempted_issues >= self.max_issue_per_cycle:
        #        break

                
        #    attempted_issues += 1
        #    if self.__is_ready_to_execute(instruction):
        #        instruction.issue_cycle = self.current_cycle
        #        instruction.exp_completion = self.current_cycle + instruction.latency()
        #        instruction.started = True

                # Append the instructions to the instructions_in_progress of the scheduler
        #        self.instructions_in_progress.append(instruction)

                # Set it to remove later on 
        #        instructions_to_remove.append(instruction)
        
        
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
        retired = []
        for instruction in self.instructions_in_progress:
            if instruction.exp_completion > self.current_cycle:
                break
            else:
                instruction.retire(self.current_cycle)
                self.logger.append(f"{instruction.log_status()}")
                retired.append(instruction)
            
        for instr in retired:
            self.instructions_in_progress.remove(instr)

        #while self.instructions_in_progress and self._check_inorder_retirement(self.instructions_in_progress[0]):
            #self.instructions_in_progress[0].retire(self.current_cycle)
            #self.logger.append(self.instructions_in_progress[0].log_status)
            #self.instructions_in_progress.pop()

            #instr = self.instructions_in_progress.pop(0)
            #instr.retire(self.current_cycle)
            #self.logger.append(instr.log_status())
    
    #def _check_inorder_retirement(self, instruction):
        #if self.current_cycle >= instruction.exp_completion:
        #    return True
        #else:
        #    return False 
