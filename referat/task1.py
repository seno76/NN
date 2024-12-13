import numpy as np
import matplotlib.pyplot as plt

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

# Метод обратного распространения ошибки с различными градиентными методами
def train_network(network, training_data, iterations, learning_rate, method, output_file="training_history.txt"):
    history = []

    with open(output_file, "w") as file:
        momentum = [np.zeros_like(layer) for layer in network]
        rprop_grad_prev = [np.zeros_like(layer) for layer in network]
        rprop_step = [np.full_like(layer, 0.1) for layer in network]
        adagrad_cache = [np.zeros_like(layer) for layer in network]
        adadelta_cache = [np.zeros_like(layer) for layer in network]
        adadelta_momentum = [np.zeros_like(layer) for layer in network]
        adam_m = [np.zeros_like(layer) for layer in network]
        adam_v = [np.zeros_like(layer) for layer in network]
        beta1, beta2, epsilon = 0.9, 0.999, 1e-8

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

                # Обратное распространение
                deltas = [error * sigmoid_derivative(activations[-1])]
                for i in range(len(network) - 1, 0, -1):
                    delta = deltas[-1].dot(network[i].T) * sigmoid_derivative(activations[i])
                    deltas.append(delta)
                deltas.reverse()

                # Обновление весов
                for i in range(len(network)):
                    gradient = activations[i][:, np.newaxis] @ deltas[i][np.newaxis, :]

                    if method == "SGD":
                        network[i] += learning_rate * gradient
                    elif method == "Momentum":
                        momentum[i] = 0.9 * momentum[i] + learning_rate * gradient
                        network[i] += momentum[i]
                    elif method == "QuickProp":
                        network[i] += gradient / (np.abs(gradient) + epsilon) * learning_rate
                    elif method == "RProp":
                        sign_change = np.sign(rprop_grad_prev[i] * gradient)
                        rprop_step[i][sign_change > 0] *= 1.2
                        rprop_step[i][sign_change < 0] *= 0.5
                        rprop_grad_prev[i] = gradient
                        network[i] += rprop_step[i] * np.sign(gradient)
                    elif method == "ConjugateGradient":
                        # Упрощённый placeholder, полноценный метод требует больше логики
                        network[i] += learning_rate * gradient
                    elif method == "NAG":
                        lookahead = network[i] + 0.9 * momentum[i]
                        momentum[i] = 0.9 * momentum[i] + learning_rate * gradient
                        network[i] = lookahead + momentum[i]
                    elif method == "AdaGrad":
                        adagrad_cache[i] += gradient ** 2
                        network[i] += learning_rate * gradient / (np.sqrt(adagrad_cache[i]) + epsilon)
                    elif method == "AdaDelta":
                        adadelta_cache[i] = 0.9 * adadelta_cache[i] + 0.1 * gradient ** 2
                        update = gradient * np.sqrt(adadelta_momentum[i] + epsilon) / np.sqrt(adadelta_cache[i] + epsilon)
                        adadelta_momentum[i] = 0.9 * adadelta_momentum[i] + 0.1 * update ** 2
                        network[i] += update
                    elif method == "Adam":
                        adam_m[i] = beta1 * adam_m[i] + (1 - beta1) * gradient
                        adam_v[i] = beta2 * adam_v[i] + (1 - beta2) * (gradient ** 2)
                        m_hat = adam_m[i] / (1 - beta1 ** iteration)
                        v_hat = adam_v[i] / (1 - beta2 ** iteration)
                        network[i] += learning_rate * m_hat / (np.sqrt(v_hat) + epsilon)

            # Сохранение ошибки для текущей итерации
            history.append(total_error)
            file.write(f"Iteration {iteration}: Error = {total_error}\n")

    return history

# Построение графика
def plot_training_history(histories, methods):
    plt.figure(figsize=(10, 6))
    for history, method in zip(histories, methods):
        plt.plot(history, label=method)
    plt.xlabel("Итерации")
    plt.ylabel("Ошибка")
    plt.title("Сравнение скорости сходимости градиентных методов")
    plt.legend()
    plt.grid()
    plt.savefig("training_comparison.png")
    plt.show()

# Основная программа
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 5:
        print("Использование: python nntask5.py <network_file> <training_file> <iterations> <learning_rate>")
        sys.exit(1)

    network_file = sys.argv[1]
    training_file = sys.argv[2]
    iterations = int(sys.argv[3])
    learning_rate = float(sys.argv[4])

    network = load_network(network_file)
    training_data = load_training_data(training_file)

    methods = [
        "SGD", "Momentum", "QuickProp", "RProp", "ConjugateGradient",
        "NAG", "AdaGrad", "AdaDelta", "Adam"
    ]
    histories = []

    for method in methods:
        # Копируем сеть для каждого метода
        network_copy = [np.copy(layer) for layer in network]

        try:
            output_file = f"training_history_{method}.txt"
            history = train_network(network_copy, training_data, iterations, learning_rate, method, output_file=output_file)
            histories.append(history)
        except Exception as err:
            with open("error.txt", "w", encoding="UTF-8") as f:
                f.write(f"Ошибка для метода {method}: {str(err)}\n")
            print(f"Ошибка для метода {method}! Подробности сохранены в 'error.txt'.")

    # Построение графика
    plot_training_history(histories, methods)