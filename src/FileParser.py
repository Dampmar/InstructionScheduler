from Instruction import Instruction, LoadStoreInstruction, ThreeRegInstruction

# file_parser class 
def read_file(filename):
    instructions = []

    # Parsing the instructions into a list
    with open(filename, 'r') as file:
        for line in file:
            # Remove whitespace or newline characters 
            line = line.strip()
            if line:            # Ensure not empty line 
                # Breakdown each line into destination and operation
                breakdown = line.replace(" ","").split("=") # Remove whitespaces
                dest = breakdown[0]

                # Further split the operation into sources 
                if '+' in breakdown[1]:
                    src1, src2 = breakdown[1].split('+')
                    operand = '+'
                    instruction = ThreeRegInstruction(dest=dest, operation=operand, src1=src1, src2=src2)
                elif '-' in breakdown[1]:
                    src1, src2 = breakdown[1].split('-')
                    operand = '-'
                    instruction = ThreeRegInstruction(dest=dest, operation=operand, src1=src1, src2=src2)
                elif '*' in breakdown[1]:
                    src1, src2 = breakdown[1].split('*')
                    operand = '*'
                    instruction = ThreeRegInstruction(dest=dest, operation=operand, src1=src1, src2=src2)
                elif 'LOAD' in breakdown[1]:
                    operand = 'LOAD'
                    instruction = LoadStoreInstruction(dest=dest, operation=operand)
                elif 'STORE' in breakdown[1]:
                    operand = 'STORE'
                    instruction = LoadStoreInstruction(dest=dest, operation=operand)
                else:
                    raise ValueError(f"Invalid operation in line: {line}")

                # Add instruction to the list 
                instructions.append(instruction)
    return instructions
            
