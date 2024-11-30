import json
import struct
import sys


def serialize_load(A,B,C):
    bytes_array = [0] * 5
    # bytes_array[0] = int((bin(B)[2:4]) + (bin(A)[2:] ),2)
    bytes_array[0] = (A & 0b11111) | ((B & 0b111) << 5)
    bytes_array[1] = ((B >> 3) & 0b1111111) | ((C & 0b1) << 7)
    bytes_array[2] = (C >> 1) & 0b11111111
    bytes_array[3] = (C >> (1 + 8)) & 0b11111111
    bytes_array[4] = (C >> (1 + 8 + 8)) & 0b11111
    return bytes(bytes_array)

def deserialize_load(byts):
    A = byts[0] & 0b11111
    B = ((byts[0] >> 5) & 0b111) | ((byts[1] & 0b1111111) << 3)
    C = ((byts[1] >> 7) & 0b1) | ((byts[2] & 0b11111111) << 1) | ((byts[3] & 0b11111111) << 1 + 8) | ((byts[4] & 0b11111111) << 1 + 8 + 8)
    return A, B, C

def serialize_read(A,B,C):
    bytes_array = [0] * 4
    bytes_array[0] = (A & 0b11111) | ((B & 0b111) << 5)
    bytes_array[1] = ((B >> 3) & 0b1111111) | ((C & 0b1) << 7)
    bytes_array[2] = (C >> 1) & 0b11111111
    bytes_array[3] = (C >> (1 + 8)) & 0b1
    return bytes(bytes_array)

def deserialize_read(byts):
    A = byts[0] & 0b11111
    B = ((byts[0] >> 5) & 0b111) | ((byts[1] & 0b1111111) << 3)
    C = ((byts[1] >> 7) & 0b1) | ((byts[2] & 0b11111111) << 1) | ((byts[3] & 0b1) << 1 + 8)
    return A, B, C

def serialize_minus(A,B,C,D):
    bytes_array = [0] * 5
    bytes_array[0] = (A & 0b11111) | ((B & 0b111) << 5)
    bytes_array[1] = (B >> 3) & 0b1111_1111
    bytes_array[2] = ((B >> 11) & 0b1111) | ((C & 0b1111) << 4)
    bytes_array[3] = ((C >> 4) & 0b111111) | ((D & 0b11) << 6)
    bytes_array[4] = (D >> 2) & 0b11111111
    return bytes(bytes_array)



def assemble(input_file, output_bin, log_file):
    commands = {
        "LOAD_CONST": 30,
        "READ_MEM": 16,
        "WRITE_MEM": 18,
        "UNARY_MINUS": 22
    }
    binary_data = []
    log_data = []

    with open(input_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if not parts:
                continue
            cmd = parts[0]
            print(parts[0],parts[1],parts[2])
            if cmd == "LOAD_CONST":
                A = 30
                B = int(parts[1])  # Адрес
                C = int(parts[2])  # Константа

                # Проверка диапазонов
                if not (0 <= A <= 31):
                    raise ValueError(f"A (opcode) out of range: {A}")
                if not (0 <= B < (1 << 14)):
                    raise ValueError(f"B (address) out of range: {B}")
                if not (0 <= C < (1 << 22)):
                    raise ValueError(f"C (constant) out of range: {C}")

                # Формирование команды
                word = ((A & 0x1F) << 35) | ((B & 0x3FFF) << 21) | ((C & 0x3FFF) << 7)
                # word = ((A & 0x1E)) | ((B & 0x143)) | ((C & 0x1DC))
                if word >= (1 << 40):
                    raise ValueError(f"Word value too large for 5 bytes: {word} (cmd={cmd}, A={A}, B={B}, C={C})")

                binary_data.append(serialize_load(A,B,C))
                log_data.append({"command": cmd, "A": A, "B": B, "C": C, "bytes": serialize_load(A,B,C).hex()})

            elif cmd  == "READ_MEM":
                A = commands[cmd]
                B = int(parts[1])
                C = int(parts[2])
                word = ((A & 0x1F) << 35) | ((B & 0x3FFF) << 21) | ((C & 0x3FFF) << 7)
                binary_data.append(serialize_read(A,B,C))
                log_data.append({"command": cmd, "A": A, "B": B, "C": C, "bytes": serialize_read(A,B,C).hex()})
                print(A, B, C)
                print(deserialize_read(serialize_read(A, B, C)))
            elif cmd == "WRITE_MEM":
                A = commands[cmd]
                B = int(parts[1])
                C = int(parts[2])
                word = ((A & 0x1F) << 35) | ((B & 0x3FFF) << 21) | ((C & 0x3FFF) << 7)
                binary_data.append(serialize_read(A, B, C))
                log_data.append({"command": cmd, "A": A, "B": B, "C": C, "bytes": serialize_read(A, B, C).hex()})
                print(A,B,C)
                print(deserialize_read(serialize_read(A,B,C)))
            elif cmd == "UNARY_MINUS":
                A = commands[cmd]  # Код команды (в данном случае, A = 22)
                B = int(parts[1])  # Смещение
                C = int(parts[2])  # Адрес
                D = int(parts[3])  # Адрес для результата

                # Ожидаем, что B, C и D должны быть в пределах допустимого диапазона
                # Например, B и C — 14 бит, D — 12 бит (или другое соответствующее ограничение)

                if B >= (1 << 14) or C >= (1 << 14) or D >= (1 << 12):
                    raise ValueError(f"Operands out of range: B={B}, C={C}, D={D}")

                # Теперь собираем команду в 5 байтов:
                word = ((A & 0x1F) << 35) | ((B & 0x7FFF) << 21) | ((C & 0x3FF) << 7) | (D & 0x3FF)

                # Проверяем, не выходит ли значение за пределы 5 байтов
                if word >= (1 << 40):
                    raise ValueError(
                        f"Word value {word} is too large for 5 bytes (cmd={cmd}, A={A}, B={B}, C={C}, D={D})")

                # Добавляем результат в бинарные данные
                g = serialize_minus(A, B, C, D)
                binary_data.append(g)
                print(A, B, C, D)

                # print(deserialize_minus(g))

                # Логируем команду
                log_data.append({
                    "command": cmd,
                    "A": A,
                    "B": B,
                    "C": C,
                    "D": D,
                    "bytes": serialize_minus(A, B, C, D).hex()
                })

    # Save binary data
    with open(output_bin, 'wb') as bin_file:
        for data in binary_data:
            bin_file.write(data)

    # Save log data
    with open(log_file, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python assembler.py <input.asm> <output.bin> <log.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_bin = sys.argv[2]
    log_file = sys.argv[3]
    assemble(input_file, output_bin, log_file)
#python assembler.py test.asm output.bin log.json
# "f02840ee00"
# "8030200d00"
# "902360ee80"
# "b03260a1b7"