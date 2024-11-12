import os
from parser import read_file
from instruction import Instruction, LoadStoreInstruction, ThreeRegInstruction
from single_rename import SingleInOrder_Renaming
from single import SingleInOrder
from scalar_in_order import SuperscalarInOrder
from scalar_in_order_rename import SuperscalarInOrder_Renaming
from scalar_out_order import SuperscalarOutOrder


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
    single = SingleInOrder(functional_units=3)
    for instr in instructions:
        single.add_instruction(instr)
    
    single.run()
    for entry in single.logger:
        print(entry)

    # Instructions retrieval 
    instructions = read_file(filePath)

    print("\nSingle Instruction (in-order) with Renaming Scheduler:")
    single_sched = SingleInOrder_Renaming(functional_units=4)
    for instr in instructions:
        single_sched.add_instruction(instr)

    single_sched.run()
    for entry in single_sched.logger:
        print(entry)
    
    # Instructions retrieval 
    instructions = read_file(filePath)
    
    print("\nSuperscalar (in-order) Scheduler:")
    superscalar_inorder_sched = SuperscalarInOrder(functional_units=4, max_issue=2)
    for instr in instructions:
        superscalar_inorder_sched.add_instruction(instr)
    
    superscalar_inorder_sched.run()

    for entry in superscalar_inorder_sched.logger:
        print(entry)
    
    # Instructions retrieval
    instructions = read_file(filePath)
    print("\nSuperscalar (in-order) with Renaming Scheduler:")
    superscalar_inorder_renaming_sched = SuperscalarInOrder_Renaming(functional_units=4, max_issue=2)
    for instr in instructions:
        superscalar_inorder_renaming_sched.add_instruction(instr)

    superscalar_inorder_renaming_sched.run()
    for entry in superscalar_inorder_renaming_sched.logger:
        print(entry)


    # Instructions retrieval 
    instructions = read_file(filePath)
    
    print("\nSuperscalar (out of order) Scheduler: ")
    super_scheduler = SuperscalarOutOrder(functional_units=4, max_issue=2)
    for instr in instructions:
        super_scheduler.add_instruction(instr)
    super_scheduler.run()
    for entry in super_scheduler.logger:
        print(entry)

    


if __name__ == "__main__":
    main()