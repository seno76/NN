import argparse
import math
import re

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

    # Все вершины графа, включая начальные и конечные
    all_vertices = set(vertices)
    # Вершины, из которых не исходит ни одной дуги
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

def has_cycle(edges, vertices):
    graph = build_graph(edges, vertices)
    visited = set()
    
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

def generate_prefix_functions(graph, root_vertices):
    result = []
    for root in root_vertices:
        result.append(build_prefix_function(graph, root))
    return result

# Функция для выполнения операции
def evaluate_operation(operation, args):
    if operation == '+':
        return sum(args)
    elif operation == '*':
        result = 1
        for arg in args:
            result *= arg
        return result
    elif operation == 'exp':
        if len(args) != 1:
            raise ValueError("Функция exp должна принимать только один аргумент.")
        return math.exp(args[0])
    else:
        raise ValueError(f"Неизвестная операция: {operation}")


# Функция для подстановки значений из словаря и вычисления выражения
def substitute_values(expression, operations):
    # Рекурсивная функция для разбора и вычисления
    def recursive_evaluate(expr):
        expr = expr.strip()

        # Если это просто вершина, возвращаем значение из словаря
        if expr in operations:
            value = operations[expr]
            if isinstance(value, str):  # Если это функция, а не константа
                raise ValueError(f"{expr} должно быть функцией, но является константой.")
            return value, str(value)

        # Ищем функцию с аргументами
        match = re.match(r'([a-zA-Z0-9_]+)\((.*)\)', expr)
        if match:
            node = match.group(1)
            if node not in operations:
                raise ValueError(f"Неизвестная вершина {node} в выражении.")

            operation = operations[node]
            if isinstance(operation, (int, float)):
                raise ValueError(f"{node} должно быть функцией, но является константой.")

            # Разбираем аргументы функции, учитывая вложенность
            args_str = match.group(2)
            args = []
            bracket_level = 0
            current_arg = []

            for char in args_str:
                if char == ',' and bracket_level == 0:
                    args.append(''.join(current_arg).strip())
                    current_arg = []
                else:
                    if char == '(':
                        bracket_level += 1
                    elif char == ')':
                        bracket_level -= 1
                    current_arg.append(char)
            args.append(''.join(current_arg).strip())

            # Рекурсивно вычисляем каждый аргумент
            evaluated_args = []
            substituted_args = []
            for arg in args:
                eval_result, sub_expr = recursive_evaluate(arg)
                evaluated_args.append(eval_result)
                substituted_args.append(sub_expr)

            result = evaluate_operation(operation, evaluated_args)

            # Формируем строку подстановки для итогового вывода
            substituted_expression = f"{operation}(" + ", ".join(substituted_args) + f") = {result}"
            return result, substituted_expression
        else:
            raise ValueError(f"Неправильное выражение: {expr}")

    # Выполняем подстановку для выражения
    _, full_expression = recursive_evaluate(expression)
    return full_expression

# Пример использования
def process_graph(graph, operations, out_file, i, in_file):
    with open(out_file[:out_file.index(".")] + f"_{i}.txt", "w", encoding="UTF-8") as f:
        for expr in graph:
            try:
                result = substitute_values(expr, operations)
                str_ = f"Результат для {expr}: {result}"
                f.write(str_ + "\n")
                print(str_)
            except Exception as e:
                message = f"Ошибка при обработке файла {in_file}: {e}"
                print(message)
                with open("errors.txt", "a", encoding="UTF-8") as f:
                    f.write(message + '\n')
                print(f"Ошибка при вычислении для {expr}: {e}")

def load_operations(file_path):
    operations = {}
    
    # Открываем файл для чтения
    with open(file_path, 'r') as f:
        for line in f:
            if line:
                # Разделяем строку на ключ и значение по символу ":"
                key_value = line.split(':')
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    
                    # Преобразуем значение: если это число, то конвертируем в int, иначе оставляем как строку
                    try:
                        value = int(value)  # Это безопасно для числа и строки
                    except (ValueError, SyntaxError):
                        pass
                    
                    operations[key] = value
                    
    return operations

def main(input_file, output_file, operation_file):
    data = read_file(input_file).strip().replace('(', '').replace(')', '').split(",")
    vertices, edges = read_graph(data)
    if has_cycle(edges, vertices):
        raise Exception("Обнаружен цикл в графе")
    graph = get_dict_graph(edges)
    roots = find_stok(graph, vertices)
    print("Стоки гарфа:", *roots)
    prefix_funcs = generate_prefix_functions(graph, roots)
    print(prefix_funcs)
    operations = load_operations(operation_file)
    print(operations)
    print(process_graph(prefix_funcs, operations, output_file))


def parse_file(in_file, i, out_file, operation_file):
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
        operations = load_operations(operation_file)
        print("Операции: ", operations)
        print(process_graph(prefix_funcs, operations, out_file, i, in_file))
        
    except Exception as e:
        message = f"Ошибка при обработке файла {in_file}: {e}"
        print(message)
        with open("errors.txt", "a", encoding="UTF-8") as f:
            f.write(message + '\n')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Программа для обработки множества графов.")
    parser.add_argument('-i', nargs='+', help='Входные файлы для обработки')
    parser.add_argument('-o', default="output.txt", help='Имя выходного файла (по умолчанию: output.txt)')
    parser.add_argument('-op', default="op.txt", help='Имя файла операций (по умолчанию: op.txt)')

    args = parser.parse_args()
    out_file = args.o
    operation_file = args.op
    for i, data in enumerate(args.i):
        parse_file(data, i + 1, out_file, operation_file)


    # input_file = "input.txt"
    # output_file = "result.txt"
    # op_file = "op.txt"
    # main(input_file, output_file, op_file)