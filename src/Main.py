# Final Project
# Computer Architecture
# Daniel Marin 

import os 
from parser import read_file
from instruction import Instruction, LoadStoreInstruction, ThreeRegInstruction
from single import SingleInOrder
from superscalar import SuperscalarInOrder
from superscalar_out_order import SuperscalarOutOrder

def main():
    filename = input("Enter the filename (in 'test' folder): ")
    test_folderpath = "test"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(os.path.dirname(current_dir), test_folderpath)
    filePath = os.path.join(test_dir, filename)

    # Instructions retrieval 
    instructions = read_file(filePath)

    # Checking that instructions are being properly parsed 
    print("Input instructions")
    for inst in instructions:
        inst.print_instruction()

    print("Single Instruction (in-order) Scheduler:")
    single_sched = SingleInOrder()
    for instr in instructions:
        single_sched.add_instruction(instr)
    
    single_sched.run()

    for entry in single_sched.logger:
        print(entry)
    
    print("Superscalar (in-order) Scheduler: ")
    super_sched = SuperscalarInOrder(functional_units=8, max_issue=2)
    for instr in instructions:
        super_sched.add_instruction(instr)
    
    super_sched.run()

    for entry in super_sched.logger:
        print(entry)

    print("Superscalar (out of order) Scheduler: ")
    super_scheduler = SuperscalarOutOrder(functional_units=4, max_issue=2)
    for instr in instructions:
        super_scheduler.add_instruction(instr)
    super_scheduler.run()
    for entry in super_scheduler.logger:
        print(entry)
    

    
if __name__ == "__main__":
    main()