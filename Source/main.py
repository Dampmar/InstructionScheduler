import os
from file_parser import file_reader
from single import SingleInOrder
from scalar_in_order import SuperscalarInOrder
from scalar_out_order import SuperscalarOutOrder
from rename_single import SingleInOrder_Renaming
from rename_scalar_in_order import SuperscalarInOrder_Renaming
from rename_scalar_out_order import SuperscalarOutOrder_Renaming

def main():
    filename = input("Enter the filename (in 'test' folder): ")
    test_folderpath = "test"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(os.path.dirname(current_dir), test_folderpath)
    filePath = os.path.join(test_dir, filename)

    # Instructions retrieval 
    instructions = file_reader(filePath)

    # Checking that instructions are being properly parsed
    print("Input instructions:")
    for inst in instructions:
        inst.print_instruction()

    print("Single Instruction (in-order) Scheduler:")
    single = SingleInOrder(functional_units=3)
    for instr in instructions:
        single.add_instruction(instr)
    
    single.run()
    for entry in single.logger:
        print(entry)
    
    # Instructions Retrieval
    instructions = file_reader(filePath)

    print("\nSuperscalar (in-order) Scheduler:")
    single = SuperscalarInOrder(functional_units=3, max_issue=2)
    for instr in instructions:
        single.add_instruction(instr)
    
    single.run()
    for entry in single.logger:
        print(entry)

    # Instructions Retrieval
    instructions = file_reader(filePath)

    print("\nSuperscalar (out-of-order) Scheduler:")
    single = SuperscalarOutOrder(functional_units=3, max_issue=2)
    for instr in instructions:
        single.add_instruction(instr)
    
    single.run()
    for entry in single.logger:
        print(entry)
    
    # Instructions Retrieval
    instructions = file_reader(filePath)

    print("\nSingle (in-order) with Renaming Scheduler:")
    single = SingleInOrder_Renaming(functional_units=3)
    for instr in instructions:
        single.add_instruction(instr)
    
    single.run()
    for entry in single.logger:
        print(entry)
    
    # Instructions Retrieval
    instructions = file_reader(filePath)

    print("\nSuperscalar (in-order) with Renaming Scheduler:")
    single = SuperscalarInOrder_Renaming(functional_units=3, max_issue=2)
    for instr in instructions:
        single.add_instruction(instr)
    
    single.run()
    for entry in single.logger:
        print(entry)

    # Instructions Retrieval
    instructions = file_reader(filePath)

    print("\nSuperscalar (out of order) with Renaming Scheduler:")
    single = SuperscalarOutOrder_Renaming(functional_units=8, max_issue=2)
    for instr in instructions:
        single.add_instruction(instr)
    
    single.run()
    for entry in single.logger:
        print(entry)

if __name__ == "__main__":
    main()