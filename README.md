# 📊 Plataforma de benchmarking: Dijkstra versus Bellman-Ford

Una herramienta profesional de análisis comparativo diseñada para evaluar el rendimiento, la eficiencia de memoria y la robustez de los algoritmos de rutas más cortas en diferentes escalas, desde grafos académicos hasta procesamiento masivo de datos (stress test).

![UI Preview](Manual/img/imagen2.png)

## 🚀 Características principales

- **Motor híbrido de alto rendimiento:** integración con `SciPy` (C++) para grafos masivos y lógica manual optimizada para auditoría pedagógica.
- **Modo stress:** capacidad de procesar hasta **10 millones de nodos** con gestión eficiente de memoria RAM.
- **Inyectores dinámicos:** herramientas para insertar pesos negativos y ciclos de costo infinito para probar la resiliencia de los algoritmos.
- **Visualización interactiva:** renderizado de grafos y tablas de adyacencia para análisis de pequeña escala (micro).
- **Reportes formales:** generación automática de evidencia técnica en formato PDF con métricas de tiempo (ms) y memoria (RSS).

## 🛠️ Requisitos técnicos

- **Python 3.10+**
- Dependencias principales:
  - `customtkinter`: interfaz moderna con estética Apple-style.
  - `scipy` & `numpy`: motores de cálculo matricial.
  - `matplotlib`: visualización de velocímetros y gráficas de consumo.
  - `Pillow`: gestión de activos visuales.
  - `reportlab`: motor de exportación PDF.

## 📦 Estructura del proyecto

```text
├── Manual/              # Manual de usuario con sus capturas y explicaciones
├── assets/              # Iconos del software
├── algoritmos.py        # Fachada y lógica de despacho de algoritmos
├── bellman_ford.py      # Optimización SPFA (Shortest Path Faster Algorithm)
├── benchmark.py         # Lógica de medición de tiempo y memoria (aislamiento)
├── crop_icons.py        # Importación de íconos
├── dijkstra.py          # Implementación híbrida de Dijkstra
├── exportador.py        # Generación de reportes PDF
├── generador.py         # Generación de grafos estocásticos y conectividad
└── ui.py                # Punto de entrada principal (GUI) 
```

## ⚙️ Instalación y uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/20pedro01/Sistema-de-benchmarking-de-grafos.git
   cd Sistema-de-benchmarking-de-grafos
   ```

2. **Instalar dependencias:**
   ```bash
   pip install customtkinter scipy numpy matplotlib Pillow reportlab
   ```

3. **Ejecutar la plataforma:**
   ```bash
   python ui.py
   ```

## 🧠 Algoritmos comparados

| Algoritmo | Enfoque | Fortaleza | Ideal para |
| :--- | :--- | :--- | :--- |
| **Dijkstra** | Greedy (voraz) | Velocidad extrema ($O(E + V \log V)$) | Redes de transporte, GPS |
| **Bellman-Ford (SPFA)** | Prog. dinámica | Robustez y detección de ciclos | Finanzas, redes con subsidios |

---
**Desarrollado para la asignatura de Lenguajes y Autómatas II - Unidad 3: Optimización.**
