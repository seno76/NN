import argparse


# Проверка корректности записи вершин
def check_vertex(vertex):
    # Вершина должна состоять из двух символов: 'v' и числа
    if len(vertex) < 2 or vertex[0] != "v" or not vertex[1:].isdigit():
        return False
    return True

# Чтение файла с графом
def read_file(file_path):
    with open(file_path, "r", encoding="UTF-8") as f:
        data = f.readline()
    return data

# Чтение графа из файла серилизация
def read_graph(data):
    graph = []
    vertices = set()
    incoming_edges = {}
    
    if len(data) % 3 != 0:
        raise Exception("Неправильный формат данных: количество элементов должно быть кратно 3")
    
    for i in range(0, len(data), 3):
        tuple_ = data[i:i+3]
        v1 = tuple_[0].strip()
        v2 = tuple_[1].strip()
        n = tuple_[2].strip()

        if not check_vertex(v1) or not check_vertex(v2):
            raise Exception(f"Неправильная запись векторов: {v1}, {v2}")
        
        if not n.isdigit():
            raise Exception(f"'{n}' не является числом")
        n = int(n)
        if n <= 0:
            raise Exception(f"Номер дуги должен быть положительным числом: {n}")
        
        vertices.add(v1)
        vertices.add(v2)
        if (v1, v2, n) not in graph:
            graph.append((v1, v2, n))
        else:
            raise Exception(f"Ребро указано дважды: {(v1, v2, n)}")

        if v2 not in incoming_edges:
            incoming_edges[v2] = [n]
        else:
            incoming_edges[v2].append(n)

    for v in incoming_edges:
        max_el = max(incoming_edges[v])
        if sorted(incoming_edges[v]) != list(range(1, max_el + 1)):
            raise Exception(f"Порядок входящих дуг нарушен для вершины {v}: {incoming_edges[v]}")
    
    return sorted(list(vertices)), graph

#
def get_dict_graph(edges):
    graph = {}
    for v1, v2, num in edges:
        if v2 in graph:
            graph[v2].append((v1, num))
        else:
            graph[v2] = [(v1, num)]
    return graph

def find_stok(graph, vertices):
    # Все вершины, которые являются началом хотя бы одной дуги
    start_vertices = set()
    for key in graph:
        for i in range(len(graph[key])):
            start_vertices.add(graph[key][i][0])

    all_vertices = set(vertices)
    no_outgoing_edges = all_vertices - start_vertices

    return sorted(list(no_outgoing_edges))

# Функция для построения графа из списка рёбер
def build_graph(edges, vertices):
    graph = {v:[] for v in vertices}
    for v1, v2, _ in edges:
        graph[v1].append(v2)
    return graph

# Рекурсивная функция DFS для поиска цикла
def dfs_for_find_cycle(vertex, graph, visited, rec_stack):
    visited.add(vertex)
    rec_stack.add(vertex)

    for neighbor in graph[vertex]:
        if neighbor in rec_stack:
            return True
        elif neighbor not in visited:
            if dfs_for_find_cycle(neighbor, graph, visited, rec_stack):
                return True
    
    # Убираем вершину из стека рекурсивного вызова перед возвратом
    rec_stack.remove(vertex)
    return False

# Основная функция для проверки наличия цикла
def has_cycle(edges, vertices):
    graph = build_graph(edges, vertices)
    visited = set()
    
    # Проверяем каждую вершину, чтобы учитывать несвязные компоненты
    for vertex in graph:
        if vertex not in visited:
            rec_stack = set()
            if dfs_for_find_cycle(vertex, graph, visited, rec_stack):
                return True
    return False

def build_prefix_function(graph, start):
    if start not in graph:
        return start 

    sorted_edges = sorted(graph[start], key=lambda x: x[1])
    inner_parts = [build_prefix_function(graph, v) for v, _ in sorted_edges]

    return f"{start}({', '.join(inner_parts)})"

# Основная функция для построения префиксной записи для всех вершин без исходящих рёбер
def generate_prefix_functions(graph, root_vertices):
    result = []
    for root in root_vertices:
        result.append(build_prefix_function(graph, root))
    return result


def main(input_file, output_file):
    data = read_file(input_file).strip().replace('(', '').replace(')', '').split(",")
    vertices, edges = read_graph(data)
    if has_cycle(edges, vertices):
        raise Exception("Обнаружен цикл в графе")
    graph = get_dict_graph(edges)
    roots = find_stok(graph, vertices)
    print("Стоки гарфа:", *roots)
    prefix_funcs = generate_prefix_functions(graph, roots)
    with open(output_file, "w", encoding="UTF-8") as f:
        for p_fun in prefix_funcs:
            f.write(p_fun + "\n")

def parse_file(in_file, i, out_file):
# Обрабатываем каждый файл
    data = read_file(in_file).strip().replace('(', '').replace(')', '').split(",")
    try:
        vertices, edges = read_graph(data)
        print(f"Файл {i}: {in_file}")
        print("Вершины:", vertices)
        print("Граф:", edges)

        if has_cycle(edges, vertices):
            raise Exception("Обнаружен цикл в графе")
        graph = get_dict_graph(edges)
        roots = find_stok(graph, vertices)
        print("Стоки гарфа:", *roots)
        prefix_funcs = generate_prefix_functions(graph, roots)
        with open(out_file[:out_file.index(".")] + f"_{i}.txt" , "w", encoding="UTF-8") as f:
            for p_fun in prefix_funcs:
                f.write(p_fun + "\n")
        
    except Exception as e:
        message = f"Ошибка при обработке файла {in_file}: {e}"
        print(message)
        with open("errors.txt", "a", encoding="UTF-8") as f:
            f.write(message + '\n')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Программа для обработки множества графов.")
    parser.add_argument('-i', nargs='+', help='Входные файлы для обработки')
    parser.add_argument('-o', default="prefix_function.txt", help='Имя выходного файла (по умолчанию: default_output.txt)')

    args = parser.parse_args()
    out_file = args.o
    for i, data in enumerate(args.i):
        parse_file(data, i + 1, out_file) 


    # input_file = "input.txt"
    # output_file = "prefix_function.txt"
    # main(input_file, output_file)
