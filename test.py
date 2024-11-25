import subprocess
import json
import os

def run_test():
    input_asm = "test_input.asm"
    output_bin = "test_output.bin"
    log_file = "test_log.json"
    result_file = "test_result.json"

    asm_code = """
LOAD_CONST 3 12
UNARY_MINUS 5 6 2
READ_MEM 7 3
WRITE_MEM 3 7
"""

    # Ожидаемое состояние памяти
    expected_memory = [0] * 1024
    expected_memory[3] = 12  # LOAD_CONST
    expected_memory[2] = -0  # UNARY_MINUS
    expected_memory[7] = 12  # READ_MEM
    expected_memory[12] = 12  # WRITE_MEM (address stored in memory[7])

    # Создаем файл для ассемблера
    with open(input_asm, 'w') as f:
        f.write(asm_code.strip())

    # Запускаем ассемблер
    subprocess.run(["python", "assembler.py", input_asm, output_bin, log_file], check=True)

    # Проверяем, что бинарный файл создан
    assert os.path.exists(output_bin), "Assembler output not created"

    # Запускаем интерпретатор
    subprocess.run(["python", "interpreter.py", output_bin, "0:1024", result_file], check=True)

    # Проверяем, что результат интерпретации сохранен
    assert os.path.exists(result_file), "Interpreter output not created"

    # Проверяем лог
    with open(log_file, 'r') as f:
        log_data = json.load(f)
    assert log_data[0]["command"] == "LOAD_CONST"
    assert log_data[1]["command"] == "UNARY_MINUS"
    assert log_data[2]["command"] == "READ_MEM"
    assert log_data[3]["command"] == "WRITE_MEM"

    # Проверяем результат интерпретации
    with open(result_file, 'r') as f:
        result_data = json.load(f)

    assert result_data["memory_range"] == [0, 1024], "Incorrect memory range"

    # Добавляем вывод текущего состояния памяти
    current_memory = result_data["values"][:16]
    print("Expected memory:", expected_memory[:16])
    print("Current memory: ", current_memory)

    assert current_memory == expected_memory[:16], "Memory state is incorrect"

    print("Test passed!")

    # Удаляем временные файлы после теста
    os.remove(input_asm)
    os.remove(output_bin)
    os.remove(log_file)
    os.remove(result_file)

run_test()
