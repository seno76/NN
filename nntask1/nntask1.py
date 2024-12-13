import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import argparse

def check_correct_data(data):
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

def check_vertex(vertex):
    # Вершина должна состоять из двух символов: 'v' и числа
    if len(vertex) < 2 or vertex[0] != "v" or not vertex[1:].isdigit():
        return False
    return True

def generate_xml(vertices, graph):
    root = ET.Element("graph")
    
    for vertex in vertices:
        vertex_elem = ET.SubElement(root, "vertex")
        vertex_elem.text = vertex

    for v1, v2, n in graph:
        arc_elem = ET.SubElement(root, "arc")
        from_elem = ET.SubElement(arc_elem, "from")
        from_elem.text = v1
        to_elem = ET.SubElement(arc_elem, "to")
        to_elem.text = v2
        order_elem = ET.SubElement(arc_elem, "order")
        order_elem.text = str(n)
    
    xml_string = ET.tostring(root, encoding='unicode', method='xml')
    
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="    ")
    
    return pretty_xml

def parse_file(in_file, i):
# Обрабатываем каждый файл
    data = read_file(in_file).strip().replace('(', '').replace(')', '').split(",")
    try:
        vertices, graph = check_correct_data(data)
        print(f"Файл {i}: {in_file}")
        print("Вершины:", vertices)
        print("Граф:", graph)
        
        pretty_xml_data = generate_xml(vertices, graph)
        
        with open(f"graph_output_{i}.xml", "w", encoding="UTF-8") as f:
            f.write(pretty_xml_data)
        print(f"\nXML документ сохранён в 'graph_output_{i}.xml'")
        
    except Exception as e:
        message = f"Ошибка в файле {in_file}: {e}"
        print(message)
        with open("errors.txt", "a", encoding="UTF-8") as f:
            f.write(message + '\n')
    

def read_file(file_path):
    with open(file_path, "r", encoding="UTF-8") as f:
        data = f.readline()
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Программа для обработки множества графов.")
    parser.add_argument('-i', nargs='+', help='Входные файлы для обработки')

    args = parser.parse_args()
    for i, data in enumerate(args.i):
        parse_file(data, i + 1) 