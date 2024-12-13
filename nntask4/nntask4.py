import argparse
import json
import math
import os

# Чтение вектора из файла
def read_vector(file_path):
    try:
        with open(file_path, 'r') as file:
            return list(map(float, file.readline().strip().split(',')))
    except Exception as e:
        raise ValueError(f"Ошибка чтения входного вектора: {e}")

# Чтение состояния нейронной сети (весов) из файла
def read_nn_state(file_path):
    try:
        with open(file_path, 'r') as file:
            weights = []
            for line in file:
                weights.append(json.loads(line.strip()))
            return weights
    except Exception as e:
        raise ValueError(f"Ошибка чтения состояния сети: {e}")

# Сигмоидная функция активации
def sigmoid(z, c):
    return 1.0 / (1.0 + math.exp(-c * z))

# Прямое распространение
def forward_pass(weights, input_vector, c=1):
    activations = input_vector
    for layer in weights:
        if len(activations) != len(layer[0]):
            raise ValueError("Длина входного вектора не совпадает с матрицей весов")
        next_activations = []
        for neuron_weights in layer:
            z = sum(w * a for w, a in zip(neuron_weights, activations))
            next_activations.append(sigmoid(z, c))
        activations = next_activations
    return activations

# Запись выходного вектора в файл
def write_output(output_vector, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(', '.join(map(str, output_vector)))
    except Exception as e:
        raise ValueError(f"Ошибка записи выходного вектора: {e}")

# Сериализация состояния сети
def serialize_nn(weights, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump({'layers': weights}, file, indent=2)
    except Exception as e:
        raise ValueError(f"Ошибка сериализации сети: {e}")


def main(args):
    error_log = "errors.txt"
    if os.path.exists(error_log):
        os.remove(error_log)

    for idx, nn_file in enumerate(args.nn_files, start=1):
        try:
            weights = read_nn_state(nn_file)
            input_vector = read_vector(args.input_vector)
            
            output_vector = forward_pass(weights, input_vector)
            
            if len(args.nn_files) > 1:
                output_file = f"output_{idx}.txt"
                output_network_file = f"outputNetwork_{idx}.json"
            else:
                output_file = args.output_file
                output_network_file = args.output_network
            
            write_output(output_vector, output_file)
            serialize_nn(weights, output_network_file)
            
            print(f"Результат успешно сохранён для {nn_file}:")
            print(f"  Выходной вектор: {output_file}")
            print(f"  Сериализация сети: {output_network_file}")
        except ValueError as e:
            with open(error_log, 'a', encoding="UTF-8") as error_file:
                error_file.write(f"Ошибка в файле {nn_file}: {e}\n")
            print(f"Ошибка обработки {nn_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Программа для прямого распространения в нейронной сети.")
    parser.add_argument(
        '-i', '--nn_files', nargs='+', default=['input.txt'], 
        help="Список файлов с весами нейронной сети (по умолчанию: input.txt)"
    )
    parser.add_argument(
        '--input_vector', default='input_vector.txt', 
        help="Файл с входным вектором (по умолчанию: input_vector.txt)"
    )
    parser.add_argument(
        '--output_file', default='output.txt', 
        help="Файл для записи выходного вектора (по умолчанию: output.txt)"
    )
    parser.add_argument(
        '--output_network', default='outputNetwork.json', 
        help="Файл для сериализации состояния сети (по умолчанию: outputNetwork.json)"
    )

    args = parser.parse_args()
    main(args)