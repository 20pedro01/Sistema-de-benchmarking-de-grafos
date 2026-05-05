import random
import numpy as np
from scipy.sparse import csr_matrix


def generar_grafo(num_vertices, densidad=0.3, semilla=None, rango_pesos=(1, 15), source=0, target=None):
    """
    Genera un grafo aleatorio estructurado como diccionario de adyacencia o matriz CSR.
    
    :param num_vertices: Cantidad de nodos (V). Los nodos serán cadenas '0', '1', '2'...
    :param densidad: Probabilidad (0.0 a 1.0) de crear una arista entre dos nodos.
                     Densidad baja (ej. 0.1) = Grafo disperso, propenso a no ser conexo.
                     Densidad alta (ej. 0.8) = Grafo denso.
    :param semilla: Semilla aleatoria para garantizar reproducibilidad exacta.
    :param rango_pesos: Tupla (min, max) para los pesos aleatorios positivos de las aristas.
    :param source: Nodo origen para garantizar ruta.
    :param target: Nodo destino para garantizar ruta.
    :return: Grafo en formato diccionario de adyacencia o un diccionario de metadatos con la matriz CSR.
    """
    if semilla is not None:
        random.seed(semilla)
        
    if num_vertices <= 0:
        return {}
        
    if target is None:
        target = num_vertices - 1
        
    rango_pesos = (1, 15)
    
    # Variables auxiliares para el modo Stress
    row_indices, col_indices, data_values = [], [], []

    # Si el grafo está entre 10 y 20 nodos y la densidad es baja (<= 0.3), usamos modo normal
    # Fuera de estos límites se considera Modo Stress para benchmarks
    if num_vertices <= 20 and densidad <= 0.3:
        grafo = {str(i): {} for i in range(num_vertices)}
        
        # Garantizar ruta Source -> Target (Backbone dinámico)
        path_nodes = []
        if source < target:
            path_nodes = list(range(source, target + 1))
        elif source > target:
            path_nodes = list(range(source, target - 1, -1))
        else:
            path_nodes = list(range(num_vertices))

        for i in range(len(path_nodes) - 1):
            u_p, v_p = path_nodes[i], path_nodes[i+1]
            grafo[str(u_p)][str(v_p)] = random.randint(rango_pesos[0], rango_pesos[1])
            
        # Aristas extras
        num_aristas_total = int(num_vertices * (num_vertices - 1) * densidad)
        aristas_actuales = len(path_nodes) - 1
        intentos = 0
        while aristas_actuales < num_aristas_total and intentos < num_aristas_total * 3:
            u, v = random.randint(0, num_vertices-1), random.randint(0, num_vertices-1)
            if u != v and str(v) not in grafo[str(u)]:
                grafo[str(u)][str(v)] = random.randint(rango_pesos[0], rango_pesos[1])
                aristas_actuales += 1
            intentos += 1
        return grafo
    
    # Modo Stress (Matriz CSR)
    # Ruta Backbone Source -> Target
    path_nodes = []
    if source < target:
        path_nodes = list(range(source, target + 1))
    elif source > target:
        path_nodes = list(range(source, target - 1, -1))
    else:
        path_nodes = list(range(num_vertices))

    for i in range(len(path_nodes) - 1):
        row_indices.append(path_nodes[i]); col_indices.append(path_nodes[i+1])
        data_values.append(random.randint(rango_pesos[0], rango_pesos[1]))
    
    num_extras = min(int(num_vertices * 10 * densidad), 2_000_000)
    if num_extras > 0:
        rng = np.random.default_rng(semilla)
        row_indices.extend(rng.integers(0, num_vertices, size=num_extras))
        col_indices.extend(rng.integers(0, num_vertices, size=num_extras))
        data_values.extend(rng.integers(rango_pesos[0], rango_pesos[1] + 1, size=num_extras))
    
    matrix = csr_matrix((data_values, (row_indices, col_indices)), shape=(num_vertices, num_vertices))
    return {"matrix": matrix, "v": num_vertices, "__is_stress_matrix__": True}

def inyectar_peso_negativo(grafo, cantidad=1, semilla=None, rango_negativo=(-10, -1)):
    """
    Toma un grafo existente y cambia el peso de aristas aleatorias a valores negativos.
    
    :param grafo: Diccionario de adyacencia modificado por referencia.
    :param cantidad: Número máximo de aristas a corromper con pesos negativos.
    :param semilla: Semilla aleatoria para reproducibilidad.
    :param rango_negativo: Rango (min, max) para los nuevos pesos.
    :return: El grafo con pesos negativos.
    """
    if semilla is not None:
        random.seed(semilla)
        
    if isinstance(grafo, dict) and grafo.get("__is_stress_matrix__"):
        # Modo Stress: Modificar directamente los datos de la matriz CSR
        matriz = grafo["matrix"]
        if matriz.nnz > 0:
            indices_a_modificar = random.sample(range(matriz.nnz), min(cantidad, matriz.nnz))
            for idx in indices_a_modificar:
                matriz.data[idx] = random.randint(rango_negativo[0], rango_negativo[1])
        return grafo

    # Modo Normal: Diccionario de adyacencia
    aristas_disponibles = []
    for u in grafo:
        for v in grafo[u]:
            aristas_disponibles.append((u, v))
            
    if not aristas_disponibles:
        return grafo
        
    aristas_a_modificar = random.sample(aristas_disponibles, min(cantidad, len(aristas_disponibles)))
    for u, v in aristas_a_modificar:
        grafo[u][v] = random.randint(rango_negativo[0], rango_negativo[1])
        
    return grafo


def inyectar_ciclo_negativo(grafo, cantidad=1, semilla=None):
    """
    Toma un grafo existente y fuerza la creación de múltiples ciclos negativos.
    """
    if semilla is not None:
        random.seed(semilla)
        
    if isinstance(grafo, dict) and grafo.get("__is_stress_matrix__"):
        matriz = grafo["matrix"]
        n = grafo["v"]
        if n >= 3 and matriz.nnz > 0:
            # Inyectar múltiples puntos de falla en el backbone o aristas aleatorias
            # Usar un valor muy negativo para asegurar que la suma del ciclo sea < 0
            indices = random.sample(range(min(matriz.nnz, n*10)), min(cantidad, matriz.nnz, n*10))
            for idx in indices:
                matriz.data[idx] = -2000
        return grafo

    # Modo Normal
    nodos = list(grafo.keys())
    for _ in range(cantidad):
        if len(nodos) >= 3:
            n1, n2, n3 = random.sample(nodos, 3)
            grafo[n1][n2] = 2; grafo[n2][n3] = 2; grafo[n3][n1] = -10
        elif len(nodos) == 2:
            n1, n2 = nodos
            grafo[n1][n2] = 2; grafo[n2][n1] = -10
            
    return grafo


def sanitizar_pesos(grafo, rango_pesos=(1, 15)):
    """
    Elimina todos los pesos negativos del grafo, restaurando la coherencia positiva.
    """
    if isinstance(grafo, dict) and grafo.get("__is_stress_matrix__"):
        matriz = grafo["matrix"]
        # Encontrar donde hay pesos <= 0
        mask = matriz.data <= 0
        if mask.any():
            matriz.data[mask] = np.random.randint(rango_pesos[0], rango_pesos[1] + 1, size=mask.sum())
        return grafo

    # Modo Normal
    for u in grafo:
        for v in grafo[u]:
            if grafo[u][v] < 0:
                grafo[u][v] = random.randint(rango_pesos[0], rango_pesos[1])
    return grafo
