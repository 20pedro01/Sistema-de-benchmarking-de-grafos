import heapq
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra as scipy_dijkstra

def grafo_a_matriz_dispersa(grafo):
    """
    Convierte el diccionario de adyacencia a una matriz dispersa CSR de Scipy.
    """
    # 1. Obtener y ordenar nodos reales
    nodos_reales = sorted([str(u) for u in grafo if str(u) not in ["inyecciones", "v", "__is_stress_matrix__"]],
                          key=lambda x: int(x) if x.isdigit() else x)
    n = len(nodos_reales)
    n_to_idx = {nodo: i for i, nodo in enumerate(nodos_reales)}
    
    rows, cols, data = [], [], []
    for u_str in nodos_reales:
        u_idx = n_to_idx[u_str]
        ady = grafo.get(u_str) or grafo.get(int(u_str) if u_str.isdigit() else u_str) or {}
        for v_orig, w in ady.items():
            v_str = str(v_orig)
            if v_str in n_to_idx:
                rows.append(u_idx)
                cols.append(n_to_idx[v_str])
                data.append(w)
            
    return csr_matrix((data, (rows, cols)), shape=(n, n)), n_to_idx, nodos_reales

def dijkstra_profesional(grafo, source, matriz_pre=None, mapping_pre=None, return_output=True, **kwargs):
    """
    Dijkstra Híbrido: SciPy para grafos normales, Manual para negativos (Pedagógico).
    """
    is_stress = isinstance(grafo, dict) and grafo.get("__is_stress_matrix__")
    target = str(kwargs.get("target", ""))
    
    if matriz_pre is not None:
        matriz, n_to_idx = matriz_pre, mapping_pre[0]
    elif is_stress:
        matriz, n_to_idx = grafo["matrix"], None
    else:
        matriz, n_to_idx, _ = grafo_a_matriz_dispersa(grafo)

    s_idx = n_to_idx.get(str(source)) if n_to_idx else int(source)
    t_idx = n_to_idx.get(target) if n_to_idx else int(target)
    has_neg = (matriz.data < 0).any()

    # RAMA 1: MODO STRESS (V > 5000) o Grafos Generados Masivos
    if is_stress or matriz.shape[0] > 5000:
        if has_neg:
            # Modo Paciencia (Pedagógico en Stress)
            dist, _ = dijkstra_vulnerable(matriz, s_idx, max_iter=500000)
            d_val = dist[t_idx] if t_idx < len(dist) else float('inf')
            if d_val > 1e12:
                return ({"dist_target": "inf (Fallo)", "error": "Ciclo detectado o Paciencia agotada"}, {})
            return ({"dist_target": float(d_val) if d_val != float('inf') else "Inalcanzable"}, {})
        else:
            # Modo Rayo (Scipy)
            dist = scipy_dijkstra(matriz, indices=s_idx, directed=True)
            d_val = dist[t_idx] if t_idx < len(dist) else float('inf')
            return ({"dist_target": float(d_val) if d_val != float('inf') else "Inalcanzable"}, {})

    # RAMA 2: MODO NORMAL (Grafos pequeños)
    if has_neg:
        dist, _ = dijkstra_vulnerable(matriz, s_idx)
    else:
        dist = scipy_dijkstra(matriz, indices=s_idx, directed=True)
    
    d_val = dist[t_idx] if t_idx < len(dist) else float('inf')
    if d_val == float('inf'):
        return ({"dist_target": "Inalcanzable"}, {})
    
    return ({"dist_target": float(d_val)}, {})

def dijkstra_vulnerable(matriz, source_idx, max_iter=None):
    """
    Dijkstra manual que permite re-visitar nodos.
    Diseñado para fallar/ser lento en ciclos negativos (Modo Académico).
    """
    n = matriz.shape[0]
    dist = np.full(n, np.inf)
    dist[source_idx] = 0
    pred = np.full(n, -9999, dtype=int)
    
    pq = [(0, source_idx)]
    
    if max_iter is None:
        max_iter = n * 500 
    iterations = 0
    
    indptr = matriz.indptr
    indices = matriz.indices
    data = matriz.data
    
    while pq and iterations < max_iter:
        iterations += 1
        d_u, u = heapq.heappop(pq)
        
        if d_u > dist[u]: continue
        
        for i in range(indptr[u], indptr[u+1]):
            v = indices[i]
            w = data[i]
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                heapq.heappush(pq, (dist[v], v))
                
    return dist, pred
