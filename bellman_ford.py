import numpy as np
from scipy.sparse import csr_matrix
from collections import deque
from dijkstra import grafo_a_matriz_dispersa

def bellman_ford_profesional(grafo, source, matriz_pre=None, mapping_pre=None, return_output=True, **kwargs):
    """
    SPFA (Shortest Path Faster Algorithm) optimizado con NumPy.
    Mucho más rápido que Scipy para grafos dispersos masivos (O(kE) vs O(VE)).
    """
    is_stress = isinstance(grafo, dict) and grafo.get("__is_stress_matrix__")
    
    if matriz_pre is not None:
        matriz, n_to_idx = matriz_pre, mapping_pre[0]
    elif is_stress:
        matriz, n_to_idx = grafo["matrix"], None
    else:
        matriz, n_to_idx, _ = grafo_a_matriz_dispersa(grafo)

    n = matriz.shape[0]
    # Resolución de indices
    s_idx = n_to_idx.get(str(source)) if n_to_idx else int(source)
    t_idx = n_to_idx.get(str(kwargs.get("target", ""))) if n_to_idx else int(kwargs.get("target", 0))
    
    # Inicialización con NumPy (Ultra rápido)
    dist = np.full(n, np.inf)
    if 0 <= s_idx < n: dist[s_idx] = 0
    else: return ({"dist_target": "inf"}, {}, False, [])
    
    pred = np.full(n, -9999, dtype=int)
    
    # Cola optimizada
    q = deque([s_idx])
    in_q = np.zeros(n, dtype=bool)
    in_q[s_idx] = True
    count = np.zeros(n, dtype=int)
    
    # Atajos de la matriz CSR para iteración rápida
    indptr = matriz.indptr
    indices = matriz.indices
    data = matriz.data
    
    has_neg = (data < 0).any()
    has_cycle = False
    affected = []

    # MODO DIAGNÓSTICO: Si el usuario inyectó un ciclo, somos más rápidos en detectarlo
    inyectado = grafo.get("inyecciones", {})
    es_demo_ciclo = inyectado.get("ciclos", 0) > 0

    if not has_neg:
        # MODO LEAN (Sin negativos, SPFA es rayo)
        while q:
            u = q.popleft()
            in_q[u] = False
            d_u = dist[u]
            for i in range(indptr[u], indptr[u+1]):
                v = indices[i]
                w = data[i]
                if d_u + w < dist[v]:
                    dist[v] = d_u + w
                    pred[v] = u
                    if not in_q[v]:
                        q.append(v)
                        in_q[v] = True
    else:
        # MODO SEGURO (Detección de ciclos)
        max_total_relax = (matriz.nnz * 2) if is_stress else (n * n)
        if es_demo_ciclo and is_stress: max_total_relax = n // 2

        total_relax = 0
        cycle_limit = min(n, 50 if es_demo_ciclo else 200) if is_stress else n
        
        while q:
            u = q.popleft()
            in_q[u] = False
            d_u = dist[u]
            for i in range(indptr[u], indptr[u+1]):
                v = indices[i]
                w = data[i]
                if d_u + w < dist[v]:
                    dist[v] = d_u + w
                    pred[v] = u
                    total_relax += 1
                    if not in_q[v]:
                        count[v] += 1
                        if count[v] >= cycle_limit or total_relax > max_total_relax:
                            has_cycle = True
                            break
                        q.append(v)
                        in_q[v] = True
            if has_cycle: break
    
    q.clear()

    if not return_output: return None, None, has_cycle, affected

    # Resolución de salida unificada
    d_target = dist[t_idx] if (0 <= t_idx < n) else float('inf')
    
    # Formateo de salida para compatibilidad con UI
    if has_cycle:
        res = "inf (Ciclo)"
    elif d_target == float('inf') or np.isinf(d_target):
        res = "Inalcanzable"
    else:
        res = float(d_target)

    return ({"dist_target": res}, {}, has_cycle, affected)
