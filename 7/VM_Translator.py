# VM translator 

import sys
from pathlib import Path

def write_push(segment, index):
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
        # Static variables use unique symbols
        assembly.extend([
            f"@Static.{index}",
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


def write_pop(segment, index):
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
        # Replace filename with the current VM filename
        assembly.extend([
            f"@Static.{index}",
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


def translate_file(input_filename, output_filename):
    comparison_count = 0

    with open(input_filename, "r") as infile:
        with open(output_filename, "w") as outfile:

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
                    assembly = write_push(segment, index)

                elif command_parts[0] == "pop":
                    segment = command_parts[1]
                    index = int(command_parts[2])
                    assembly = write_pop(segment, index)

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
                    assembly = write_eq(comparison_count)
                    comparison_count += 1   

                elif command_parts[0] == "gt":
                    assembly = write_gt(comparison_count)
                    comparison_count += 1

                elif command_parts[0] == "lt":
                    assembly = write_lt(comparison_count)
                    comparison_count += 1     

                else:
                    raise ValueError(f"Unsupported command: {line}")

                # Write the generated assembly to the output file
                outfile.write(assembly + "\n")

def main():
    

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

if __name__ == "__main__":
    main()
