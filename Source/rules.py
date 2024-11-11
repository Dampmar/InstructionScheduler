class RenamingRules:
    def __init__(self, max_registers=8):
        # Store the mapping of logical registers to physical registers
        self.rename_map = {}
        self.max_registers = max_registers
        self.available_physical_regs = set([f"S{i}" for i in range(0, max_registers)])  # Available physical registers
    
    def create_rule(self, logical_register):
        """Create a renaming rule by assigning a physical register to the logical register."""
        if logical_register not in self.rename_map:
            if not self.available_physical_regs:
                return False  # No available physical registers
            
            # Assign a new physical register from the available ones
            physical_register = self.available_physical_regs.pop()  # Take one register from the available pool
            self.rename_map[logical_register] = physical_register
            return True
        return False

    def remove_rule(self, logical_register):
        """Remove a renaming rule for the logical register."""
        if logical_register in self.rename_map:
            physical_register = self.rename_map.pop(logical_register)
            self.available_physical_regs.add(physical_register)  # Return the register to the available pool
            return True
        return False

    def apply_renaming(self, register):
        """Apply renaming to a register (if it's renamed, return the physical register)."""
        return self.rename_map.get(register, register)

    def clear(self):
        """Clear all renaming rules."""
        self.rename_map.clear()
        self.available_physical_regs = set([f"R{i}" for i in range(1, self.max_registers + 1)])  # Reset available registers
