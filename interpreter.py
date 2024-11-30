import json
import sys


def interpret(binary_file, memory_range, output_file):
    memory = [0] * 1024  # Example memory size

    def deserialize_minus(byts):
        A = byts[0] & 0b11111
        B = ((byts[0] >> 5) & 0b111) | ((byts[1] & 0b11111111) << 3) | ((byts[2] & 0b1111) << 11)
        C = ((byts[2] >> 4) & 0b1111) | ((byts[3] & 0b111111) << 4)
        D = ((byts[3] >> 6) & 0b11) | ((byts[4] & 0b11111111) << 2)
        return A, B, C, D

    def deserialize_load(byts):
        A = byts[0] & 0b11111
        B = ((byts[0] >> 5) & 0b111) | ((byts[1] & 0b1111111) << 3)
        C = ((byts[1] >> 7) & 0b1) | ((byts[2] & 0b11111111) << 1) | ((byts[3] & 0b11111111) << 1 + 8) | ((byts[4] & 0b11111111) << 1 + 8 + 8)
        return A, B, C

    def deserialize_read(byts):
        A = byts[0] & 0b11111
        B = ((byts[0] >> 5) & 0b111) | ((byts[1] & 0b1111111) << 3)
        C = ((byts[1] >> 7) & 0b1) | ((byts[2] & 0b11111111) << 1) | ((byts[3] & 0b1) << 1 + 8)
        return A, B, C


    with open(binary_file, 'rb') as file:
        binary_data = file.read()

    pc = 0
    while pc < len(binary_data):
        # if len(binary_data[pc:pc + 5]) >= 21:
            word = int.from_bytes(binary_data[pc:pc + 5], 'big')
            A = (word >> 32) & 0b11111


            if A == 30:  # LOAD_CONST
                data = binary_data[pc:pc + 5]
                A, B, C = deserialize_load(data)
                print(A, B, C)
                print(f"LOAD_CONST: memory[{B}] = {C}")  # Debug
                memory[B] = C
                pc += 5
            elif A == 16:  # READ_MEM
                data = binary_data[pc:pc + 4]
                A, B, C =  deserialize_read(data)
                print(f"READ_MEM: memory[{B}] = memory[{C}]")  # Debug
                memory[B] = memory[C]
                pc += 4
            elif A == 18:  # WRITE_MEM
                data = binary_data[pc:pc + 4]
                A, B, C = deserialize_read(data)
                print(f"WRITE_MEM: memory[{C}] = memory[{B}]")  # Debug
                memory[memory[C]] = memory[B]
                pc += 4
            elif A == 22:  # UNARY_MINUS
                data = binary_data[pc:pc + 5]
                A, B, C, D = deserialize_minus(data)
                print(A, B, C, D)
                memory[D] = -(memory[memory[C] + B])
                pc += 5


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
