# Plan de Implementación: Benchmarking de Dijkstra y Bellman-Ford

A continuación, se detalla el plan para estructurar y construir el proyecto de manera ordenada, modular y escalable, con un fuerte enfoque en la Experiencia de Usuario (UX) y el diseño interactivo.

---

## 1. Fases del Desarrollo
*   **Fase 1: Planeación y Diseño:** Definición de arquitectura, selección de librerías, estructuración del proyecto y diseño del flujo UX.
*   **Fase 2: Implementación Matemática:** Desarrollo del núcleo algorítmico puro y del generador de grafos topológicos.
*   **Fase 3: Construcción del Módulo de Benchmarking:** Creación de los *scripts* de envoltura para garantizar el aislamiento y la precisión de la medición.
*   **Fase 4: Desarrollo de la Interfaz Gráfica (UI):** Construcción del *layout* minimalista, paneles de control, máquina de estados y lienzo central.
*   **Fase 5: Integración y Renderizado:** Conexión de la lógica (*backend*) con la interfaz (*frontend*), aplicando la semántica de colores y generación de PDF.
*   **Fase 6: Pruebas y Validación de Resultados:** Análisis empírico final, corrección de errores (*debugging*) y generación de métricas definitivas.

## 2. Desglose de Módulos del Sistema
El sistema seguirá un enfoque estricto de separación de responsabilidades:
*   **Módulo de Algoritmos:** Contendrá exclusivamente la lógica matemática de Dijkstra y Bellman-Ford.
*   **Módulo Generador de Grafos:** Capaz de crear grafos aleatorios (densos/dispersos) e inyectar premeditadamente pesos y ciclos negativos.
*   **Módulo de Benchmarking:** Envoltorio o *wrapper* que utiliza `timeit` y `tracemalloc` para ejecutar los algoritmos y abstraer las estadísticas en completo aislamiento.
*   **Módulo UI (Configuración e Interacción):** Ventana y menú lateral interactivo que gestiona los estados de la aplicación (Editable, Bloqueado, Ejecución).
*   **Módulo Visualizador de Resultados:** El lienzo gráfico central y la sección analítica que muestra medidores visuales (tipo velocímetro).
*   **Módulo de Exportación (NUEVO):** Encargado de formatear y compilar la topología del grafo, los resultados numéricos y los anexos gráficos en un reporte PDF listo para entrega académica, además de generar un archivo JSON con los datos crudos.

## 3. Tareas Específicas por Módulo

### 3.1 Módulo de Algoritmos
*   **Tarea 1:** Definir la estructura de datos interna del grafo (diccionario de adyacencia recomendado).
*   **Tarea 2:** Programar Dijkstra utilizando una cola de prioridad (`heapq`). Esta función requerirá un parámetro explícito para el **nodo origen** (*source*).
*   **Tarea 3:** Programar Bellman-Ford con su mecanismo de relajación $V-1$ veces y la pasada adicional de detección de ciclos (partiendo igualmente de un nodo origen definido).
*   *Dependencias:* Ninguna (debe ser el primer módulo programado).

### 3.2 Generador de Grafos
*   **Tarea 1:** Programar función para instanciar grafos aleatorios basados en la cantidad de vértices ($V$) y densidad deseada.
*   **Tarea 2:** Programar funciones inyectoras para forzar rutas anómalas (pesos/ciclos negativos).
*   *Dependencias:* Requiere que la estructura de datos en Algoritmos esté finalizada.

### 3.3 Módulo de Benchmarking
*   **Tarea 1:** Crear funciones aisladas que apaguen el *Garbage Collector*, inicien `timeit`/`tracemalloc`, ejecuten el algoritmo objetivo y registren las métricas.
*   **Tarea 2:** Implementar estrategia de promedio. Cada algoritmo se ejecutará múltiples veces ($n$ iteraciones) y se reportará el tiempo promedio aritmético para minimizar el ruido del procesador.
*   *Dependencias:* Módulo de Algoritmos y Módulo Generador.

### 3.4 Interfaz Gráfica (UI) y Control UX
*   **Tarea 1:** Diseñar la cuadrícula de la ventana (*layout*) reservando espacio para Configuración, Grafo y Resultados.
*   **Tarea 2:** Implementar el controlador de estados (Editable $\rightarrow$ Bloqueado $\rightarrow$ Ejecución).
*   **Tarea 3:** Programar el lienzo interactivo permitiendo visualización previa y edición manual de nodos/aristas en estado "Editable".
*   **Tarea 4:** Programar la ventana modal de confirmación (advertencia requerida para pasar de estado "Bloqueado" de vuelta a "Editable").
*   *Dependencias:* Totalmente dependiente de que el *backend* devuelva datos limpios y estructurados.

### 3.5 Visualización, Exportación PDF y JSON
*   **Tarea 1:** Renderizar el lienzo. La UI incluirá un selector explícito para que el usuario decida el **nodo origen**. Si el usuario no elige uno, se usará selección automática documentada (ej. Nodo 0) avisando en pantalla.
*   **Tarea 2:** Integrar velocímetros analíticos. Se programará una **escala dinámica**: el tiempo máximo medido en la comparativa definirá el tope del medidor, logrando que el más lento se acerque a la zona de error (roja) y el rápido a la de eficiencia (verde).
*   **Tarea 3:** Generación de archivos de resultados:
    *   **PDF:** Incluirá una descripción textual detallada del grafo en formato de *lista de adyacencia*, la tabla de benchmarking y los grafos renderizados como anexos gráficos en páginas separadas (*landscape*).
    *   **JSON:** Guardar el volcado crudo (topología, rutas, tiempos y memoria) para garantizar la reproducibilidad y permitir un análisis técnico posterior.
*   *Dependencias:* Módulo de UI y Benchmarking.

## 4. Tecnologías a Utilizar
*   **Lenguaje Base:** Python 3.x
*   **Benchmarking y Memoria:** `timeit` y `tracemalloc`.
*   **Interfaz Gráfica (UI):** `CustomTkinter` (Ideal para diseño minimalista, botones redondeados y manejo de colores pastel y ventanas modales).
*   **Lógica y Dibujado de Grafos:** `NetworkX` acoplado a `Matplotlib` (para renderizar nodos, bordes y velocímetros).
*   **Generación de PDF:** `ReportLab` o `FPDF` para estructurar texto, tablas e imágenes horizontales programáticamente.

## 5. Estrategia de Pruebas
*   **Validación Unitaria Matemática:** Probar algoritmos con grafos pre-calculados a mano para verificar precisión.
*   **Prueba de Detección de Ciclos:** Validar que Bellman-Ford identifique ciclos negativos correctamente.
*   **Validación de Medición Aislada:** Ejecutar una prueba con el lienzo desactivado asegurando que la UI no sume sobrecarga al contador de `timeit`.
*   **Pruebas de Flujo UX:** Comprobar que es imposible iniciar el benchmarking si el estado no está "Bloqueado", garantizando que el usuario confirmó la topología.

## 6. Consideraciones Críticas de Diseño

### 6.1 Diseño Visual y Paleta de Colores
La UI implementará una **paleta de colores** elegida minuciosamente para reducir la carga cognitiva, evitar fatiga visual ante datos densos y mantener un tono académico y moderno:
*   **Fondo del Sistema:** Gris claro o blanco roto, proporcionando contraste alto sin el brillo molesto del blanco puro.
*   **Color Primario:** Morado pastel, perfecto para botones principales, bordes y el área central de configuración.
*   **Color Secundario:** Azul pastel para acentos visuales interactivos y paneles de apoyo.
*   **Semántica de Estados (Lienzo y Textos):** 
    *   *Éxito (Nodos normales y textos de métricas rápidas):* Verde suave (indica rutas matemáticas óptimas y tiempos eficientes).
    *   *Error / Ciclos Negativos:* Rojo suave (textos de lentitud o alarma ante un bucle infinito).
    *   *Afectados:* Naranja o durazno (indica corrupción en cadena en el grafo).
*   **Velocímetros de Resultados:** La estructura principal o cuerpo del velocímetro se presentará en **rosa pastel**, sirviendo como un elemento que resalte el área analítica. Sin embargo, los textos dinámicos internos utilizarán la semántica de éxito (verde suave) o error (rojo suave) para comunicar la eficiencia del algoritmo.

### 6.2 Flujo de Interacción (UX) y Control de Estados
Para evitar interferencias y errores de usuario, el lienzo interactivo estará gobernado por tres estados estrictos:
1.  **Estado Editable:** Es la fase inicial. El usuario visualiza la pre-generación del grafo y puede hacer ediciones libres (modificar pesos o alterar la topología). Las herramientas de dibujo están habilitadas.
2.  **Estado Bloqueado:** Una vez que el usuario termina de pre-visualizar y editar, presiona "Confirmar Grafo". El lienzo se bloquea y se vuelve inmutable. Si el usuario cambia de opinión y desea editar nuevamente, debe presionar "Modificar Grafo", lo que invocará una **ventana modal (pop-up)** de advertencia para evitar reinicios accidentales.
3.  **Estado de Ejecución:** Ocurre al lanzar el benchmarking. La interfaz deshabilita cualquier interacción temporalmente. Tras bastidores, el cálculo se hace en aislamiento. Finalmente, retorna al Estado Bloqueado desplegando los resultados en los velocímetros y habilitando el botón de exportación PDF.

### 6.3 Arquitectura y Reproducibilidad
*   **Separación Estricta y Aislamiento:** La máquina de estados garantiza que el módulo de matemáticas jamás empiece a calcular mientras la interfaz de dibujo esté activa, asegurando tiempos de $O(V+E\log V)$ puros.
*   **Reproducibilidad Estocástica:** Todo grafo generado utilizará "Semillas Aleatorias". La exportación PDF/JSON incluirá esta semilla para que los resultados puedan auditarse y recrearse con exactitud.

### 6.4 Manejo de errores y validaciones
Para garantizar la solidez del sistema frente a anomalías:
*   **Validación de grafos vacíos:** Si el lienzo no tiene vértices, se bloqueará la ejecución mostrando un aviso amigable.
*   **Manejo de grafos no conexos:** Los algoritmos deben tolerar y reportar como "Inalcanzable" o "$\infty$" los vértices que estén aislados del nodo origen sin romper la ejecución.
*   **Mensajes claros por ciclos negativos:** Al detectarse un bucle infinito en Bellman-Ford, la interfaz pausará el análisis numérico y mostrará una alerta contundente notificando que "la ruta más corta no existe debido a un ciclo negativo", coloreando los nodos involucrados.

## 7. Cronograma sugerido (enfoque Ágil - 5 Días)
*   **Día 1:** Estructuras de datos, algoritmos puros y pruebas de escritorio.
*   **Día 2:** Generador de grafos y módulo de benchmarking.
*   **Día 3:** Levantamiento de interfaz visual (paleta pastel), máquina de estados UX y controles.
*   **Día 4:** Renderizado semántico del grafo y ventana modal de bloqueos.
*   **Día 5:** Integración de velocímetros rosa pastel, Exportación a PDF (formato *landscape*) y validación final.

## 8. Entregables por fase
1.  **Backend.py:** Script de algoritmos.
2.  **Benchmark.py:** Recolección de datos.
3.  **UI.py:** Archivo maestro de interfaz gráfica interactiva.
4.  **Exportador.py:** Módulo de reporte PDF.
5.  **Reporte.pdf:** Entregable final generado automáticamente por el software, demostrando gráficamente y numéricamente las diferencias empíricas de los algoritmos.
