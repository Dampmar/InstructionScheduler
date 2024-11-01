import os 
from FileParser import read_file
from Instruction import Instruction, LoadStoreInstruction, ThreeRegInstruction

def main():
    filename = "instructions.asm"
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

if __name__ == "__main__":
    main()