import re
import math

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

            # Выполняем функцию
            result = evaluate_operation(operation, evaluated_args)

            # Формируем строку подстановки для итогового вывода
            substituted_expression = f"{operation}(" + ", ".join(substituted_args) + f") = {result}"
            return result, substituted_expression
        else:
            raise ValueError(f"Неправильное выражение: {expr}")

    # Выполняем подстановку для выражения
    _, full_expression = recursive_evaluate(expression)
    return full_expression

# Пример входных данных
expressions = ['v4(v3(v2, v1, v2))', 'v5(v1, v3(v2, v1, v2), v6)']
operations = {'v1': 23.0, 'v2': 13.0, 'v3': '+', 'v4': 'exp', 'v5': '*', 'v6': 2.0}

# Обработка выражений
for expr in expressions:
    try:
        full_expression = substitute_values(expr, operations)
        print(full_expression)
    except ValueError as e:
        print(f"Ошибка при вычислении для {expr}: {e}")

# Пример входных данных
expressions = ['v4(v3(v2, v1, v2))', 'v5(v1, v3(v2, v1, v2), v6)']
operations = {'v1': 23, 'v2': 13, 'v3': '+', 'v4': 'exp', 'v5': '*', 'v6': 2}

# Обработка выражений
results = []
for expr in expressions:
    try:
        result = substitute_values(expr, operations)
        results.append(result)
        print(f"Результат для {expr}: {result}")
    except ValueError as e:
        print(f"Ошибка при вычислении для {expr}: {e}")