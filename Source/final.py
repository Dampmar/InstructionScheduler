import os
from file_parser import file_reader
from single import SingleInOrder
from scalar_in_order import SuperscalarInOrder
from scalar_out_order import SuperscalarOutOrder
from rename_single import SingleInOrder_Renaming
from rename_scalar_in_order import SuperscalarInOrder_Renaming
from rename_scalar_out_order import SuperscalarOutOrder_Renaming

def main():
    print("Select the configuration for simulation")
    # Ask the user to enter a the number of issue slots; verify its valid
    while True:
        issue_slots = input("Enter number of issue slots: ").strip()
        if issue_slots.isdigit() and int(issue_slots) > 0:
            issue_slots = int(issue_slots)
            break
        print("Please enter a valid number of issue slots (positive integer value)")
    
    # Ask the user for the type of instruction fetching and retirement
    while True:
        type = input("Enter the type of instruction fetching and retirement (out-of-order / in-order): ").strip()
        if type.lower() == "out-of-order" or type.lower() == "in-order":
            type = type.lower()
            break
        print("Please enter either in-order or out-of-order")
    
    # Ask the user for the number of parallel functional units
    while True:
        functional_units = input("Enter the number of functional units: ").strip()
        if functional_units.isdigit() and int(functional_units) > 0:
            functional_units = int(functional_units)
            break
        print("Please enter a valid number of functional units (positive integer value)")
    
    # Ask the user if they want register renaming 
    while True:
        hasRenaming = input("Would you like register renaming? (y/n): ").strip().lower()
        if hasRenaming in ['y', 'yes']:
            hasRenaming = True
            break
        elif hasRenaming in ['n', 'no']:
            hasRenaming = False
            break
        print("Please select a valid option.")
    
    # Build the scheduler
    scheduler = None 
    if hasRenaming:
        if type == 'in-order' and issue_slots == 1:
            scheduler = SingleInOrder_Renaming(functional_units=functional_units)
        elif type == 'in-order' and issue_slots > 1:
            scheduler = SuperscalarInOrder_Renaming(functional_units=functional_units, max_issue=issue_slots)
        elif type == 'out-of-order' and issue_slots >= 1:
            scheduler = SuperscalarOutOrder_Renaming(functional_units=functional_units, max_issue=issue_slots)
        else:
            print("Invalid sequence")
            exit()
    elif not hasRenaming:
        if type == 'in-order' and issue_slots == 1:
            scheduler = SingleInOrder(functional_units=functional_units)
        elif type == 'in-order' and issue_slots > 1:
            scheduler = SuperscalarInOrder(functional_units=functional_units, max_issue=issue_slots)
        elif type == 'out-of-order' and issue_slots >= 1:
            scheduler = SuperscalarOutOrder(functional_units=functional_units, max_issue=issue_slots)
        else:
            print("Invalid sequence")
            exit()
    else:
        print("Invalid sequence for setupping the scheduler, terminating program!")
        exit()
    
    while True:
        # Ask the user for the filename
        filename = input("Enter the filename (in 'test' folder): ")
        test_folderpath = "test"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_dir = os.path.join(os.path.dirname(current_dir), test_folderpath)
        filePath = os.path.join(test_dir, filename)

        # Get instructions, and show them to the user
        instructions = file_reader(filePath)
        print("Input instructions:")
        for instr in instructions:
            scheduler.add_instruction(instr)
            #instr.print_instruction()

        print("Results of Configuration:")
        # Schedule the instructions, print the results
        scheduler.run()
        for entry in scheduler.logger:
            print(entry)
        
        # Ask the user if they want to run another test
        continue_test = input("Do you want to run another test? (y/n): ").strip().lower()
        if continue_test not in ("y", "yes"):
            print("Exiting the program.")
            break
        

if __name__ == "__main__":
    main()