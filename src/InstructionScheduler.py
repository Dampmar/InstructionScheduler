from Instruction import Instruction, LoadStoreInstruction, ThreeRegInstruction

class InstructionScheduler:
    def __init__(self, instructions, processor_config):
        self.instructions = instructions
        self.processor_config = processor_config
        self.execution_mode = processor_config["execution mode"]
        self.issue_width = processor_config["issue width"] if self.execution_mode == "superscalar_in_order" else 1
        self.num_funcU = processor_config["num_functional_units"]
        self.cycle = 1
        self.in_flight = []
        self.retired = []
        self.ready_to_issue = [Instruction(*inst) for inst in self.instructions]
                               
