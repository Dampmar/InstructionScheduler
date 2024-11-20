@startuml
enum DependencyType {
    NONE
    RAW
    WAR
    WAW
}

abstract class InstructionScheduler {
    + instructions : List<Instruction>
    + functional_units : int
    + current_cycle : int 
    + instructions_in_progress : List<Instruction>
    + logger : List<Strings>
    - __init__(self, functional_units)
    # {abstract} _retire_instructions(self)
    + execute_cycle(self)
    + run(self)
    + add_instruction(self, instruction)
    + {abstract} schedule(self)
}

class SingleInOrder {
    + renaming_rules : RenamingRules
    - __init__(self, functional_units)
    - __is_ready_to_execute(self, instruction) : bool
    - __check_dependencies(self, instruction) : DependencyType
    # {method} _retire_instructions(self)
    + {method} schedule(self) 
}

class SingleInOrder_Renaming {
    - __init__(self, functional_units)
    - __is_ready_to_execute(self, instruction) : bool
    - __check_dependencies(self, instruction) : DependencyType
    # {method} _retire_instructions(self)
    + {method} schedule(self) 
}

class SuperscalarInOrder {
    + max_issue_per_cycle : int
    - __init__(self, functional_units, max_issue)
    - __is_ready_to_execute(self, instruction) : bool
    - __check_dependencies(self, instruction) : DependencyType
    # {method} _retire_instructions(self)
    + {method} schedule(self) 
}

class SuperscalarInOrder_Renaming {
    + renaming_rules : RenamingRules
    + max_issue_per_cycle : int
    + {method} schedule(self) 
    # {method} _retire_instructions(self)
    - __check_dependencies(self, instruction) : DependencyType
    - __is_ready_to_execute(self, instruction) : bool
    - __init__(self, functional_units, max_issue)
}

class SuperscalarOutOrder {
    + max_issue_per_cycle : int
    + pending_instructions : List<Instructions> 
    + {method} schedule(self) 
    + {method} run(self)
    # {method} _retire_instructions(self)
    - __is_ready_to_execute_from_pending_instructions(self, instruction) : bool
    - __is_ready_to_execute_from_instructions(self, instruction) : bool
    - __check_dependencies(self, instruction, list_of_instructions) : DependencyType
    - __can_retire_instructions(self, instruction) : bool
    - __init__(self, functional_units, max_issue)
}

class SuperscalarOutOrder_Renaming {
    + max_issue_per_cycle : int
    + pending_instructions : List<Instructions> 
    + renaming_rules : RenamingRules
    + {method} schedule(self) 
    + {method} run(self)
    # {method} _retire_instructions(self)
    - __is_ready_to_execute_from_pending_instructions(self, instruction) : bool
    - __is_ready_to_execute_from_instructions(self, instruction) : bool
    - __check_dependencies(self, instruction, list_of_instructions) : DependencyType
    - __can_retire_instructions(self, instruction) : bool
    - __init__(self, functional_units, max_issue)
}

class RenamingRules {
    + rename_map : Dictionary<String, String>
    + max_registers : int 
    + available_physical_regs : set<String>
    - __init__(self, max_registers=8)
    + create_rule(self, logical_register)
    + remove_rule(self, logical_register)
    + apply_renaming(self, register)
    + clear(self)
}

abstract class Instruction {
    + dest : String
    + op : String
    + issue_cycle : int 
    + exp_completion : int 
    + started : bool 
    + retired_cycle : int 
    + {abstract} print_instruction(self)
    + {abstract} log_status(self)
    + {abstract} update_registers(self)
    + retire(self, cycle)
    + latency(self) : int 
    - __init__(self, dest, operation)
}

class LoadStoreInstruction {
    - __init__(self, dest, operation)
    + {method} print_instruction(self)
    + {method} update_registers(self, renaming_rules)
    + {method} log_status(self)
}

class ThreeRegInstruction {
    + src1 : String
    + src2 : String
    - __init__(self, dest, operation, src1, src2)
    + {method} print_instruction(self)
    + {method} update_registers(self, renaming_rules)
    + {method} log_status(self)
}

InstructionScheduler "1" <-- "*" Instruction
SingleInOrder --|> InstructionScheduler
SuperscalarInOrder --|> InstructionScheduler
SuperscalarOutOrder --|> InstructionScheduler
SingleInOrder_Renaming --|> InstructionScheduler
SuperscalarInOrder_Renaming --|> InstructionScheduler
SuperscalarOutOrder_Renaming --|> InstructionScheduler

SingleInOrder_Renaming "1" <-- "1" RenamingRules
SuperscalarInOrder_Renaming "1" <-- "1" RenamingRules
SuperscalarOutOrder_Renaming "1" <-- "1" RenamingRules

ThreeRegInstruction --|> "extends" Instruction
LoadStoreInstruction --|> "extends" Instruction

@enduml