import numpy as np

# Функция активации (сигмоида) и её производная
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

# Загрузка нейронной сети из файла
def load_network(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        layers = [eval(line.strip()) for line in lines]
    return [np.array(layer) for layer in layers]

# Загрузка обучающей выборки
def load_training_data(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        data = []
        for line in lines:
            x, y = line.strip().split("->")
            x = eval(x.strip())
            y = eval(y.strip())
            data.append((np.array(x), np.array(y)))
    return data

# Метод обратного распространения ошибки
def train_network(network, training_data, iterations, output_file="training_history.txt"):
    history = []
    
    for iteration in range(1, iterations + 1):
        total_error = 0
        for x, y in training_data:
            
            # Прямое распространение
            activations = [x]
            for layer in network:
                activations.append(sigmoid(np.dot(activations[-1], layer)))

            # Ошибка выходного слоя
            error = y - activations[-1]
            total_error += np.sum(error ** 2)
            # print(error, total_error)

            # Обратное распространение
            deltas = [error * sigmoid_derivative(activations[-1])]
            for i in range(len(network) - 1, 0, -1):
                delta = deltas[-1].dot(network[i].T) * sigmoid_derivative(activations[i])
                deltas.append(delta)
            deltas.reverse()

            # Обновление весов
            for i in range(len(network)):
                network[i] += activations[i][:, np.newaxis] @ deltas[i][np.newaxis, :]

        # Сохранение ошибки для текущей итерации
        history.append(f"{iteration} : {total_error}")

    # Запись истории обучения в файл
    with open(output_file, "w") as file:
        file.write("\n".join(history))

# Основная программа
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Использование: python nntask5.py <network_file> <training_file> <iterations>")
        sys.exit(1)

    network_file = sys.argv[1]
    training_file = sys.argv[2]
    iterations = int(sys.argv[3])

    network = load_network(network_file)
    training_data = load_training_data(training_file)

    try:

        # Обучение нейронной сети
        train_network(network, training_data, iterations)
        print("Обучение завершено. История сохранена в 'training_history.txt'.")
    
    except Exception as err:

        with open("error.txt", "w", encoding="UTF-8") as f:
            f.write(str(err))
        print("Ошибка в процессе обучения!! Ошибка сохранена в 'error.txt'.")