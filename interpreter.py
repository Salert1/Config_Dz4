import json
import sys


def interpret(binary_file, memory_range, output_file):
    memory = [0] * 1024  # Example memory size

    def fetch_command(binary, length):
        if length == 5:
            A = (binary >> 32) & 0b11111
            B = (binary >> 18) & 0x3FF
            C = (binary >> 5) & 0x3FFF
            return A, B, C
        return None

    def fetch_command_with_four(binary):
        A = (binary >> 35) & 0b11111
        B = (binary >> 21) & 0x7FFF
        C = (binary >> 7) & 0x3FFF
        D = binary & 0x3FF
        return A, B, C, D

    with open(binary_file, 'rb') as file:
        binary_data = file.read()

    pc = 0
    while pc < len(binary_data):
        # if len(binary_data[pc:pc + 5]) >= 21:
            word = int.from_bytes(binary_data[pc:pc + 5], 'big')
            A = (word >> 32) & 0b11111
            print(A)

            if A == 30:  # LOAD_CONST
                A, B, C = fetch_command(word, 5)
                print(A, B, C)
                print(f"LOAD_CONST: memory[{B}] = {C}")  # Debug
                memory[B] = C
            elif A == 16:  # READ_MEM
                A, B, C = fetch_command(word, 5)
                print(f"READ_MEM: memory[{B}] = memory[{C}]")  # Debug
                memory[B] = memory[C]
            elif A == 18:  # WRITE_MEM
                A, B, C = fetch_command(word, 5)
                print(f"WRITE_MEM: memory[{C}] = memory[{B}]")  # Debug
                memory[memory[C]] = memory[B]
            elif A == 22:  # UNARY_MINUS
                A, B, C, D = fetch_command_with_four(word)
                print(f"UNARY_MINUS: memory[{D}] = -memory[{C}]")  # Debug
                memory[D] = memory[C] + B
            pc += 5
        # else:
        #     print(f"Incomplete data at pc={pc}")  # Debug
        #     break

    # Debug before writing to file
    print(f"Final memory state: {memory[memory_range[0]:memory_range[1]]}")

    result = {"memory_range": memory_range, "values": memory[memory_range[0]:memory_range[1]]}

    # Save result to file
    with open(output_file, 'w') as result_file:
        json.dump(result, result_file, indent=4)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python interpreter.py <input.bin> <start:end> <output.json>")
        sys.exit(1)

    binary_file = sys.argv[1]
    memory_range = list(map(int, sys.argv[2].split(':')))
    output_file = sys.argv[3]
    interpret(binary_file, memory_range, output_file)

#python interpreter.py output.bin 0:1000 result.json
