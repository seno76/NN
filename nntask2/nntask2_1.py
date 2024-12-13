import re
from collections import defaultdict


def check_vertex(vertex):
    # Вершина должна состоять из двух символов: 'v' и числа
    if len(vertex) < 2 or vertex[0] != "v" or not vertex[1:].isdigit():
        return False
    return True

def read_file(file_path):
    with open(file_path, "r", encoding="UTF-8") as f:
        data = f.readline()
    return data

# Чтение графа из файла
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

# Представление матрицы смежности для графа
class Matrix:
    def __init__(self, size):
        self.data = [[[] for _ in range(size)] for _ in range(size)]
        self.size = size

    def set_element(self, i, j, val):
        self.data[i][j].append(val)

    def get_root(self, start):
        for i in range(start, self.size):
            root = all(len(self.data[j][i]) == 0 for j in range(self.size))
            if root:
                print(root, i)
                return i
        
        return -1

    def get_row(self, i):
        return self.data[i]

# Граф с сортировкой вершин и дуг
class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = []

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def add_edge(self, edge):
        self.edges.append(edge)

    def sort_vertices(self):
        self.vertices.sort()

    def sort_edges(self):
        self.edges.sort(key=lambda e: (e[1], e[2]))

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges

# DFS для обхода графа и построения префиксной записи
class DFS:
    def __init__(self, vertex_map):
        self.vertex_check = [0] * len(vertex_map)
        self.vertex_map = vertex_map

    def has_unchecked(self):
        return any(v == 0 for v in self.vertex_check)

    def order_dfs(self, matrix, root):
        res = []
        row = matrix.get_row(root)
        children = [(val, idx) for idx, vals in enumerate(row) for val in vals]
        children.sort(key=lambda x: x[0])

        res.append(self.vertex_map[root])
        self.vertex_check[root] = 1
        if not children:
            return ''.join(res)

        res.append("(")
        for _, child_idx in children:
            res.append(self.order_dfs(matrix, child_idx))
            res.append(", ")
        res.pop()  # Удалить последнюю запятую
        res.append(")")
        return ''.join(res)

# Основная функция
def main(input_file, output_file):
    data = read_file(input_file).strip().replace('(', '').replace(')', '').split(",")
    vertices, edges = read_graph(data)
    graph = Graph()
    for vertex in vertices:
        graph.add_vertex(vertex)
    for edge in edges:
        graph.add_edge(edge)

    graph.sort_vertices()
    graph.sort_edges()

    vertex_map = {i: v for i, v in enumerate(graph.get_vertices())}
    vertex_map_rev = {v: i for i, v in vertex_map.items()}

    matrix = Matrix(len(vertex_map))
    for v1, v2, order in graph.get_edges():
        i1 = vertex_map_rev[v2]
        i2 = vertex_map_rev[v1]
        matrix.set_element(i1, i2, order)

    root = matrix.get_root(0)
    if root == -1:
        raise Exception("В графе присутствует цикл, ошибка")

    dfs = DFS(vertex_map)
    result = []
    while root != -1:
        result.append(dfs.order_dfs(matrix, root))
        root = matrix.get_root(root + 1)

    if dfs.has_unchecked():
        raise Exception("В графе присутствует цикл, ошибка")

    with open(output_file, "w", encoding="UTF-8") as file:
        file.write('\n'.join(result))

# Запуск программы
input_file = "input.txt"  # Входной файл с описанием графа
output_file = "p1rdsefix_function.txt"  # Выходной файл с префиксной записью функции

main(input_file, output_file)