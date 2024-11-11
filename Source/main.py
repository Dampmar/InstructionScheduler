import os 
from parser import read_file
from instruction import Instruction, LoadStoreInstruction, ThreeRegInstruction
from rename import SingleInOrder_Renaming

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
    single_sched = SingleInOrder_Renaming(functional_units=4)
    for instr in instructions:
        single_sched.add_instruction(instr)

    single_sched.run()

    for entry in single_sched.logger:
        print(entry)

if __name__ == "__main__":
    main()