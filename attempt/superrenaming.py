from scheduler import InstructionScheduler, DependencyType
from instruction import Instruction, ThreeRegInstruction, LoadStoreInstruction

class SuperscalarInOrder_Renaming(InstructionScheduler):
    def __init__(self, functional_units=4, max_issue=2, num_physical_regs=16):
        super().__init__(functional_units)
        self.max_issue_per_cycle = max_issue
        
        # Register Renaming Structures
        self.num_physical_regs = num_physical_regs
        self.rat = {}  # Register Allocation Table (logical -> physical)
        self.physical_to_arch_map = {}  # Reverse map for retiring registers
        self.free_list = [f's{i}' for i in range(num_physical_regs)]  # Physical register names like 's0', 's1', etc.

    def schedule(self):
        attempted_issues = 0
        scheduled_instructions = []

        for instruction in self.instructions:
            if len(self.instructions_in_progress) < self.functional_units and attempted_issues < self.max_issue_per_cycle:
                attempted_issues += 1
                if self.__is_ready_to_execute(instruction):
                    # Rename registers before issuing
                    self.__rename_registers(instruction)
                    
                    instruction.issue_cycle = self.current_cycle
                    instruction.exp_completion = self.current_cycle + instruction.latency()
                    instruction.started = True
                    self.instructions_in_progress.append(instruction)
                    scheduled_instructions.append(instruction)
                else:
                    break

        for instruction in scheduled_instructions:
            self.instructions.remove(instruction)

    def __is_ready_to_execute(self, instruction):
        return self.check_dependencies(instruction) == DependencyType.NONE

    def check_dependencies(self, instruction):
        """Check for RAW dependencies (WAR and WAW resolved by register renaming)."""
        for instr in self.instructions_in_progress:
            # RAW: if current instruction uses a register being written by an executing instruction
            if isinstance(instruction, ThreeRegInstruction):
                if instr.dest in [instruction.src1, instruction.src2]:
                    return DependencyType.RAW
        
        return DependencyType.NONE

    def __rename_registers(self, instruction):
        """Rename registers using the Register Allocation Table (RAT) and free list."""
        if isinstance(instruction, ThreeRegInstruction):
            # Rename source registers
            if instruction.src1 in self.rat:
                instruction.src1 = self.rat[instruction.src1]
            if instruction.src2 in self.rat:
                instruction.src2 = self.rat[instruction.src2]

            # Rename destination register
            if instruction.dest:
                if self.free_list:
                    # Allocate a new physical register for the destination
                    new_phys_reg = self.free_list.pop(0)
                    self.rat[instruction.dest] = new_phys_reg
                    self.physical_to_arch_map[new_phys_reg] = instruction.dest
                    instruction.dest = new_phys_reg

    def _retire_instructions(self):
        """Handle retiring instructions and freeing physical registers."""
        completed = []

        for instr in self.instructions_in_progress:
            if self.current_cycle >= instr.exp_completion:
                instr.retire(self.current_cycle)
                self.logger.append(f"{instr.log_status()}")
                completed.append(instr)
                
                # Free the physical register and update the RAT on retirement
                if instr.dest in self.physical_to_arch_map:
                    logical_reg = self.physical_to_arch_map[instr.dest]
                    self.free_list.append(instr.dest)
                    del self.physical_to_arch_map[instr.dest]
                    if logical_reg in self.rat:
                        del self.rat[logical_reg]

        for instr in completed:
            self.instructions_in_progress.remove(instr)
