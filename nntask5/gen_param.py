import numpy as np

def generate_large_network(input_size, hidden_size, output_size, file_path, count=10):
    network = [
        np.random.rand(hidden_size, input_size).tolist() for _ in range(count)  # Скрытый -> выходной
    ]
    with open(file_path, "w") as file:
        for layer in network:
            file.write(f"{layer}\n")

# Исправлено: входной слой из 4 нейронов, скрытый — 5, выходной — 3
generate_large_network(3, 3, 3, "network.txt")

def generate_large_training_data(num_samples, input_size, output_size, file_path):
    with open(file_path, "w") as file:
        for _ in range(num_samples):
            x = np.random.rand(input_size).tolist()  # Входной вектор (размер 4)
            y = np.random.rand(output_size).tolist()  # Выходной вектор (размер 3)
            file.write(f"{x} -> {y}\n")

# Исправлено: входной вектор из 4 элементов, выходной — из 3
generate_large_training_data(3, 3, 3, "vectors.txt")