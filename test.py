import json
import os


def run_test():
    assembler_input = """\
LOAD_CONST 0 10
LOAD_CONST 1 20
LOAD_CONST 2 30
LOAD_CONST 3 40
LOAD_CONST 4 50
LOAD_CONST 5 60

UNARY_MINUS 0 10 0
UNARY_MINUS 1 20 1
UNARY_MINUS 2 30 2
UNARY_MINUS 3 40 3
UNARY_MINUS 4 50 4
UNARY_MINUS 5 60 5
"""
    # Путь для временных файлов
    assembler_file = "test.asm"
    binary_file = "test.bin"
    log_file = "test.log"
    output_file = "result.json"

    # Ожидаемый результат
    expected_memory = [-10, -20, -30, -40, -50, -60] + [0] * 1018  # Остальная память заполнена нулями

    # Создаем входной файл для ассемблера
    with open(assembler_file, 'w') as asm_file:
        asm_file.write(assembler_input)

    # Выполняем сборку
    os.system(f"python assembler.py {assembler_file} {binary_file} {log_file}")

    # Запускаем интерпретатор
    os.system(f"python interpreter.py {binary_file} 0:1024 {output_file}")

    # Проверяем результат
    with open(output_file, 'r') as result_file:
        result_data = json.load(result_file)

    # Убедимся, что память соответствует ожидаемой
    assert result_data["values"][:1024] == expected_memory, "Memory state is incorrect"

    print("Test passed. Memory state is correct.")


if __name__ == "__main__":
    run_test()
