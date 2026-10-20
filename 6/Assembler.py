import sys
import os

# A-instructions:
# 0 + 15-bit value
#
# C-instructions:
# 111 + comp + dest + jump

# comp      a zx nx zy ny f no
COMP = {
    "0":   "0101010",  # zx=1, nx=0, zy=1, ny=0, f=1, no=0 

    "1":   "0111111",  # zx=1, nx=1, zy=1, ny=1, f=1, no=1 

    "-1":  "0111010",  # zx=1, nx=1, zy=1, ny=0, f=1, no=0

    "D":   "0001100",  # zx=0, nx=0, zy=1, ny=1, f=0, no=0

    "A":   "0110000",  # zx=1, nx=1, zy=0, ny=0, f=0, no=0 

    "!D":  "0001101",  # same as D, then negate output 

    "!A":  "0110001",  # same as A, then negate output

    "-D":  "0001111",  # same as D, then negate output 

    "-A":  "0110011",  # same as A, then negate output

    "D+1": "0011111",  # manipulate y to 1, then D + 1

    "A+1": "0110111",  # manipulate x to 1, then A + 1

    "D-1": "0001110",  # D + (-1) 

    "A-1": "0110010",  # A + (-1) 

    "D+A": "0000010",  # zx=0, nx=0, zy=0, ny=0, f=1, no=0 

    "D-A": "0010011",  # manipulate y → -A, then D + (-A)

    "A-D": "0000111",  # manipulate x → -D, then A + (-D)

    "D&A": "0000000",  # zx=0, nx=0, zy=0, ny=0, f=0, no=0 

    "D|A": "0010101",  # manipulate inputs to produce D|A


    # M versions:
    # a=0 → ALU uses A
    # a=1 → ALU uses M

    "M":   "1110000",  # Same operation as A, but a=1

    "!M":  "1110001",  # Same operation as !A, but a=1

    "-M":  "1110011",  # Same operation as -A, but a=1

    "M+1": "1110111",  # Same operation as A+1, but a=1

    "M-1": "1110010",  # Same operation as A-1, but a=1

    "D+M": "1000010",  # Same operation as D+A, but a=1

    "D-M": "1010011",  # Same operation as D-A, but a=1

    "M-D": "1000111",  # Same operation as A-D, but a=1

    "D&M": "1000000",  # Same operation as D&A, but a=1

    "D|M": "1010101",  # Same operation as D|A, but a=1
}


DEST = {
    "":    "000",
    "M":   "001",
    "D":   "010",
    "MD":  "011",
    "A":   "100",
    "AM":  "101",
    "AD":  "110",
    "AMD": "111"
}


JUMP = {
    "":    "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}

SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,

    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,

    "SCREEN": 16384,
    "KBD": 24576
}

variable_address = 16

def translate_instruction(instruction):

    if instruction.startswith("@"):
        return translate_a_instruction(instruction[1:])

    else:
        return translate_c_instruction(instruction)

def translate_a_instruction(value):
    global variable_address

    if value in SYMBOLS:
        number = SYMBOLS[value]

    elif value.isdigit():
        number = int(value)

    else:
        SYMBOLS[value] = variable_address
        number = variable_address
        variable_address += 1

    return "0" + format(number, "015b")

def translate_c_instruction(instruction):

    dest = ""
    comp = ""
    jump = ""

    # Separate destination from computation
    if "=" in instruction:
        dest, instruction = instruction.split("=")

    # Separate computation from jump
    if ";" in instruction:
        comp, jump = instruction.split(";")
    else:
        comp = instruction

    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]



def clean_line(line):
    # Remove comments
    line = line.split("//")[0]

    # Remove whitespace
    line = line.strip()

    return line

def first_pass(filename):
    instruction_number = 0

    with open(filename, "r") as file:
        for line in file:
            instruction = clean_line(line)

            if not instruction:
                continue

            if instruction.startswith("(") and instruction.endswith(")"):
                # Removes parenthesis from symbol
                label = instruction[1:-1]
                SYMBOLS[label] = instruction_number
            else:
                instruction_number += 1

# Get the .asm filename from the command line
filename = sys.argv[1]

# Create the output filename in the same folder
output_filename = os.path.splitext(filename)[0] + ".hack"

# First pass: find labels
first_pass(filename)

# Second pass: translate instructions
with open(filename, "r") as input_file:
    with open(output_filename, "w") as output_file:

        for line in input_file:
            instruction = clean_line(line)

            if not instruction:
                continue

            # Labels do not generate machine code
            if instruction.startswith("(") and instruction.endswith(")"):
                continue

            binary = translate_instruction(instruction)

            output_file.write(binary + "\n")