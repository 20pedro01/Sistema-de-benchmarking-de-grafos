# Investigación: Análisis y Comparativa de Algoritmos de Rutas Más Cortas

## 1. Introducción
La optimización de rutas es un problema fundamental en las ciencias de la computación y la teoría de grafos, con aplicaciones que van desde el enrutamiento de redes de telecomunicaciones hasta la navegación por GPS. El objetivo de esta investigación es establecer las bases teóricas para realizar un análisis comparativo de rendimiento (benchmarking) entre dos de los algoritmos más prominentes para la búsqueda de la ruta más corta: el algoritmo de Dijkstra y el algoritmo de Bellman-Ford. Este análisis no solo se centrará en su corrección matemática, sino en su eficiencia práctica evaluando el tiempo de ejecución y el consumo de memoria en entornos controlados mediante el lenguaje de programación Python.

## 2. Marco Teórico

### 2.1 Concepto de Benchmarking de Software
El *benchmarking* de software es el proceso sistemático de medir el rendimiento de una aplicación, componente o algoritmo bajo condiciones específicas. Su propósito es cuantificar métricas objetivas (como velocidad, uso de recursos, latencia o rendimiento general) para comparar diferentes implementaciones o evaluar si un sistema cumple con ciertos estándares de calidad. En el contexto de los algoritmos, el benchmarking empírico complementa el análisis teórico (notación Big-O), revelando cómo factores del mundo real como el hardware, la gestión de memoria y el intérprete del lenguaje afectan la ejecución.

### 2.2 Importancia de Medir Tiempo y Memoria
Para evaluar la eficiencia de un algoritmo, dos recursos computacionales son críticos:
*   **Tiempo de ejecución (CPU):** Determina qué tan rápido un algoritmo produce una solución a medida que crece el tamaño de la entrada. Un algoritmo ineficiente en tiempo puede volver inviable un sistema en tiempo real.
*   **Uso de memoria (RAM):** Indica la cantidad de espacio necesario para mantener las estructuras de datos durante la ejecución. Un uso excesivo de memoria puede provocar agotamiento de recursos (*Out of Memory*), paginación o degradación severa del rendimiento del sistema.

## 3. Descripción de Algoritmos

### 3.1 Algoritmo de Dijkstra
Concebido por Edsger W. Dijkstra en 1956, es un algoritmo voraz (*greedy*) que encuentra el camino más corto desde un nodo origen hacia todos los demás nodos en un grafo ponderado. Funciona explorando siempre el nodo no visitado con la distancia acumulada más corta, actualizando las distancias de sus vecinos iterativamente.

*   **Restricción principal:** Requiere que todas las aristas tengan pesos no negativos.
*   **Por qué falla con pesos negativos:** Imagina que vas en un viaje por carretera y siempre tomas el desvío que parece más corto en ese momento (enfoque voraz). Dijkstra asume que añadir más tramos a un viaje siempre aumentará la distancia o costo total. Si de repente hay un tramo que "te devuelve tiempo" (un peso negativo), Dijkstra no lo considerará correctamente porque ya habrá marcado las rutas anteriores como definitivas e inamovibles.
*   **Complejidad Computacional Teórica:**
    *   **Tiempo:** $O((V + E) \log V)$ utilizando una cola de prioridad (Min-Heap), donde $V$ son los vértices y $E$ las aristas.
    *   **Memoria (Espacio):** $O(V)$ para almacenar las distancias, predecesores y la cola de prioridad.

### 3.2 Algoritmo de Bellman-Ford
Propuesto independientemente por Richard Bellman y Lester Ford Jr., este algoritmo se basa en el principio de la programación dinámica. En lugar de seleccionar codiciosamente el nodo más cercano, relaja (actualiza) todas las aristas del grafo $V-1$ veces.

*   **Ventaja principal:** Es capaz de manejar grafos con aristas de peso negativo y detectar ciclos de peso negativo.

**Pesos Negativos (Analogía del Mundo Real):** 
Piensa en los pesos negativos como un trayecto de transporte donde, por alguna razón, se genera una "ganancia" que reduce tu costo acumulado. Por ejemplo, un vehículo eléctrico que recarga su batería al descender por una colina empinada, o un tramo de ruta comercial donde recibes un subsidio económico. Ese trayecto representa una reducción neta en el costo total de tu viaje.

**El Problema de los Ciclos Negativos:**
Un ciclo negativo ocurre cuando puedes dar una vuelta en círculo (volver al mismo punto de partida) y el balance final es a tu favor (ganas más de lo que gastas).
*   **¿Por qué no existe una ruta más corta?:** Si existe un ciclo negativo en tu camino, podrías dar vueltas en ese círculo infinitamente. Cada vuelta reduciría tu costo total más y más, tendiendo hacia el infinito negativo. Al no haber un límite o un costo mínimo final, matemáticamente es imposible definir un "camino más corto".
*   **¿Cómo los detecta Bellman-Ford?:** Tras relajar todas las aristas $V-1$ veces (el número máximo de aristas que puede tener un camino simple válido), el algoritmo realiza una inspección adicional. Si en esta última revisión aún encuentra que puede mejorar el costo de alguna ruta, significa que inevitablemente ha encontrado un ciclo negativo.
*   **¿Por qué Dijkstra falla en estos casos?:** Al ser un algoritmo voraz, Dijkstra asume que una vez evaluado un nodo, su ruta óptima ya fue encontrada. Si se topa con un ciclo negativo, se quedaría atrapado infinitamente en el bucle intentando actualizar valores, o simplemente lo ignoraría al marcar los nodos como "visitados", entregando un resultado completamente erróneo.

*   **Complejidad Computacional Teórica:**
    *   **Tiempo:** $O(V \times E)$, lo que lo hace considerablemente más lento que Dijkstra en grafos densos.
    *   **Memoria (Espacio):** $O(V)$ para almacenar distancias y predecesores.

### 3.3 Diferencias Clave
| Característica | Dijkstra | Bellman-Ford |
| :--- | :--- | :--- |
| **Enfoque** | Algoritmo Voraz (*Greedy*) | Programación Dinámica |
| **Pesos Negativos** | No soportados (falla silenciosamente) | Soportados |
| **Detección de Ciclos Negativos** | No aplicable (falla o se atrapa) | Sí, mediante una pasada adicional |
| **Rendimiento General** | Muy rápido, ideal para la mayoría de casos | Más lento, usado solo si es necesario |
| **Sensibilidad a Densidad** | Muy eficiente en grafos dispersos | Se degrada rápidamente en grafos densos |

### 3.4 Casos de Uso Reales
*   **Dijkstra:** Sistemas de navegación GPS (Google Maps, Waze), enrutamiento en redes IP utilizando el protocolo OSPF (*Open Shortest Path First*), y en videojuegos para el movimiento de la inteligencia artificial.
*   **Bellman-Ford:** Protocolos de enrutamiento por vector de distancias como RIP (*Routing Information Protocol*), donde los nodos solo conocen a sus vecinos directos y no la topología completa de la red, y en algoritmos financieros para arbitraje de divisas (donde los ciclos negativos representan ganancias garantizadas al cambiar monedas).

## 4. Interpretación Visual de los Resultados

Para facilitar la comprensión del comportamiento algorítmico y sus anomalías, el software contará con una interfaz gráfica donde los grafos se representarán visualmente. Los conceptos matemáticos abstractos se traducirán en un esquema de colores e indicadores gráficos claros:

*   **Nodos y Rutas Óptimas (Verde Suave - Éxito):** Representan los vértices estándar y las aristas normales. Las rutas óptimas descubiertas y confirmadas por el algoritmo se resaltarán con trazos más gruesos o tonos de verde indicando el camino a seguir, asociado al concepto de una operación exitosa.
*   **Nodos en Ciclos Negativos (Rojo Suave - Error):** Aquellos vértices que forman parte directa de un bucle de ganancia infinita se marcarán en rojo suave. Esto indicará al usuario exactamente el epicentro del problema o anomalía en la red topológica.
*   **Nodos Afectados por Ciclos Negativos (Color Naranja):** Cualquier nodo que, aunque no pertenezca al ciclo directamente, sea accesible desde él, tendrá su ruta corrompida (pues su distancia también tenderá a menos infinito). Estos nodos se visualizarán en color naranja para ilustrar cómo el "efecto dominó" del ciclo negativo contamina otras rutas del grafo.

Esta representación visual permitirá al usuario diferenciar de inmediato entre un grafo saludable con rutas válidas (tonos verdes) y una red problemática donde los cálculos matemáticos pierden validez (alertas rojas y naranjas).

## 5. Metodología de Medición

Para la fase de implementación y pruebas en Python, se emplearán las siguientes bibliotecas estándar orientadas al análisis de rendimiento:

### 5.1 Herramientas en Python
*   **`timeit`**: Módulo diseñado para medir el tiempo de ejecución de pequeños fragmentos de código de manera precisa. Evita problemas comunes de temporización ejecutando el código múltiples veces e inhabilitando temporalmente el recolector de basura (*Garbage Collector*) para reducir fluctuaciones.
*   **`tracemalloc`**: Herramienta integrada en Python que permite rastrear la asignación de memoria. Es ideal para perfilar el consumo máximo de memoria (pico de RAM) de un bloque de código y detectar posibles fugas (*memory leaks*), brindando una visión detallada de los bloques de memoria asignados.

### 5.2 Buenas Prácticas al Medir Rendimiento
Para asegurar que los resultados del benchmarking sean estadísticamente significativos y reproducibles, se deben seguir estas pautas:
1.  **Aislamiento del Entorno:** Cerrar aplicaciones innecesarias durante las pruebas para evitar que procesos en segundo plano consuman CPU o memoria.
2.  **Múltiples Iteraciones:** Ejecutar cada algoritmo repetidas veces (ej. 100 o 1000 iteraciones) y tomar promedios o la mediana, descartando valores atípicos (anomalías causadas por el sistema operativo).
3.  **Fase de Calentamiento (*Warm-up*):** Realizar ejecuciones previas que no se miden para asegurar que el intérprete, cachés de CPU y bibliotecas estén inicializados.
4.  **Desactivación del Recolector de Basura (GC):** Al medir tiempos exactos con `timeit`, deshabilitar el GC evita picos de procesamiento impredecibles en medio del algoritmo.
5.  **Variación Controlada de Entradas:** Probar con grafos de distintos tamaños y densidades (grafos pequeños, grandes, dispersos y densos) para observar la curva de complejidad asintótica empírica.

## 6. Conclusiones Preliminares
Basado en la literatura académica y el análisis asintótico, se espera que en la fase experimental empírica el algoritmo de **Dijkstra muestre una superioridad significativa en términos de tiempo de ejecución**, particularmente a medida que aumente la escala y densidad del grafo. Sin embargo, en cuanto al consumo de memoria, ambos algoritmos deberían mostrar un comportamiento similar (crecimiento lineal respecto a los nodos), dada su complejidad espacial $O(V)$. La implementación en Python confirmará cómo estas teorías se traducen en la práctica bajo el intérprete CPython.

## 7. Aplicación al Proyecto

La investigación presentada servirá como base para el desarrollo de un software de benchmarking en Python, el cual permitirá comparar empíricamente los algoritmos Dijkstra y Bellman-Ford.

El sistema generará grafos de distintos tamaños y aplicará ambos algoritmos bajo condiciones controladas, midiendo:

- Tiempo de ejecución mediante el módulo timeit
- Uso de memoria mediante tracemalloc

Los resultados serán utilizados para validar experimentalmente las diferencias teóricas descritas previamente, así como para identificar comportamientos no evidentes en el análisis asintótico.

Además, se espera observar que la diferencia de rendimiento entre ambos algoritmos se amplifica conforme aumenta el tamaño del grafo, lo cual permitirá evidenciar el impacto real de sus complejidades computacionales en escenarios prácticos.

Esto es especialmente relevante en sistemas reales donde el tiempo de respuesta es crítico, como en redes o sistemas de navegación.

## 8. Arquitectura del Sistema

Para garantizar un benchmarking riguroso y una experiencia de usuario fluida, el software se diseñará bajo el principio de **separación de responsabilidades**. La arquitectura se dividirá en tres componentes principales:

*   **Implementación de Algoritmos:** Este núcleo matemático contendrá el código puro de Dijkstra y Bellman-Ford. Su única responsabilidad es recibir un grafo estructurado en memoria y devolver las distancias mínimas y los predecesores, sin interactuar con ninguna otra parte del sistema.
*   **Módulo de Benchmarking:** Será el encargado de orquestar las pruebas. Su función es instanciar los algoritmos, envolverlos en los medidores de rendimiento (`timeit` y `tracemalloc`), registrar las métricas exactas en milisegundos y bytes, y devolver los datos en crudo.
*   **Interfaz de Usuario (UI):** Responsable exclusiva de la interacción visual, la captura de parámetros de entrada (como la cantidad de vértices), el renderizado visual de la red y la presentación gráfica de los resultados mediante tablas o *charts*.

**Flujo de ejecución:** 
1. El usuario configura los parámetros en la UI.
2. La UI solicita la generación de los datos.
3. El Módulo de Benchmarking aísla el entorno y ejecuta la implementación del algoritmo puro.
4. Se devuelven los tiempos, el uso de memoria y las rutas calculadas hacia la UI.
5. La UI, finalmente, renderiza el grafo coloreado (aplicando las reglas de nodos azules, rojos y naranjas) y despliega las estadísticas.

## 9. Aislamiento de Mediciones

Para que los resultados empíricos sean científicamente válidos e irrefutables, es absolutamente indispensable que el módulo de benchmarking actúe en total aislamiento.

**¿Por qué excluir la UI de la medición?**
El renderizado gráfico, la actualización de la ventana en pantalla, las animaciones y la gestión de eventos de interacción del usuario consumen una cantidad monumental de recursos (CPU y RAM) y tiempo en comparación con el cálculo puro de rutas lógicas en memoria. Si las rutinas de visualización se incluyeran dentro del temporizador, se estaría midiendo la velocidad de la tarjeta gráfica y el sobrecosto de las bibliotecas de dibujo, distorsionando y enmascarando por completo el rendimiento real del algoritmo ($O(V+E\log V)$ vs $O(VE)$).

**Ejemplos Conceptuales:**
*   ✅ **QUÉ SÍ SE DEBE MEDIR:** Exclusivamente el tiempo que tarda la función pura `dijkstra(grafo, origen)` desde que inicia la primera iteración hasta que retorna el arreglo definitivo de rutas. Igualmente, medir solo la memoria que ocupan las colas de prioridad y diccionarios internos durante ese procesamiento del CPU.
*   ❌ **QUÉ NO SE DEBE MEDIR:** El tiempo que toma procesar y dibujar un nodo azul en pantalla; los milisegundos que transcurren desde que el usuario da clic en el botón "Ejecutar"; o la gran cantidad de memoria RAM asignada para las ventanas, colores y tipografías del sistema operativo.

**Buenas Prácticas Aplicadas:**
*   **Evitar Interferencias:** El código algorítmico puro jamás debe incluir sentencias `print()` a consola o llamadas a funciones de actualización de gráficos durante su bucle `while/for` principal, ya que el I/O es increíblemente lento y arruinaría la precisión del *benchmark*.
*   **Reproducibilidad Estricta:** Aislar estas capas arquitectónicas garantiza que si el mismo sistema de benchmarking se corre en un servidor (sin monitor ni interfaz visual), los tiempos de ejecución asintóticos sigan mostrando la misma proporción empírica.

## 10. Diseño de la Interfaz de Usuario

Para asegurar que el software sea accesible y cumpla cabalmente con sus objetivos didácticos y de investigación, se diseñará una Interfaz de Usuario (UI) enfocada en la claridad y la ergonomía visual.

### 10.1 Enfoque Minimalista y Estética Visual
La interfaz adoptará un **diseño minimalista** empleando una paleta de **colores pastel** y controles con **bordes redondeados**. 
*   **Mejora de la Experiencia del Usuario (UX):** Un entorno limpio y libre de elementos distractores previene la sobrecarga cognitiva. Los tonos pastel reducen la fatiga visual, lo cual es fundamental cuando se analiza información densa y compleja (como grafos de cientos de nodos). Asimismo, los bordes redondeados suavizan la interfaz, transmitiendo una sensación de modernidad, amigabilidad e intuición.

### 10.2 Estructura y Componentes de la Interfaz
La pantalla principal se dividirá de forma lógica en tres secciones interconectadas:
1.  **Panel de Configuración:** Un menú lateral de controles claros donde el usuario podrá seleccionar qué algoritmo evaluar, ajustar el tamaño y densidad del grafo, e inducir deliberadamente pesos o ciclos negativos.
2.  **Panel de Visualización del Grafo:** El lienzo central que servirá para renderizar interactivamente la topología de la red computada, actualizándose según los parámetros elegidos.
3.  **Panel de Resultados:** El área analítica del sistema. Aquí se presentarán las métricas recolectadas empleando componentes gráficos inmersivos. Destacará el uso de **visualizaciones tipo velocímetro (indicadores radiales)**, diseñadas específicamente para ilustrar el tiempo de ejecución de manera casi instantánea, facilitando una comparación visual y visceral del rendimiento entre Dijkstra y Bellman-Ford.

### 10.3 Semántica de Colores Integrada
En plena coherencia con la sección de *Interpretación Visual*, la interfaz mapeará los comportamientos abstractos a un esquema cromático universal en el lienzo de dibujo y la UI en general:
*   **UI Estructural:** Fondo gris claro o blanco roto para descansar la vista, utilizando Morado Pastel como color Primario (botones, menús) y Azul Pastel como Secundario.
*   **Nodos Normales (Verde Suave - Éxito):** Señalizarán caminos viables, estables y matemáticamente óptimos.
*   **Nodos en Ciclos Negativos (Rojo Suave - Error):** Actuarán como una alarma visual, señalando los puntos exactos donde el grafo presenta un bucle de costo infinito.
*   **Nodos Afectados (Naranja):** Indicarán qué vértices inocentes se han visto corrompidos o "infectados" por la presencia del ciclo negativo adyacente.
*   **Velocímetros Analíticos:** El cuerpo gráfico será rosa pastel para destacarse estéticamente, mientras que sus textos internos y agujas usarán verde suave (para métricas eficientes) o rojo suave (para tiempos lentos), logrando una lectura instintiva de éxito o error.

### 10.4 Justificación de las Decisiones de Diseño
*   **Claridad Visual:** La estricta separación espacial (configuración vs. gráfica vs. resultados) guía naturalmente el ojo del usuario a través del flujo de trabajo sin causar confusión.
*   **Interpretación Rápida de Resultados:** Elementos analógicos como el "velocímetro" permiten que, incluso sin un entendimiento profundo de la notación asintótica (Big-O), cualquier observador asimile rápidamente qué algoritmo fue más eficiente.
*   **Facilidad de Uso:** Al transformar un proceso algorítmico complejo en una experiencia de "configurar parámetros y observar medidores visuales", se prioriza el valor académico y didáctico del proyecto, garantizando que el usuario comprenda el comportamiento del sistema de un solo vistazo.

## 11. Limitaciones del Estudio

Es importante considerar que los resultados del benchmarking pueden verse influenciados por factores externos como el hardware, el sistema operativo y la implementación específica en Python.

Por lo tanto, los resultados obtenidos representan una aproximación empírica y no deben interpretarse como valores absolutos universales.

## 12. Hipótesis de Resultados

| Escenario | Algoritmo esperado más eficiente |
|----------|-------------------------------|
| Grafos grandes sin pesos negativos | Dijkstra |
| Grafos con pesos negativos | Bellman-Ford |
| Grafos densos | Dijkstra |
| Grafos con ciclos negativos | Bellman-Ford (detección) |
