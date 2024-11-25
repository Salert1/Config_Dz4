import json
import struct
import sys


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
                A = commands[cmd]
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
                word = (A << 35) | (B << 21) | (C << 7)
                if word >= (1 << 40):
                    raise ValueError(f"Word value too large for 5 bytes: {word} (cmd={cmd}, A={A}, B={B}, C={C})")

                binary_data.append(word.to_bytes(5, 'big'))
                log_data.append({"command": cmd, "A": A, "B": B, "C": C, "bytes": word.to_bytes(5, 'big').hex()})
            elif cmd in ["READ_MEM", "WRITE_MEM"]:
                A = commands[cmd]
                B = int(parts[1])
                C = int(parts[2])
                word = (A << 35) | (B << 21) | (C << 7)
                binary_data.append(word.to_bytes(5, 'big'))
                log_data.append({"command": cmd, "A": A, "B": B, "C": C, "bytes": word.to_bytes(5, 'big').hex()})
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
                word = (A << 35) | (B << 21) | (C << 7) | D

                # Проверяем, не выходит ли значение за пределы 5 байтов
                if word >= (1 << 40):
                    raise ValueError(
                        f"Word value {word} is too large for 5 bytes (cmd={cmd}, A={A}, B={B}, C={C}, D={D})")

                # Добавляем результат в бинарные данные
                binary_data.append(word.to_bytes(5, 'big'))

                # Логируем команду
                log_data.append({
                    "command": cmd,
                    "A": A,
                    "B": B,
                    "C": C,
                    "D": D,
                    "bytes": word.to_bytes(5, 'big').hex()
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
