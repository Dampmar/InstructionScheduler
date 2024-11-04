from InstructionScheduler import InstructionScheduler_NoRenaming

class SingleInOrder(InstructionScheduler_NoRenaming):
    def schedule(self):
        if len(self.currently_executing) < self.funcUnits:
            for instruction in self.instructions:
                if self.is_ready_to_execute(instruction):
                    instruction.issue_cycle = self.cycle_count
                    instruction.complete_cycle = self.cycle_count + instruction.latency()
                    instruction.started = True
                    self.currently_executing.append(instruction)
                    self.instructions.remove(instruction)
                    break