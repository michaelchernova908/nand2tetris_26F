# VM translator 

import sys
from pathlib import Path

def write_push(segment, index, file_name):
    assembly = []

    if segment == "constant":
        # Load the constant into D
        assembly.extend([
            f"@{index}",
            "D=A"
        ])

    elif segment in ["local", "argument", "this", "that"]:
        # Load the base address into D
        base = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }[segment]

        assembly.extend([
            f"@{base}",
            "D=M",
            f"@{index}",
            "A=D+A",
            "D=M"
        ])

    elif segment == "temp":
        # Temp segment occupies RAM[5] through RAM[12]
        if not 0 <= index <= 7:
            raise ValueError("Temp index must be between 0 and 7")

        assembly.extend([
            f"@{5 + index}",
            "D=M"
        ])

    elif segment == "pointer":
        # pointer 0 = THIS, pointer 1 = THAT
        if index not in [0, 1]:
            raise ValueError("Pointer index must be 0 or 1")

        pointer = "THIS" if index == 0 else "THAT"

        assembly.extend([
            f"@{pointer}",
            "D=M"
        ])

    elif segment == "static":
        assembly.extend([
            f"@{file_name}.{index}",
            "D=M"
        ])

    else:
        raise ValueError(f"Unsupported push segment: {segment}")

    # Common code: push D onto the stack
    assembly.extend([
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
    ])

    return "\n".join(assembly)


def write_pop(segment, index, file_name):
    assembly = []

    # Calculate the destination address for the segment
    if segment in ["local", "argument", "this", "that"]:
        base = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }[segment]

        assembly.extend([
            f"@{base}",
            "D=M",
            f"@{index}",
            "D=D+A",
            "@R13",
            "M=D"
        ])

    elif segment == "temp":
        if not 0 <= index <= 7:
            raise ValueError("Temp index must be between 0 and 7")

        assembly.extend([
            f"@{5 + index}",
            "D=A",
            "@R13",
            "M=D"
        ])

    elif segment == "pointer":
        if index not in [0, 1]:
            raise ValueError("Pointer index must be 0 or 1")

        pointer = "THIS" if index == 0 else "THAT"

        assembly.extend([
            f"@{pointer}",
            "D=A",
            "@R13",
            "M=D"
        ])

    elif segment == "static":
        assembly.extend([
            f"@{file_name}.{index}",
            "D=A",
            "@R13",
            "M=D"
        ])

    else:
        raise ValueError(f"Unsupported pop segment: {segment}")

    # Pop the stack value and store it at the destination
    assembly.extend([
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "A=M",
        "M=D"
    ])

    return "\n".join(assembly)


def write_add():
    # Decrement SP to point to the top stack value, then load it into D.
    # Move A to the previous stack location and add D to that value.
    # The result replaces the two original values, so SP stays decremented by one.
    assembly = [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "M=D+M"
    ]
    return "\n".join(assembly)


def write_sub():
    # Pop the top value into D, then subtract it from the
    # previous stack value. The result replaces both operands.
    assembly = [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "M=M-D"
    ]
    return "\n".join(assembly)


def write_neg():
    # Negate the value at the top of the stack.
    assembly = [
        "@SP",
        "A=M-1",
        "M=-M"
    ]
    return "\n".join(assembly)


def write_and():
    # Pop the top value into D and perform a bitwise AND
    # with the previous stack value.
    assembly = [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "M=D&M"
    ]
    return "\n".join(assembly)


def write_or():
    # Pop the top value into D and perform a bitwise OR
    # with the previous stack value.
    assembly = [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "M=D|M"
    ]
    return "\n".join(assembly)


def write_not():
    # Perform a bitwise NOT on the top stack value.
    assembly = [
        "@SP",
        "A=M-1",
        "M=!M"
    ]
    return "\n".join(assembly)

def write_eq(label_number):
    true_label = f"TRUE_{label_number}"
    end_label = f"END_{label_number}"

    assembly = [
        # Pop the top value into D
        "@SP",
        "AM=M-1",
        "D=M",

        # Subtract the top value from the value below it
        "A=A-1",
        "D=M-D",

        # If the result is zero, the values are equal
        f"@{true_label}",
        "D;JEQ",

        # Otherwise, store false (0)
        "@SP",
        "A=M-1",
        "M=0",

        # Skip the true case
        f"@{end_label}",
        "0;JMP",

        # True case: store -1
        f"({true_label})",
        "@SP",
        "A=M-1",
        "M=-1",

        # End of comparison
        f"({end_label})"
    ]

    return "\n".join(assembly)

def write_gt(label_number):
    true_label = f"TRUE_{label_number}"
    end_label = f"END_{label_number}"

    assembly = [
        # Pop the top value into D
        "@SP",
        "AM=M-1",
        "D=M",

        # Subtract the top value from the value below it
        "A=A-1",
        "D=M-D",

        # If the result is greater than zero, jump to TRUE
        f"@{true_label}",
        "D;JGT",

        # Otherwise, store false (0)
        "@SP",
        "A=M-1",
        "M=0",

        # Skip the true case
        f"@{end_label}",
        "0;JMP",

        # True case: store -1
        f"({true_label})",
        "@SP",
        "A=M-1",
        "M=-1",

        # End of comparison
        f"({end_label})"
    ]

    return "\n".join(assembly)

def write_lt(label_number):
    true_label = f"TRUE_{label_number}"
    end_label = f"END_{label_number}"

    assembly = [
        # Pop the top value into D
        "@SP",
        "AM=M-1",
        "D=M",

        # Subtract the top value from the value below it
        "A=A-1",
        "D=M-D",

        # If the result is less than zero, jump to TRUE
        f"@{true_label}",
        "D;JLT",

        # Otherwise, store false (0)
        "@SP",
        "A=M-1",
        "M=0",

        # Skip the true case
        f"@{end_label}",
        "0;JMP",

        # True case: store -1
        f"({true_label})",
        "@SP",
        "A=M-1",
        "M=-1",

        # End of comparison
        f"({end_label})"
    ]

    return "\n".join(assembly)

def write_label(function_name, label):
    assembly = [
        f"({function_name}${label})"
    ]
    return "\n".join(assembly)


def write_goto(function_name, label):
    assembly = [
        f"@{function_name}${label}",
        "0;JMP"
    ]
    return "\n".join(assembly)


def write_if(function_name, label):
    assembly = [
        "@SP",
        "AM=M-1",
        "D=M",
        f"@{function_name}${label}",
        "D;JNE"
    ]
    return "\n".join(assembly)

def write_function(name, num_locals):
    assembly = [
        # Declare the function label
        f"({name})"
    ]

    # Initialize local variables to zero
    for i in range(num_locals):
        assembly.extend([
            "@SP",
            "A=M",
            "M=0",
            "@SP",
            "M=M+1"
        ])

    return "\n".join(assembly)

def write_call(name, num_args, return_number):
    return_label = f"RETURN_{return_number}"

    assembly = [
        # Push caller's return address
        f"@{return_label}",
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",

        # Push caller's LCL
        "@LCL",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",

        # Push caller's ARG
        "@ARG",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",

        # Push caller's THIS
        "@THIS",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",

        # Push caller's THAT
        "@THAT",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",

        # ARG = SP - 5 - num_args
        "@SP",
        "D=M",
        "@5",
        "D=D-A",
        f"@{num_args}",
        "D=D-A",
        "@ARG",
        "M=D",

        # LCL = SP
        "@SP",
        "D=M",
        "@LCL",
        "M=D",

        # Jump to called function
        f"@{name}",
        "0;JMP",

        # Declare return address
        f"({return_label})"
    ]

    return "\n".join(assembly)

def write_return():
    assembly = [
        # FRAME = LCL (store the current frame in R13)
        "@LCL",
        "D=M",
        "@R13",
        "M=D",

        # Return = value stored at address (FRAME - 5) (store return address in R14)
        "@5",
        "A=D-A",
        "D=M",
        "@R14",
        "M=D",

        # Make value stored in ARG = pop() (put return value in memory address of 1st argument)
        "@SP",
        "AM=M-1",
        "D=M",
        "@ARG",
        "A=M",
        "M=D",

        # SP = ARG + 1
        "@ARG",
        "D=M+1",
        "@SP",
        "M=D",

        # THAT =  value stored at (FRAME - 1)
        "@R13",
        "AM=M-1",
        "D=M",
        "@THAT",
        "M=D",

        # THIS = value stored at  (FRAME - 2)
        "@R13",
        "AM=M-1",
        "D=M",
        "@THIS",
        "M=D",

        # ARG = value stored at  (FRAME - 3)
        "@R13",
        "AM=M-1",
        "D=M",
        "@ARG",
        "M=D",

        # LCL = value stored at  (FRAME - 4)
        "@R13",
        "AM=M-1",
        "D=M",
        "@LCL",
        "M=D",

        # Goto return address
        "@R14",
        "A=M",
        "0;JMP"
    ]

    return "\n".join(assembly)

def write_init(return_number):
    assembly = [
        # Initialize stack pointer
        "@256",
        "D=A",
        "@SP",
        "M=D"
    ]

    # Call Sys.init
    assembly.append(write_call("Sys.init", 0, return_number))

    return "\n".join(assembly)




def translate_file(input_filename, outfile, counters):

    # Get the VM filename without its extension (for static variables)
    file_name = Path(input_filename).stem

    # Track the current function for function-scoped labels
    current_function = ""

    with open(input_filename, "r") as infile:

        for line in infile:
            # Remove comments and whitespace
            line = line.split("//")[0].strip()

            # Skip empty lines
            if not line:
                continue

            # Split the VM command into its individual parts
            command_parts = line.split()

            if command_parts[0] == "push":
                segment = command_parts[1]
                index = int(command_parts[2])
                assembly = write_push(segment, index, file_name)

            elif command_parts[0] == "pop":
                segment = command_parts[1]
                index = int(command_parts[2])
                assembly = write_pop(segment, index, file_name)

            elif command_parts[0] == "add":
                assembly = write_add()

            elif command_parts[0] == "sub":
                assembly = write_sub()

            elif command_parts[0] == "neg":
                assembly = write_neg()

            elif command_parts[0] == "and":
                assembly = write_and()

            elif command_parts[0] == "or":
                assembly = write_or()

            elif command_parts[0] == "not":
                assembly = write_not()

            elif command_parts[0] == "eq":
                assembly = write_eq(counters["comparison"])
                counters["comparison"] += 1

            elif command_parts[0] == "gt":
                assembly = write_gt(counters["comparison"])
                counters["comparison"] += 1

            elif command_parts[0] == "lt":
                assembly = write_lt(counters["comparison"])
                counters["comparison"] += 1

            elif command_parts[0] == "label":
                label = command_parts[1]
                assembly = write_label(current_function, label)

            elif command_parts[0] == "goto":
                label = command_parts[1]
                assembly = write_goto(current_function, label)

            elif command_parts[0] == "if-goto":
                label = command_parts[1]
                assembly = write_if(current_function, label)

            elif command_parts[0] == "function":
                name = command_parts[1]
                num_locals = int(command_parts[2])

                current_function = name
                assembly = write_function(name, num_locals)

            elif command_parts[0] == "call":
                name = command_parts[1]
                num_args = int(command_parts[2])

                assembly = write_call(
                    name,
                    num_args,
                    counters["return"]
                )
                counters["return"] += 1

            elif command_parts[0] == "return":
                assembly = write_return()

            else:
                raise ValueError(f"Unsupported command: {line}")

            # Write generated assembly to the shared output file
            outfile.write(assembly + "\n")


def main():

    if __name__ == "__main__":

        # Check that a command-line argument was provided
        if len(sys.argv) != 2:
            print("Usage: python VMTranslator.py <input file or directory>")
            sys.exit(1)

        # Get the input path from the terminal
        input_path = Path(sys.argv[1])

        # Check that the input path exists
        if not input_path.exists():
            print("Error: Input path does not exist.")
            sys.exit(1)

        # Determine whether the input is a file or directory
        if input_path.is_file():

            # Make sure the input is a VM file
            if input_path.suffix.lower() != ".vm":
                print("Error: Input file must have a .vm extension.")
                sys.exit(1)

            # Translate a single VM file
            vm_files = [input_path]

            # Output ASM file has the same name as the VM file
            output_filename = input_path.with_suffix(".asm")

            # No bootstrap code for a single VM file
            bootstrap = False

        elif input_path.is_dir():

            # Find all VM files in the directory
            vm_files = sorted(input_path.glob("*.vm"))

            if not vm_files:
                print("Error: No VM files found in directory.")
                sys.exit(1)

            # Output ASM file has the same name as the directory
            output_filename = input_path / (input_path.name + ".asm")

            # Bootstrap code is required for directory translation
            bootstrap = True

        else:
            print("Error: Invalid input path.")
            sys.exit(1)

        # Initialize shared counters
        counters = {
            "comparison": 0,
            "return": 0
        }

        # Open the output ASM file
        with open(output_filename, "w") as outfile:

            # Write bootstrap code if translating a directory
            if bootstrap:
                outfile.write(write_init(counters["return"]) + "\n")
                counters["return"] += 1

            # Translate each VM file into the same ASM file
            for input_filename in vm_files:
                translate_file(input_filename, outfile, counters)

        print(f"Translation complete: {output_filename}")


    """
        input_path = Path(sys.argv[1])
    
        if not input_path.exists():
            print(f"Error: {input_path} does not exist.")
            sys.exit(1)
    
        if input_path.is_file():
            if input_path.suffix.lower() != ".vm":
                print("Error: Input file must have a .vm extension.")
                sys.exit(1)
    
            output_path = input_path.with_suffix(".asm")
            translate_file(str(input_path), str(output_path))
    
        elif input_path.is_dir():
            vm_files = list(input_path.glob("*.vm"))
    
            if not vm_files:
                print("Error: No .vm files found in directory.")
                sys.exit(1)
    
            
            for vm_file in vm_files:
                output_path = vm_file.with_suffix(".asm")
                translate_file(str(vm_file), str(output_path))
          """   


if __name__ == "__main__":
    main()


