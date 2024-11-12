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

    # Retrieve the input instructions 
    instructions = read_file(filePath)
    print("Input Instructions:")
    for inst in instructions:
        inst.print_instruction()

    # Ask the user for the number of parallel functional units 
    while True:
        functional_units = input("Enter the number of functional units:")
        if functional_units.isdigit() and int(functional_units) > 0:
            functional_units = int(functional_units)
            break
        print("Please enter a valid positive integer value.")
    
    # Ask the user for the number of issue slots 
    while True:
        issue_slots = input("Enter the number of issue slots:")
        if issue_slots.isdigit() and int(issue_slots) > 0:
            issue_slots = int(issue_slots)
            break
        print("Please enter a valid positive integer value.")
    
    # Ask the user for the type instruction fetching and retirement
    while True:
        type = input("Enter the type of instruction fetching and retirement (out-of-order / in-order):")
        if type.lower() == "out-of-order" or type.lower() == "in-order":
            type = type.lower()
            break
        print("Please enter either in-order or out-of-order")
    
    # Build the scheduler
    scheduler = None
    if type == "in-order" and issue_slots == 1:
        scheduler = SingleInOrder(functional_units=functional_units)
    elif type == "in-order" and issue_slots > 1:
        scheduler = SuperscalarInOrder(functional_units=functional_units, max_issue=issue_slots)
    elif type == "out-of-order" and issue_slots >= 1:
        scheduler = SuperscalarOutOrder(functional_units=functional_units, max_issue=issue_slots)
    else:
        print("Invalid sequence for setupping the scheduler, terminating program!")
    
    # Add the instructions to the scheduler
    for instr in instructions:
        scheduler.add_instruction(instr)
    
    # Run the scheduling of instructions
    scheduler.run()

    # Print the results on the logger, printed in the order they retire
    for entry in scheduler.logger:
        print(entry)

if __name__ == "__main__":
    main()