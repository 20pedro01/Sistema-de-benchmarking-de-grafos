import customtkinter as ctk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")

from generador import generar_grafo, inyectar_peso_negativo, inyectar_ciclo_negativo, sanitizar_pesos
from benchmark import ejecutar_en_proceso_separado
from exportador import exportar_pdf, exportar_json
import random
import os
import multiprocessing
import numpy as np
from PIL import Image
import markdown
import webbrowser

# ==========================================
# PALETA DE COLORES Y TIPOGRAFÍA (Apple Style)
# ==========================================
BG_COLOR = "#FCE4EC"  # Rosa pastel muy suave
PRIMARY_COLOR = "#B39DDB" # Morado pastel
SECONDARY_COLOR = "#90CAF9" # Azul pastel
SUCCESS_COLOR = "#A5D6A7"  # Verde suave (Éxito)
ERROR_COLOR = "#EF9A9A"    # Rojo suave (Error)
AFFECTED_COLOR = "#FFF59D" # Amarillo pastel
HINT_COLOR = "#78909C"     # Gris azulado pastel para pistas
SPEEDOMETER_BG = "#FFFFFF" # Fondo de tarjeta limpio
CARD_BG = "#FFFFFF"

# Fuentes Estándar para Uniformidad
MAIN_FONT = "Outfit"
FONT_TITLE = (MAIN_FONT, 16, "bold")
FONT_RESULT = (MAIN_FONT, 15, "bold")
FONT_LABEL = (MAIN_FONT, 13, "bold")
FONT_DETAIL = (MAIN_FONT, 11)

class BenchmarkingUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Plataforma de benchmarking: Dijkstra versus Bellman-Ford")
        self.geometry("1100x950")
        self.configure(fg_color=BG_COLOR)
        
        # Estados
        self.estado_actual = "EDITABLE"
        self.grafo = {}
        self.filas_tabla = [] 
        self.resultados_actuales = None
        self.seed = 42
        self.inyecciones = {"negativos": 0, "ciclos": 0}

        # Cargar íconos desde assets/icons (sustituyen emojis, mismo tamaño)
        _icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")
        def _ico(name, size=20):
            return ctk.CTkImage(Image.open(os.path.join(_icons_dir, name)), size=(size, size))
        self.ico_dice     = _ico("dice.png")
        self.ico_timer    = _ico("timer.png")
        self.ico_trash    = _ico("trash.png")
        self.ico_check    = _ico("check.png")
        self.ico_rocket   = _ico("rocket.png")
        self.ico_pencil   = _ico("pencil.png")
        self.ico_negative = _ico("negative.png")
        self.ico_loop     = _ico("loop.png")
        self.ico_refresh  = _ico("refresh.png")
        self.ico_pdf      = _ico("pdf.png")
        # Íconos para títulos y tarjetas de bienvenida
        self.ico_rocket_big  = _ico("rocket.png", 26)
        self.ico_chart_bar   = _ico("chart_bar.png", 32)
        self.ico_bolt        = _ico("bolt.png", 32)
        self.ico_link        = _ico("link.png", 32)
        self.ico_flask       = _ico("flask.png", 32)
        self.ico_settings    = _ico("settings.png", 22)
        self.ico_chart_line  = _ico("chart_line.png", 18)
        self.ico_trophy      = _ico("trophy.png", 20)

        self.setup_ui()

    def setup_ui(self):
        # Figuras de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.fig_gauge = plt.Figure(figsize=(5, 1.6), dpi=100, facecolor=SPEEDOMETER_BG) 
        self.ax_d_gauge = self.fig_gauge.add_subplot(121, polar=True)
        self.ax_b_gauge = self.fig_gauge.add_subplot(122, polar=True)

        self.fig_mem = plt.Figure(figsize=(3, 1.2), dpi=100, facecolor="white") # Más altura para evitar compactación
        self.ax_mem = self.fig_mem.add_subplot(111)

        self.fig_cost = plt.Figure(figsize=(5, 0.9), dpi=100, facecolor="#F8F9FA")
        self.ax_cost = self.fig_cost.add_subplot(111)

        # Registro de Validadores
        self.v_int = (self.register(self.validate_int), "%P")
        self.v_float = (self.register(self.validate_float), "%P")

        # Proceso de benchmark
        self.p = None
        self.q = None
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.configurar_layout()

    def configurar_layout(self):
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        
        self.header = ctk.CTkFrame(self.main_container, fg_color=PRIMARY_COLOR, height=80, corner_radius=0)
        self.header.pack(fill="x", side="top")
        ctk.CTkLabel(self.header, text="Dijkstra versus Bellman-Ford", 
                     font=("Outfit", 28, "bold"), text_color="black").pack(pady=20)
        
        # --- DASHBOARD DE BIENVENIDA ---
        self.panel_bienvenida = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=20, border_width=1, border_color="#E0E0E0")
        self.panel_bienvenida.pack(fill="x", padx=20, pady=(15, 10))
        
        f_welcome = ctk.CTkFrame(self.panel_bienvenida, fg_color="transparent")
        f_welcome.pack(padx=30, pady=25, fill="x")
        
        ctk.CTkLabel(f_welcome, text=" Sistema de benchmarking de grafos",
                     image=self.ico_rocket_big, compound="left",
                     font=(MAIN_FONT, 26, "bold"), text_color="black").pack(anchor="center")
        ctk.CTkLabel(f_welcome, text="Plataforma de análisis comparativo de algoritmos para rutas óptimas.", 
                     font=(MAIN_FONT, 14), text_color="#546E7A").pack(anchor="center", pady=(2, 15))
        
        f_features = ctk.CTkFrame(f_welcome, fg_color="transparent")
        f_features.pack(fill="x", pady=5)
        f_features.columnconfigure((0, 1), weight=1)
        
        def create_feature_card(parent, row, col, icon, title, desc):
            card = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=15, border_width=1, border_color="#EDF2F7")
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=8)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=15, pady=12, fill="both", expand=True)
            
            ctk.CTkLabel(inner, image=icon, text="", font=(MAIN_FONT, 28)).pack(pady=(0, 5))
            ctk.CTkLabel(inner, text=title, font=(MAIN_FONT, 15, "bold"), text_color="black").pack()
            ctk.CTkLabel(inner, text=desc, font=(MAIN_FONT, 12), text_color="#64748B", justify="center", wraplength=400).pack(pady=(2, 0))

        create_feature_card(f_features, 0, 0, self.ico_chart_bar, "Visualización", "Auditoría gráfica interactiva y tablas de adyacencia para grafos pequeños.")
        create_feature_card(f_features, 0, 1, self.ico_bolt,      "Modo stress",   "Optimización de alto rendimiento para análisis masivo de hasta 10 miiilones de nodos.")
        create_feature_card(f_features, 1, 0, self.ico_link,      "Conectividad",  "Algoritmos que garantizan grafos 100% conexos.")
        create_feature_card(f_features, 1, 1, self.ico_flask,     "Inyectores",    "Pruebas de robustez mediante inserción de pesos negativos y ciclos.")

        f_footer = ctk.CTkFrame(f_welcome, fg_color="transparent")
        f_footer.pack(fill="x", pady=(15, 0))
        
        self.btn_manual = ctk.CTkButton(f_footer, text=" Descargar manual de uso",
                                        image=self.ico_pdf, compound="left",
                                        font=(MAIN_FONT, 13, "bold"),
                                        fg_color=PRIMARY_COLOR, 
                                        text_color="black", 
                                        hover_color=SECONDARY_COLOR,
                                        width=250, height=45, corner_radius=12,
                                        command=self.acc_descargar_manual)
        self.btn_manual.pack(anchor="center")

        # 1. BLOQUE: CONFIGURACIÓN
        self.panel_config = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=20)
        self.panel_config.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(self.panel_config, text=" Parámetros del grafo",
                     image=self.ico_settings, compound="left",
                     font=("Outfit", 22, "bold"), text_color="black").pack(pady=10)
        
        f_top = ctk.CTkFrame(self.panel_config, fg_color="transparent")
        f_top.pack(fill="x", padx=20, pady=(20, 0))
        f_top.grid_columnconfigure((0,1,2,3), weight=1)

        def create_modern_input(master, label, row, col, width=200, is_nodes=False, vcmd=None, placeholder=""):
            frame = ctk.CTkFrame(master, fg_color="transparent")
            frame.grid(row=row, column=col, padx=8, pady=5, sticky="ew")
            ctk.CTkLabel(frame, text=label, font=(MAIN_FONT, 12, "bold"), text_color="black").pack(pady=(0,2))
            entry = ctk.CTkEntry(frame, width=width, height=35, corner_radius=8, border_width=1, font=FONT_DETAIL, justify="center", 
                                 validate="key", validatecommand=vcmd, placeholder_text=placeholder)
            entry.pack(fill="x")
            hint = ctk.CTkLabel(frame, text="", font=(MAIN_FONT, 10), height=20)
            hint.pack(pady=(5, 5))
            if is_nodes: entry.bind("<KeyRelease>", lambda e: self.actualizar_nodos_defecto())
            return entry, frame, hint

        self.entry_nodos, self.f_nodos, self.lbl_hint_nodos = create_modern_input(f_top, "Nodos", 0, 0, is_nodes=True, vcmd=self.v_int)
        self.lbl_hint_nodos.configure(text="Intervalo: 10 a 10,000,000", text_color="#E74C3C", anchor="n")
        self.entry_nodos.bind("<FocusOut>", self.validar_rango_nodos)
        
        self.entry_densidad, self.f_densidad, self.lbl_hint_densidad = create_modern_input(f_top, "Densidad", 0, 1, vcmd=self.v_float)
        self.lbl_hint_densidad.configure(text_color="#78909C", anchor="n")
        self.entry_densidad.bind("<FocusOut>", self.validar_densidad)
        self.entry_densidad.bind("<KeyRelease>", lambda e: self.verificar_habilitacion_generar())
        
        self.entry_source, self.f_source, self.lbl_hint_source = create_modern_input(f_top, "Nodo origen", 0, 2)
        self.entry_target, self.f_target, self.lbl_hint_target = create_modern_input(f_top, "Nodo destino", 0, 3)
        self.entry_source.configure(state="readonly")
        self.entry_target.configure(state="readonly")

        self.f_nodos.grid(row=0, column=0, columnspan=4, sticky="")
        for f in [self.f_densidad, self.f_source, self.f_target]:
            f.grid_remove()

        self.f_middle = ctk.CTkFrame(self.panel_config, fg_color="#F8F9FA", corner_radius=15)
        lbl_u = ctk.CTkLabel(self.f_middle, text="U (origen)", font=FONT_DETAIL, text_color="black")
        lbl_u.grid(row=0, column=0, sticky="ew", pady=(15, 5))
        lbl_v = ctk.CTkLabel(self.f_middle, text="V (destino)", font=FONT_DETAIL, text_color="black")
        lbl_v.grid(row=0, column=1, sticky="ew", pady=(15, 5))
        lbl_p = ctk.CTkLabel(self.f_middle, text="Peso", font=FONT_DETAIL, text_color="black")
        lbl_p.grid(row=0, column=2, sticky="ew", pady=(15, 5))
        self.f_middle.grid_columnconfigure((0,1,2), weight=1)
        self.scroll_tabla = ctk.CTkScrollableFrame(self.f_middle, fg_color="transparent", height=140)
        self.scroll_tabla.grid(row=1, column=0, columnspan=3, sticky="ew", padx=0, pady=0)

        # 3. BLOQUE: ACCIONES
        self.f_actions = ctk.CTkFrame(self.panel_config, fg_color="transparent", height=90)
        self.btn_generar = ctk.CTkButton(self.f_actions, text=" Generar grafo aleatorio",
                                         image=self.ico_dice, compound="left",
                                         font=(MAIN_FONT, 14, "bold"), fg_color=PRIMARY_COLOR, 
                                         hover_color="#3F51B5", text_color="white", height=42, width=220, 
                                         corner_radius=10, command=self.acc_generar_aleatorio)
        self.f_iny = ctk.CTkFrame(self.f_actions, fg_color="transparent")
        
        def create_iny_group(master, label, color, command, btn_attr, iny_type, emoji):
            """Crea la tarjeta vertical exacta de la imagen del usuario."""
            card = ctk.CTkFrame(master, fg_color="white", corner_radius=12, border_width=1, border_color="#E0E0E0")
            card.pack(side="left", padx=15, pady=5)
            
            # 1. Entrada arriba (Placeholder en lugar de 0 insertado)
            entry = ctk.CTkEntry(card, width=120, height=35, font=(MAIN_FONT, 14), justify="center", corner_radius=8, 
                                 border_color="#CCC", placeholder_text="0",
                                 validate="key", validatecommand=(self.register(lambda P: self.validate_iny(P, iny_type)), "%P"))
            entry.pack(pady=(15, 8), padx=20)

            # 2. Botón en medio (Inicia deshabilitado hasta que haya un número > 0)
            btn = ctk.CTkButton(card, text=f" {label}",
                                image=emoji, compound="left",
                                font=(MAIN_FONT, 13, "bold"), fg_color=color, hover_color=color, 
                                text_color="black", height=40, width=180, corner_radius=10, 
                                state="disabled", command=command)
            setattr(self, btn_attr, btn)
            btn.pack(pady=5, padx=20)

            # Vincular validación en tiempo real para habilitar el botón
            def check_val(e, ent=entry, b=btn):
                v = ent.get().strip()
                if v and v.isdigit() and int(v) > 0:
                    b.configure(state="normal")
                else:
                    b.configure(state="disabled")
            entry.bind("<KeyRelease>", check_val)
            
            # 3. Dos líneas de información abajo
            lbl_l1 = ctk.CTkLabel(card, text="Máximo para este caso: 0", font=(MAIN_FONT, 10, "bold"), text_color="#555")
            lbl_l1.pack(pady=(5, 0))
            lbl_l2 = ctk.CTkLabel(card, text="(Calculando límite...)", font=(MAIN_FONT, 9, "italic"), text_color="#777")
            lbl_l2.pack(pady=(0, 15))
            
            return entry, lbl_l1, lbl_l2

        self.f_iny_tools = ctk.CTkFrame(self.f_iny, fg_color="transparent")
        self.f_iny_tools.pack(side="top", pady=5)
        self.entry_qty_neg, self.lbl_iny_neg_l1, self.lbl_iny_neg_l2 = create_iny_group(self.f_iny_tools, "Inyectar negativo", AFFECTED_COLOR, self.inyectar_negativo, "btn_iny_neg", "neg", self.ico_negative)
        self.entry_qty_ciclo, self.lbl_iny_ciclo_l1, self.lbl_iny_ciclo_l2 = create_iny_group(self.f_iny_tools, "Inyectar ciclo", ERROR_COLOR, self.inyectar_ciclo, "btn_iny_ciclo", "cic", self.ico_loop)

        self.btn_limpiar = ctk.CTkButton(self.f_actions, text=" Limpiar pesos inyectados",
                                        image=self.ico_trash, compound="left",
                                        font=(MAIN_FONT, 13), fg_color="#F5F5F5", text_color="black",
                                        border_width=1, border_color="#DDD", height=38, width=300, corner_radius=10, command=self.limpiar_pesos)
        # Se empaquetará dinámicamente en _finalizar_generacion
        
        # Etiqueta de estado para inyecciones (sustituye modales)
        self.lbl_status_iny = ctk.CTkLabel(self.f_actions, text="", font=(MAIN_FONT, 12, "bold"), text_color=SUCCESS_COLOR)
        # Se empaquetará al final en _finalizar_generacion
        
        self.f_actions.pack(fill="x", pady=5)
        self.btn_generar.pack_forget() 

        # PANEL DE VISUALIZACIÓN (REBAUTIZADO Y OCULTO)
        self.panel_visualizacion = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=15, height=1, width=1)
        self.panel_visualizacion.pack_forget()
        
        f_grafo_header = ctk.CTkFrame(self.panel_visualizacion, fg_color="transparent")
        # El encabezado se empaquetará solo cuando el panel sea visible
        ctk.CTkLabel(f_grafo_header, text=" Estructura del grafo",
                     image=self.ico_chart_line, compound="left",
                     font=FONT_TITLE, text_color="#333").pack(side="left", padx=20)
        
        # Contador permanente de inyecciones
        self.lbl_iny_total = ctk.CTkLabel(f_grafo_header, text="Inyecciones: 0 negativos | 0 ciclos", font=(MAIN_FONT, 12, "bold"), text_color=PRIMARY_COLOR)
        self.lbl_iny_total.pack(side="right", padx=20)
        
        # Pack diferido del encabezado
        self.f_grafo_header = f_grafo_header 
        
        self.f_canvas = ctk.CTkFrame(self.panel_visualizacion, fg_color="white", height=450)
        # self.panel_visualizacion NO se empaqueta aquí
        self.f_canvas.pack_propagate(False)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.f_canvas)
        # El widget de canvas se empaquetará solo cuando sea necesario en actualizar_lienzo
        
        # 3. GARANTIZAR OCULTACIÓN TOTAL AL INICIO
        self.panel_visualizacion.pack_forget()

        # --- FOOTER DE FLUJO (Independiente para pegarse a la tarjeta activa) ---
        self.f_flow_footer = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.f_flow_footer.grid_columnconfigure((0, 1), weight=1)

        self.btn_confirmar = ctk.CTkButton(self.f_flow_footer, text=" Confirmar grafo",
                                          image=self.ico_check, compound="left",
                                          font=FONT_LABEL, fg_color=SUCCESS_COLOR, text_color="black", 
                                          height=45, corner_radius=12, command=self.confirmar_grafo)
        
        self.btn_ejecutar = ctk.CTkButton(self.f_flow_footer, text=" Ejecutar benchmark",
                                         image=self.ico_rocket, compound="left",
                                         font=FONT_LABEL, fg_color=PRIMARY_COLOR, text_color="black", 
                                         height=45, corner_radius=12, state="disabled", command=self.acc_ejecutar_benchmark)

        self.btn_modificar = ctk.CTkButton(self.f_flow_footer, text=" Modificar",
                                          image=self.ico_pencil, compound="left",
                                          font=FONT_LABEL, fg_color="#F5F5F5", text_color="black", 
                                          border_width=1, border_color="#CCC", height=45, corner_radius=12, 
                                          command=self.acc_modificar)

        # 3. GARANTIZAR OCULTACIÓN TOTAL AL INICIO
        self.panel_visualizacion.pack_forget()
        self.f_middle.pack_forget()
        self.f_flow_footer.pack_forget()
        self.btn_generar.pack_forget()

        # PANEL DERECHO: Resultados del Benchmark
        self.panel_res = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=20)
        
        # Título con más aire hacia abajo
        ctk.CTkLabel(self.panel_res, text=" Análisis comparativo de rendimiento",
                     image=self.ico_trophy, compound="left",
                     font=("Outfit", 20, "bold"), text_color="#1A237E").pack(pady=(5, 15))

        res_grid = ctk.CTkFrame(self.panel_res, fg_color="transparent")
        res_grid.pack(fill="x", padx=10, pady=0)
        res_grid.grid_columnconfigure(0, weight=1)

        # SECCIÓN 1: TIEMPO (Velocímetros)
        m1 = ctk.CTkFrame(res_grid, fg_color="transparent")
        m1.grid(row=0, column=0, sticky="nsew", padx=10, pady=2)
        
        self.canvas_gauge = FigureCanvasTkAgg(self.fig_gauge, master=m1)
        self.canvas_gauge.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)
        
        # Subtítulo de Velocidad y ajuste de margen inferior (bottom agresivo para acercar textos)
        self.fig_gauge.suptitle("Velocidad de ejecución (ms)", fontsize=10, color="#888", y=0.98)
        self.fig_gauge.subplots_adjust(left=0.05, right=0.95, top=0.82, bottom=-0.1, wspace=0.1)
        
        f_time_res = ctk.CTkFrame(m1, fg_color="transparent")
        f_time_res.pack(fill="x", pady=0)
        f_time_res.grid_columnconfigure((0, 1), weight=1)
        
        # Etiquetas de Nombre (Centrado absoluto)
        self.lbl_dijkstra = ctk.CTkLabel(f_time_res, text="Dijkstra", font=FONT_LABEL, text_color="#555")
        self.lbl_dijkstra.grid(row=0, column=0, sticky="nsew")
        self.lbl_bf = ctk.CTkLabel(f_time_res, text="Bellman-Ford", font=FONT_LABEL, text_color="#555")
        self.lbl_bf.grid(row=0, column=1, sticky="nsew")

        # Etiquetas de Resultados (Milisegundos centrados)
        self.lbl_dijkstra_ms = ctk.CTkLabel(f_time_res, text="--- ms", font=FONT_RESULT)
        self.lbl_dijkstra_ms.grid(row=1, column=0, sticky="nsew")
        self.lbl_bf_ms = ctk.CTkLabel(f_time_res, text="--- ms", font=FONT_RESULT)
        self.lbl_bf_ms.grid(row=1, column=1, sticky="nsew")
        
        self.lbl_interpretation = ctk.CTkLabel(m1, text="", font=FONT_DETAIL, text_color="#666")
        self.lbl_interpretation.pack(pady=(2, 0))

        # SECCIÓN 2: MEMORIA (Más espacio respecto a velocidad)
        m2 = ctk.CTkFrame(res_grid, fg_color="white", corner_radius=15)
        m2.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.canvas_mem = FigureCanvasTkAgg(self.fig_mem, master=m2)
        self.canvas_mem.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=0)

        # SECCIÓN 3: COMPARATIVA DE DISTANCIA (Tarjetas de Estado)
        m3 = ctk.CTkFrame(res_grid, fg_color="transparent")
        m3.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        ctk.CTkLabel(m3, text="Comparativa de distancia final", font=FONT_LABEL, text_color="#455A64").pack(pady=(8, 5))
        
        # Tarjetas de Resultado (Dijkstra y Bellman-Ford)
        self.lbl_res_d = ctk.CTkLabel(m3, text="", font=FONT_LABEL, height=45, corner_radius=10, fg_color="#F5F5F5")
        self.lbl_res_d.pack(fill="x", padx=30, pady=3)
        
        self.lbl_res_bf = ctk.CTkLabel(m3, text="", font=FONT_LABEL, height=45, corner_radius=10, fg_color="#F5F5F5")
        self.lbl_res_bf.pack(fill="x", padx=30, pady=3)
        
        self.lbl_cost_insight = ctk.CTkLabel(m3, text="", font=FONT_LABEL)
        self.lbl_cost_insight.pack(pady=2)
        
        self.lbl_history_compact = ctk.CTkLabel(m3, text="Inyección: Ninguna", font=FONT_DETAIL, text_color="#78909C")
        self.lbl_history_compact.pack(pady=(0, 8))
        
        # --- BLOQUE DE ACCIONES FINALES (Exportar y Nueva Prueba) ---
        self.f_footer_res = ctk.CTkFrame(self.panel_res, fg_color="transparent")
        # Se muestra al final en terminar_benchmark
        
        self.btn_exportar = ctk.CTkButton(self.f_footer_res, text=" Reporte PDF",
                                         image=self.ico_pdf, compound="left",
                                         font=(MAIN_FONT, 13, "bold"), fg_color="#A594F1", 
                                         hover_color="#8B7EDC", text_color="black", height=42, width=180, 
                                         corner_radius=12, command=self.acc_exportar)
        self.btn_exportar.pack(side="left", padx=10, expand=True)

        self.btn_nueva = ctk.CTkButton(self.f_footer_res, text=" Nueva prueba",
                                 image=self.ico_refresh, compound="left",
                                 font=(MAIN_FONT, 13, "bold"), fg_color="#F5F5F5", text_color="black", 
                                 border_width=1, border_color="#CCC", hover_color="#E0E0E0", 
                                 height=42, width=180, corner_radius=12, command=self.acc_nueva_prueba)
        self.btn_nueva.pack(side="left", padx=10, expand=True)

        self.update_idletasks()

    # --- VALIDACIÓN DE ENTRADAS ---
    def validate_int(self, P):
        if P == "" or P.isdigit():
            if P.isdigit() and int(P) > 10000000:
                return False
            return True
        return False

    def validate_iny(self, P, iny_type):
        """Valida que la inyección no supere los límites dinámicos."""
        if P == "": return True
        if not P.isdigit(): return False
        
        n = self.get_n_nodos()
        val = int(P)
        if iny_type == "neg":
            # Lógica equilibrada: 10% de N para pequeños, tope en 1000 para grandes
            limite = min(max(1, int(n * 0.1)), 1000)
        else:
            # Lógica equilibrada: 10% de N para pequeños, tope en 100 para grandes
            limite = min(max(1, int(n * 0.1)), 100)
        
        return val <= limite

    def validate_float(self, P):
        """Valida densidad en porcentaje (0.00001% a 100%) con máx. 5 decimales."""
        if P == "" or P == ".": return True
        if not all(c.isdigit() or c == "." for c in P): return False
        if P.count(".") > 1: return False

        # Limitar a 5 decimales (0.00001% es el mínimo para N=10,000,000)
        if "." in P and len(P.split(".")[1]) > 5: return False

        try:
            val = float(P)
            if val > 100: return False

            # Validación de d_min dinámico (en porcentaje)
            n_raw = self.entry_nodos.get().strip()
            if n_raw and n_raw.isdigit():
                n = int(n_raw)
                if n >= 10:
                    d_min_pct = (1.0 / n) * 100
                    # Heurística: ¿Puede este prefijo llegar a d_min% añadiendo dígitos?
                    if float(P + "999999") < (d_min_pct - 1e-9):
                        return False

            return True
        except ValueError:
            return False

    def validar_densidad(self, event=None):
        """Ajusta la densidad al mínimo (1/N)*100% solo al perder el foco."""
        try:
            d_raw = self.entry_densidad.get().strip()
            if not d_raw: return
            d = float(d_raw)

            n_raw = self.entry_nodos.get().strip()
            n = int(n_raw) if n_raw else 10
            d_min_pct = (1.0 / n) * 100

            if d < d_min_pct:
                self.entry_densidad.delete(0, "end")
                clean_min = "{:.5f}".format(d_min_pct).rstrip('0').rstrip('.')
                self.entry_densidad.insert(0, clean_min)
            elif d > 100:
                self.entry_densidad.delete(0, "end")
                self.entry_densidad.insert(0, "100")
        except: pass

    def validar_rango_nodos(self, event=None):
        """Corrige el valor al rango [10, 10,000,000] solo al perder el foco."""
        try:
            val = self.entry_nodos.get().strip()
            if not val: return
            n = int(val)
            if n < 10:
                self.entry_nodos.delete(0, "end")
                self.entry_nodos.insert(0, "10")
                self.actualizar_nodos_defecto()
            elif n > 10000000:
                self.entry_nodos.delete(0, "end")
                self.entry_nodos.insert(0, "10000000")
                self.actualizar_nodos_defecto()
        except: pass

    # --- HELPERS ---
    def get_n_nodos(self):
        if not self.grafo: return 0
        if isinstance(self.grafo, dict) and self.grafo.get("__is_stress_matrix__"):
            return self.grafo["v"]
        # Filtrar solo claves que son nodos (evitar 'inyecciones', 'v', etc.)
        return len([k for k in self.grafo if k not in ["v", "__is_stress_matrix__", "inyecciones"]])

    def has_negativos(self):
        if isinstance(self.grafo, dict) and self.grafo.get("__is_stress_matrix__"):
            return (self.grafo["matrix"].data < 0).any()
        return any(w < 0 for u in self.grafo for w in self.grafo[u].values())

    # --- LOGICA ---
    def cambiar_estado(self, nuevo):
        self.estado_actual = nuevo
        is_ed = (nuevo == "EDITABLE")
        st_val = "normal" if is_ed else "disabled"
        # Botones que deben cambiar su estado (solo si están visibles)
        for b in [self.btn_confirmar, self.btn_generar, self.btn_iny_neg, self.btn_iny_ciclo, self.btn_limpiar, self.btn_ejecutar, self.btn_modificar]:
            if hasattr(b, "configure"):
                b.configure(state=st_val)
        self.entry_nodos.configure(state="normal" if is_ed else "disabled")
        self.entry_source.configure(state="normal" if is_ed else "disabled")
        self.entry_target.configure(state="normal" if is_ed else "disabled")
        self.btn_modificar.configure(state="normal" if nuevo == "BLOQUEADO" else "disabled")
        self.btn_ejecutar.configure(state="normal" if nuevo == "BLOQUEADO" else "disabled")

    def show_modal(self, tit, msg, color=ERROR_COLOR):
        try:
            d = ctk.CTkToplevel(self); d.title(tit); d.geometry("400x180"); d.attributes("-topmost", True)
            ctk.CTkLabel(d, text=msg, font=("Arial", 13), text_color=color, wraplength=350).pack(pady=30)
            ctk.CTkButton(d, text="Cerrar", command=d.destroy).pack()
        except: pass

    def sanitizar_iny(self, entry, iny_type):
        """Asegura que el valor final sea al menos 0."""
        val = entry.get().strip()
        if not val or int(val) < 0:
            entry.delete(0, "end")
            entry.insert(0, "0")

    def bloquear_configuracion(self, lock=True):
        """Bloquea o desbloquea los campos de configuración."""
        state = "readonly" if lock else "normal"
        self.entry_nodos.configure(state=state)
        self.entry_densidad.configure(state=state)
        if lock:
            self.btn_iny_neg.configure(state="disabled")
            self.btn_iny_ciclo.configure(state="disabled")
            self.btn_limpiar.configure(state="disabled")
            self.btn_generar.grid_remove()
        else:
            self.btn_generar.configure(state="normal", image=self.ico_dice, text=" Generar grafo aleatorio")
            self.f_iny.pack_forget()
            self.verificar_habilitacion_generar()

    def _finalizar_generacion(self, n_calc):
        self.f_iny.pack(pady=10)
        if n_calc <= 15:
            self.actualizar_tabla_desde_grafo()

    def on_closing(self):
        """Limpieza al cerrar la ventana."""
        if self.p and self.p.is_alive():
            self.p.terminate()
            self.p.join()
        if self.q:
            self.q.close()
            self.q.join_thread()
        plt.close('all')
        self.quit()
        self.destroy()

    def actualizar_nodos_defecto(self):
        try:
            val = self.entry_nodos.get().strip()
            if not val:
                self.entry_source.configure(state="normal")
                self.entry_source.delete(0, "end")
                self.entry_source.configure(state="readonly")
                
                self.entry_target.configure(state="normal")
                self.entry_target.delete(0, "end")
                self.entry_target.configure(state="readonly")
                
                self.entry_densidad.delete(0, "end")
                self.lbl_hint_densidad.configure(text="")
                self.lbl_hint_nodos.configure(text="Intervalo: 10 a 10,000,000")
                self.f_nodos.grid(row=0, column=0, columnspan=4, sticky="")
                for f in [self.f_densidad, self.f_source, self.f_target]:
                    f.grid_remove()
                self.verificar_habilitacion_generar()
                return
            n = int(val)
            if n >= 10:
                self.lbl_hint_nodos.configure(text="")
                n_cap = min(n, 10000000)
                d_min_pct = (1.0 / n) * 100
                # Formato limpio sin ceros sobrantes (máx 5 decimales)
                d_min_str = "{:.5f}".format(d_min_pct).rstrip('0').rstrip('.')
                msg_sug = f"Sugerido: {d_min_str}% a 100%"
                if n <= 20:
                    msg_sug += " (Vis. habilitada <= 30%)"
                self.lbl_hint_densidad.configure(text=msg_sug)

                # Re-validar densidad actual según el nuevo N
                d_curr = self.entry_densidad.get().strip()
                if d_curr:
                    try:
                        if float(d_curr) < d_min_pct:
                            self.entry_densidad.delete(0, "end")
                            self.entry_densidad.insert(0, d_min_str)
                    except: pass
                
                # Actualizar Origen (Solo lectura)
                self.entry_source.configure(state="normal")
                self.entry_source.delete(0, "end"); self.entry_source.insert(0, "0")
                self.entry_source.configure(state="readonly")
                
                # Actualizar Destino (Solo lectura con n-1)
                self.entry_target.configure(state="normal")
                self.entry_target.delete(0, "end"); self.entry_target.insert(0, f"{n_cap-1} (n-1)")
                self.entry_target.configure(state="readonly")
                
                self.f_nodos.grid(row=0, column=0, columnspan=1, sticky="ew")
                for f in [self.f_densidad, self.f_source, self.f_target]:
                    f.grid()
            else:
                self.lbl_hint_nodos.configure(text="Intervalo: 10 a 10,000,000")
                self.f_nodos.grid(row=0, column=0, columnspan=4, sticky="")
                for f in [self.f_densidad, self.f_source, self.f_target]:
                    f.grid_remove()
            
            self.verificar_habilitacion_generar()
        except: pass

    def verificar_habilitacion_generar(self, event=None):
        """Muestra y activa el botón solo si Nodos >= 10 y Densidad es válida y suficiente (>= 1/N)."""
        try:
            n_val = self.entry_nodos.get().strip()
            d_val = self.entry_densidad.get().strip()
            
            if n_val and d_val:
                try:
                    n = int(n_val)
                    d = float(d_val)
                    d_min_pct = (1.0 / n) * 100

                    # Condición proporcional (con pequeño margen de error float)
                    es_valido = (n >= 10 and d >= (d_min_pct - 1e-7) and d <= 100.001)

                    # Feedback visual de la densidad
                    if d < (d_min_pct - 1e-7):
                        self.lbl_hint_densidad.configure(text_color="#E74C3C")
                    else:
                        self.lbl_hint_densidad.configure(text_color="#78909C")
                    
                    if es_valido:
                        # Asegurar que el contenedor esté visible
                        self.f_actions.pack(fill="x", pady=5)
                        self.btn_generar.pack(pady=15)
                        self.btn_generar.configure(state="normal", fg_color=PRIMARY_COLOR)
                        return
                except: pass
            
            # Si no es válido o faltan valores, escondemos el botón y el panel
            self.btn_generar.pack_forget()
            self.panel_visualizacion.pack_forget()
        except:
            self.btn_generar.grid_remove()
            self.f_actions.pack_forget()

    def add_fila_tabla(self, u=None, v=None, w=None):
        r = ctk.CTkFrame(self.scroll_tabla, fg_color="transparent")
        r.pack(fill="x", expand=True, pady=2, padx=2)
        r.grid_columnconfigure((0,1,2), weight=1, minsize=120)
        
        row_data = {}
        for i, (key, val) in enumerate(zip(["u", "v", "w"], [u, v, w])):
            e = ctk.CTkEntry(r, justify="center", font=FONT_DETAIL, height=32, corner_radius=8, border_width=1)
            e.grid(row=0, column=i, sticky="ew", padx=5)
            if val is not None: 
                e.insert(0, str(val))
            e.configure(state="readonly") # Bloqueo absoluto para modo monitor
            row_data[key] = e
        
        self.filas_tabla.append(row_data)
        return row_data

    def actualizar_tabla_desde_grafo(self):
        # Limpiar tabla actual
        for f in self.filas_tabla:
            if hasattr(f, 'destroy'): f.destroy()
        self.filas_tabla = []
        for child in self.scroll_tabla.winfo_children(): child.destroy()

        n = self.get_n_nodos()
        
        # Calcular densidad REAL del grafo
        if isinstance(self.grafo, dict) and self.grafo.get("__is_stress_matrix__"):
            num_aristas = self.grafo["matrix"].nnz
        else:
            num_aristas = sum(len(self.grafo[u]) for u in self.grafo if isinstance(self.grafo[u], dict))
            
        densidad_real = num_aristas / (n * (n - 1)) if n > 1 else 0

        # Límite de visualización de tabla: Solo si N <= 20 y D <= 0.3
        if n > 20 or densidad_real > 0.3: 
            self.f_middle.pack_forget() # Ocultar tabla en modo stress
            return
        
        # Mostrar tabla solo si es un grafo analizable pequeño
        if not self.f_middle.winfo_ismapped():
            self.f_middle.pack(fill="x", padx=20, pady=10)

        # Configurar pesos de columnas para que la tabla sea ancha y balanceada
        for i in range(3): self.f_middle.grid_columnconfigure(i, weight=1, pad=2)

        for u in self.grafo:
            for v, w in self.grafo[u].items():
                self.add_fila_tabla(str(u), str(v), str(w))

    def acc_generar_aleatorio(self):
        try:
            # 1. Sanitizar y validar Nodos
            n_raw = self.entry_nodos.get().strip()
            if not n_raw: n = 10
            else: n = int(n_raw)
            
            if n < 10:
                n = 10
            elif n > 10000000:
                n = 10000000
            elif n > 500:
                pass # Eliminado el modal de Modo Stress
            
            # Actualizar campo de nodos
            self.entry_nodos.delete(0, "end"); self.entry_nodos.insert(0, str(n))
            
            # 2. Sanitizar y validar Densidad (campo en %, generador espera 0.0-1.0)
            d_raw = self.entry_densidad.get().replace(",", ".")
            try:
                d_pct = float(d_raw)
            except:
                d_pct = 30.0  # 30% por defecto

            d = d_pct / 100.0  # Conversión a decimal para el generador

            # Densidad mínima para garantizar conectividad
            d_min = 1.0 / n
            if d < d_min:
                d = d_min
                d_pct = d * 100
                self.show_modal("Conectividad", f"Densidad mínima para {n} nodos es {d_pct:.5f}%.\nSe ha ajustado para garantizar que exista al menos una ruta.", SECONDARY_COLOR)
            elif d > 1.0:
                d = 1.0
                d_pct = 100.0

            self.entry_densidad.delete(0, "end"); self.entry_densidad.insert(0, f"{d_pct:.5f}".rstrip('0').rstrip('.'))

            # 3. Validar Origen y Destino (Extrayendo solo el número para la lógica)
            try:
                s_str = str(self.entry_source.get()).split()[0]
                t_str = str(self.entry_target.get()).split()[0]
                s = int(s_str)
                t = int(t_str)
            except:
                s, t = 0, n - 1
            
            if not (0 <= s < n): s = 0
            if not (0 <= t < n): t = n - 1
            
            self.entry_source.delete(0, "end"); self.entry_source.insert(0, str(s))
            self.entry_target.delete(0, "end"); self.entry_target.insert(0, str(t))

            self.seed = random.randint(1, 9999)
            self.btn_generar.configure(image=self.ico_timer, text=" Generando...", state="disabled")
            
            # Limpiar estado previo
            self.f_middle.pack_forget()
            self.panel_visualizacion.pack_forget()
            self.panel_res.pack_forget()
            self.f_flow_footer.pack_forget()
            self.btn_confirmar.pack_forget()
            self.btn_ejecutar.pack_forget()
            self.btn_modificar.pack_forget()
            
            self.inyecciones = {"negativos": 0, "ciclos": 0}
            
            # Usar contexto explícito para máxima estabilidad en macOS
            ctx = multiprocessing.get_context('spawn')
            q_gen = ctx.Queue()
            p_gen = ctx.Process(target=self._worker_generar, args=(n, d, self.seed, q_gen, s, t))
            p_gen.start()

            def _finalizar_generacion(res):
                # 1. Bloquear configuración primero
                self.bloquear_configuracion(True)
                
                # 2. Asignar y actualizar visualización
                self.grafo = res["grafo"]
                # La tabla se actualiza abajo solo si N <= 15
                self.actualizar_lienzo()
                
                # 3. Barra de Flujo (Se pega debajo de la última tarjeta visible)
                self.f_flow_footer.pack(fill="x", pady=(0, 20), padx=20)
                self.btn_confirmar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
                self.btn_modificar.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
                self.btn_modificar.configure(state="normal")
                self.btn_ejecutar.grid_forget()
                
                # 4. Activar Inyectores, hints y botón limpiar (Usando pack secuencial)
                self.f_iny.pack(pady=10)
                self.btn_limpiar.pack(pady=(10, 0))
                self.lbl_status_iny.pack(pady=(5, 10))
                
                # Dejar que la validación KeyRelease controle los inyectores
                self.btn_limpiar.configure(state="normal")
                
                n_calc = self.get_n_nodos()
                
                # OPTIMIZACIÓN: Solo actualizar tabla para grafos pequeños
                if n_calc <= 15:
                    self.actualizar_tabla_desde_grafo()
                else:
                    self.f_middle.pack_forget() # Asegurar que la tabla no estorbe
                lim_neg = min(max(1, int(n_calc * 0.1)), 1000)
                lim_cic = min(max(1, int(n_calc * 0.1)), 100)
                
                txt_neg = "(Límite proporcional: 10% de N)" if lim_neg < 1000 else "(Tope máximo de seguridad)"
                txt_cic = "(Límite proporcional: 10% de N)" if lim_cic < 100 else "(Tope máximo de seguridad)"
                
                self.lbl_iny_neg_l1.configure(text=f"Máximo para este caso: {lim_neg}")
                self.lbl_iny_neg_l2.configure(text=txt_neg)
                self.lbl_iny_ciclo_l1.configure(text=f"Máximo para este caso: {lim_cic}")
                self.lbl_iny_ciclo_l2.configure(text=txt_cic)
                
                self.btn_generar.configure(image=self.ico_dice, text=" Generar grafo aleatorio", state="normal")

            def monitorear_gen():
                if not self.winfo_exists(): return
                
                try:
                    resultado = q_gen.get_nowait()
                    if "error" in resultado:
                        self.show_modal("Error", resultado["error"])
                        self.btn_generar.configure(state="normal")
                    else:
                        _finalizar_generacion(resultado)
                    p_gen.join()
                    return
                except: pass

                if not p_gen.is_alive():
                    try:
                        resultado = q_gen.get(timeout=0.1)
                        if "error" in resultado: self.show_modal("Error", resultado["error"])
                        else: _finalizar_generacion(resultado)
                    except:
                        # Si no hay nada en la cola y el proceso murió, algo falló
                        self.btn_generar.configure(state="normal")
                    p_gen.join()
                    return

                self.after(100, monitorear_gen)

            self.after(100, monitorear_gen)
            
        except Exception as e: self.show_modal("Error", f"Fallo al iniciar generación: {e}")

    @staticmethod
    def _worker_generar(n, d, seed, q, s, t):
        try:
            # Importación local para evitar problemas de serialización
            import sys
            import os
            sys.path.append(os.getcwd())
            from generador import generar_grafo
            g = generar_grafo(n, d, seed, source=s, target=t)
            q.put({"grafo": g})
        except Exception as e:
            import traceback
            q.put({"error": f"Error en trabajador: {str(e)}\n{traceback.format_exc()}"})

    def acc_cargar_manual(self):
        g = {}
        try:
            for row in self.filas_tabla:
                u, v, w = row["u"].get(), row["v"].get(), row["w"].get()
                if u and v and w:
                    if u not in g: g[u] = {}
                    g[u][v] = int(w)
            if g: 
                self.grafo = g
                self.inyecciones = {"negativos": 0, "ciclos": 0}
                self.actualizar_lienzo()
            else: self.show_modal("Aviso", "Tabla vacía")
        except: self.show_modal("Error", "Pesos inválidos")

    def acc_descargar_manual(self):
        """Genera un archivo HTML a partir del Markdown y lo abre en el navegador con opción de PDF."""
        try:
            ruta_md = "Manual/Manual_Usuario.md"
            if not os.path.exists(ruta_md):
                self.show_modal("Error", "No se encontró el archivo Manual_Usuario.md")
                return

            with open(ruta_md, "r", encoding="utf-8") as f:
                md_text = f.read()

            # Separar la portada del resto (usando la primera regla horizontal ---) para centrarla
            partes = md_text.split("---", 1)
            if len(partes) > 1:
                portada_md = partes[0]
                resto_md = "---" + partes[1]
                
                portada_html = markdown.markdown(portada_md, extensions=['extra'])
                resto_html = markdown.markdown(resto_md, extensions=['extra', 'toc', 'fenced_code'])
                html_body = f'<div class="cover-page">{portada_html}</div>{resto_html}'
            else:
                html_body = markdown.markdown(md_text, extensions=['extra', 'toc', 'fenced_code'])

            # Plantilla HTML con CSS profesional
            full_html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Manual de Usuario - Benchmark</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                    :root {{
                        --primary: #B39DDB;
                        --secondary: #90CAF9;
                        --text: #2c3e50;
                        --bg: #f8f9fa;
                    }}
                    body {{
                        font-family: Arial, sans-serif;
                        font-size: 12pt;
                        line-height: 1.6;
                        color: var(--text);
                        background: var(--bg);
                        margin: 0;
                        padding: 0;
                        text-align: justify;
                    }}
                    .cover-page {{
                        text-align: center;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        break-after: page;
                        page-break-after: always;
                        padding: 20px;
                        border: 3px double var(--primary);
                        margin: 0;
                        box-sizing: border-box;
                    }}
                    .cover-page h1 {{
                        font-size: 20pt;
                        color: var(--primary);
                        margin: 10px 0;
                        text-align: center !important;
                    }}
                    .cover-page p {{
                        font-size: 11pt;
                        margin: 4px 0;
                        text-align: center !important;
                    }}
                    .cover-page strong {{
                        display: inline;
                    }}
                    .cover-page ul {{
                        display: inline-block;
                        text-align: left;
                        margin: 10px auto;
                        padding-left: 20px;
                    }}
                    .cover-page li {{
                        font-size: 11pt;
                        margin-bottom: 2px;
                        list-style-type: disc;
                    }}
                    /* Estilos profesionales para el Índice (TOC) */
                    .toc-list {{
                        list-style: none !important;
                        padding: 0 !important;
                    }}
                    .toc-list li a {{
                        display: flex;
                        justify-content: space-between;
                        align-items: baseline;
                        text-decoration: none;
                        color: var(--text);
                    }}
                    .toc-list li a::after {{
                        content: " ...........................................................................................................................................................................";
                        flex: 1;
                        white-space: nowrap;
                        overflow: hidden;
                        margin: 0 10px;
                        color: #ccc;
                        order: 1;
                    }}
                    .toc-list li a span {{
                        font-weight: bold;
                        min-width: 20px;
                        text-align: right;
                        order: 2;
                    }}
                    .toc-list ul {{
                        list-style: none !important;
                        padding-left: 20px !important;
                    }}
                    /* Estilo para los enlaces de retorno al índice */
                    h1 a, h2 a, h3 a, h4 a, blockquote a {{
                        text-decoration: none !important;
                        color: inherit !important;
                        cursor: pointer;
                        display: block; /* Forzar que cubra todo el espacio */
                    }}
                    blockquote a img {{
                        border: none !important;
                        outline: none !important;
                        cursor: pointer;
                    }}
                    .navbar {{
                        background: white;
                        padding: 1rem 10%;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        position: sticky;
                        top: 0;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        z-index: 1000;
                    }}
                    .container {{
                        max-width: 900px;
                        margin: 2rem auto;
                        background: white;
                        padding: 3rem;
                        border-radius: 20px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
                    }}
                    .btn-print {{
                        background: var(--primary);
                        color: black;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 10px;
                        font-weight: bold;
                        cursor: pointer;
                        transition: all 0.3s;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }}
                    .btn-print:hover {{
                        background: var(--secondary);
                        transform: translateY(-2px);
                    }}
                    h1, h2, h3 {{ color: #4527a0; text-align: left; }}
                    p {{
                        text-align: justify;
                        text-justify: inter-word;
                    }}
                    table {{
                        width: 90%;
                        max-width: 800px;
                        border-collapse: collapse;
                        margin: 30px auto;
                        background: #fff;
                    }}
                    th, td, td p, td span {{
                        text-align: center !important;
                    }}
                    th {{
                        padding: 12px;
                        border: 1px solid #ddd;
                        background: #f3f4f6;
                        font-weight: bold;
                    }}
                    td {{
                        padding: 12px;
                        border: 1px solid #ddd;
                    }}
                    td p {{
                        margin: 0;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 12px;
                        display: block;
                        margin: 20px auto;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    }}
                    blockquote {{
                        border-left: 5px solid var(--primary);
                        background: #f3f0ff;
                        padding: 15px;
                        margin: 20px 0;
                        font-style: italic;
                        text-align: justify;
                    }}
                    ul, ol {{
                        margin: 20px 0;
                        padding-left: 30px;
                        text-align: justify;
                    }}
                    li {{
                        margin-bottom: 10px;
                    }}
                    pre {{
                        background: #282c34;
                        color: #abb2bf;
                        padding: 15px;
                        border-radius: 8px;
                        overflow-x: auto;
                        text-align: left !important;
                        font-size: 10pt;
                        margin: 15px 0;
                        line-height: 1.4;
                    }}
                    code {{
                        font-family: 'Courier New', Courier, monospace;
                    }}
                    @media print {{
                        .navbar {{ display: none; }}
                        .container {{ 
                            box-shadow: none; 
                            margin: 0; 
                            padding: 0; 
                            max-width: 100%; 
                        }}
                        body {{ 
                            background: white; 
                            font-size: 11pt;
                        }}
                        .container {{
                            padding: 1cm;
                        }}
                        /* Ocultar separadores en impresión para evitar líneas y espacios extra */
                        hr {{
                            display: none;
                        }}
                        /* Evitar que los títulos se queden solos al final de la página */
                        h1, h2, h3, h4 {{
                            break-after: avoid;
                            page-break-after: avoid;
                            margin-top: 30px;
                        }}
                        /* Forzar salto de página en secciones de presentación */
                        .page-break {{
                            display: block;
                            break-after: page !important;
                            page-break-after: always !important;
                            height: 0;
                            margin: 0;
                        }}
                        #1-indice-general, 
                        #2-indice-de-imagenes, 
                        #3-introduccion,
                        #4-marco-teorico-algoritmos-de-ruta-mas-corta {{
                            break-before: page !important;
                            page-break-before: always !important;
                            margin-top: 0 !important;
                        }}
                        /* Evitar que elementos clave se corten a la mitad y permitir división de tablas */
                        img, pre, blockquote {{
                            break-inside: avoid !important;
                            page-break-inside: avoid !important;
                        }}
                        table {{
                            break-inside: auto !important;
                        }}
                        thead {{
                            display: table-header-group;
                        }}
                        /* Regla general: Figuras y códigos no se dividen internamente */
                        img, pre {{
                            break-inside: avoid !important;
                            page-break-inside: avoid !important;
                        }}
                        /* Las figuras (blockquote) pueden dividirse pero con títulos pegados */
                        blockquote {{
                            break-inside: auto !important;
                            page-break-inside: auto !important;
                            padding: 10px 15px !important;
                            margin: 10px 0 !important;
                        }}
                        /* Soldadura universal: Título e Imagen siempre juntos */
                        /* Soldadura universal: Título (p1) e Imagen (p2) siempre juntos */
                        /* Usamos selector de ID para máxima prioridad en el navegador */
                        [id^="img"] + blockquote p:nth-of-type(1) {{
                            break-after: avoid-page !important;
                            page-break-after: avoid-page !important;
                            margin-bottom: 0 !important;
                        }}
                        [id^="img"] + blockquote p:nth-of-type(2) {{
                            break-before: avoid-page !important;
                            page-break-before: avoid-page !important;
                            margin-top: 0 !important;
                        }}
                        /* El pie de imagen (p3) sí tiene permiso de saltar */
                        [id^="img"] + blockquote p:nth-of-type(3) {{
                            break-before: auto !important;
                            page-break-before: auto !important;
                        }}
                        blockquote strong {{
                            display: inline;
                        }}
                        p, ul, ol {{
                            margin: 8px 0 !important;
                        }}
                        pre {{
                            background: #282c34 !important;
                            color: #abb2bf !important;
                            -webkit-print-color-adjust: exact;
                            print-color-adjust: exact;
                            padding: 15px;
                            border-radius: 8px;
                        }}
                        img {{
                            max-width: 70% !important;
                            height: auto;
                            display: block;
                            margin: 15px auto !important;
                            break-inside: avoid !important;
                            break-before: avoid !important;
                        }}
                        .cover-page img {{
                            max-width: 100% !important;
                            margin-bottom: 20px !important;
                        }}
                        /* Asegurar que las tablas ocupen el ancho disponible */
                        table {{
                            width: 100% !important;
                        }}
                        tr {{
                            break-inside: avoid;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="navbar">
                    <div style="font-weight: bold; color: var(--primary);">Benchmarking Software</div>
                    <button class="btn-print" onclick="window.print()">
                        <i class="fas fa-file-pdf"></i> Guardar como PDF
                    </button>
                </div>
                <div class="container">
                    {html_body}
                </div>
            </body>
            </html>
            """

            ruta_html = "Manual/Manual_Usuario.html"
            with open(ruta_html, "w", encoding="utf-8") as f:
                f.write(full_html)

            webbrowser.open("file://" + os.path.abspath(ruta_html))

        except Exception as e:
            self.show_modal("Error", f"No se pudo generar el manual: {{str(e)}}")

    def acc_ejecutar_benchmark(self):
        source = str(self.entry_source.get()).split()[0]
        target = str(self.entry_target.get()).split()[0]
        
        # Validar existencia de nodos
        if isinstance(self.grafo, dict) and self.grafo.get("__is_stress_matrix__"):
            try:
                s_int, t_int = int(source), int(target)
                if not (0 <= s_int < self.grafo["v"]):
                    self.show_modal("Error", f"Origen '{source}' fuera de rango (0-{self.grafo['v']-1})")
                    return
                if not (0 <= t_int < self.grafo["v"]):
                    self.show_modal("Error", f"Destino '{target}' fuera de rango (0-{self.grafo['v']-1})")
                    return
            except ValueError:
                self.show_modal("Error", "En modo stress, los nodos deben ser números.")
                return
        else:
            if source not in self.grafo:
                self.show_modal("Error", f"El nodo origen '{source}' no existe.")
                return
            if target not in self.grafo:
                self.show_modal("Error", f"El nodo destino '{target}' no existe.")
                return

        self.cambiar_estado("EJECUCION")
        self.btn_ejecutar.configure(image=self.ico_timer, text=" Procesando...", state="disabled")
        
        # Inyectar metadatos para el Modo Diagnóstico Rápido
        if isinstance(self.grafo, dict):
            self.grafo["inyecciones"] = self.inyecciones
            
        self.q = multiprocessing.Queue()
        self.p = multiprocessing.Process(target=ejecutar_en_proceso_separado, args=(self.grafo, source, target, self.q))
        
        self.p_error_msg = None
        def safe_start():
            try: self.p.start()
            except Exception as e: self.p_error_msg = str(e)

        import threading
        threading.Thread(target=safe_start, daemon=True).start()
        
        def monitorear():
            if not self.winfo_exists(): return
            
            if self.p_error_msg:
                self.show_modal("Error de arranque", f"No se pudo iniciar el motor:\n{self.p_error_msg}")
                self.btn_ejecutar.configure(image=self.ico_rocket, text=" Ejecutar benchmark", state="normal")
                return

            # Esperar a que el proceso tenga PID
            if self.p.pid is None:
                self.after(100, monitorear)
                return

            try:
                res = self.q.get_nowait()
                if "error" in res:
                    self.show_modal("Error en benchmark", res["error"])
                    self.cambiar_estado("BLOQUEADO")
                else:
                    self.finalizar_benchmark(res)
                
                self.p.join()
                self.btn_ejecutar.configure(image=self.ico_rocket, text=" Ejecutar benchmark")
                self.p = None
                self.q = None
                return
            except:
                if not self.p.is_alive():
                    # Aquí ya estamos seguros de que el proceso empezó y luego murió
                    self.show_modal("Fallo del proceso", "El motor de cálculo se cerró inesperadamente.")
                    self.cambiar_estado("BLOQUEADO")
                    self.btn_ejecutar.configure(image=self.ico_rocket, text=" Ejecutar benchmark")
                    self.p.join()
                    self.p = None
                    self.q = None
                    return
            
            self.after(100, monitorear)

        self.after(100, monitorear)

    def finalizar_benchmark(self, res):
        if not self.panel_res.winfo_ismapped():
            self.panel_res.pack(pady=10, padx=20, fill="x")

        self.resultados_actuales = res
        t_d, t_b = res['dijkstra']['tiempo_promedio_ms'], res['bellman_ford']['tiempo_promedio_ms']
        m_d, m_b = res['dijkstra']['memoria_pico_kb'], res['bellman_ford']['memoria_pico_kb']
        
        # Actualizar gráficas
        self.actualizar_graficas(t_d, t_b, m_d, m_b)
        
        # Actualizar etiquetas de tiempo (4 decimales + ms)
        self.lbl_dijkstra_ms.configure(text=f"{t_d:.4f} ms")
        self.lbl_bf_ms.configure(text=f"{t_b:.4f} ms")
        
        # Bonus: Línea de interpretación automática
        if t_d > 0 and t_b > 0:
            winner = "Dijkstra" if t_d < t_b else "Bellman-Ford"
            diff = abs(t_d - t_b)
            perc = (diff / max(t_d, t_b)) * 100
            self.lbl_interpretation.configure(text=f"✨ {winner} fue un {perc:.1f}% más rápido en este escenario")
        else:
            self.lbl_interpretation.configure(text="")

        # Formatear reporte de comparación
        salida_d = res['dijkstra']['salida']
        salida_bf = res['bellman_ford']['salida']
        
        # Extraer estadísticas
        stats_d = salida_d[0] if isinstance(salida_d, (tuple, list)) else salida_d
        stats_bf = salida_bf[0] if isinstance(salida_bf, (tuple, list)) else salida_bf
        
        d_val = stats_d.get("dist_target", "inf")
        bf_val = stats_bf.get("dist_target", "inf")
        has_cycle = salida_bf[2] if isinstance(salida_bf, (tuple, list)) and len(salida_bf) > 2 else False

        # --- Lógica de Interpretación de Costos ---
        try:
            d_val_num = float(d_val) if str(d_val).replace('.','').replace('-','').isdigit() else float('inf')
            bf_val_num = float(bf_val) if str(bf_val).replace('.','').replace('-','').isdigit() else float('inf')
        except: d_val_num, bf_val_num = float('inf'), float('inf')

        # Actualizar componentes visuales
        self.panel_res.pack(fill="both", expand=True, padx=20, pady=(10, 25))
        self.actualizar_graficas(t_d, t_b, m_d, m_b)
        self.actualizar_tarjetas_costo(d_val_num, bf_val_num, has_cycle)

        # Semántica: El más rápido en verde
        c_d = SUCCESS_COLOR if (t_d > 0 and t_d <= t_b) else "#555"
        c_b = SUCCESS_COLOR if (t_b > 0 and t_b < t_d) else "#555"
        
        self.lbl_dijkstra.configure(text_color=c_d)
        self.lbl_bf.configure(text_color=c_b)
        self.lbl_dijkstra_ms.configure(text_color=c_d)
        self.lbl_bf_ms.configure(text_color=c_b)

        # Insight automático pedagógico (Explica el PORQUÉ de los resultados)
        if has_cycle:
            insight = "⚠️ Ciclo negativo: Dijkstra es inválido. Bellman-Ford detectó la anomalía."
            color_i = ERROR_COLOR
        elif abs(d_val_num - bf_val_num) > 0.1 and self.has_negativos():
            insight = "⚠️ Pesos negativos: Dijkstra perdió precisión. Bellman-Ford es el resultado real."
            color_i = "#FF8F00" # Naranja de advertencia
        elif d_val_num == bf_val_num and d_val_num != float('inf'):
            insight = f"✅ Consistencia: Ambos algoritmos coinciden. {winner} fue más rápido."
            color_i = SUCCESS_COLOR
        else:
            insight = "ℹ️ Bellman-Ford es preferible para validar grafos con pesos negativos."
            color_i = SECONDARY_COLOR

        self.lbl_cost_insight.configure(text=insight, text_color=color_i)
        
        # Historial compacto
        neg, cic = self.inyecciones.get("negativos", 0), self.inyecciones.get("ciclos", 0)
        self.lbl_history_compact.configure(text=f"Inyección: {neg} peso(s) negativos · {cic} ciclo(s) detectados")

        self.update_idletasks()
        
        if self.get_n_nodos() <= 500:
            salida_bf = res['bellman_ford']['salida']
            has_cycle, affected = salida_bf[2], salida_bf[3]
            # Filtrar solo nodos reales para asignar colores
            nodos_reales = [n for n in self.grafo if n not in ["v", "__is_stress_matrix__", "inyecciones"]]
            colors = {n: (AFFECTED_COLOR if has_cycle and n in affected else SUCCESS_COLOR) for n in nodos_reales}
            self.actualizar_lienzo(colors=colors)
        
        # Ocultar controles de configuración y flujo una vez mostrados los resultados
        self.f_flow_footer.pack_forget()
        self.f_actions.pack_forget()
        
        # Mostrar botones finales en el footer del reporte con margen inferior
        self.f_footer_res.pack(fill="x", pady=(15, 20))
        self.btn_exportar.configure(state="normal")
        self.cambiar_estado("BLOQUEADO")
        self.update_idletasks()


    def actualizar_lienzo(self, colors=None):
        # 1. SEGURIDAD TOTAL: Si no hay grafo, NUNCA mostrar el panel
        if self.grafo is None:
            if hasattr(self, 'panel_visualizacion'):
                self.panel_visualizacion.pack_forget()
            return

        # 2. Límite de Visualización Detallada (Nodos y Densidad Real)
        num_nodos = self.get_n_nodos()
        
        if isinstance(self.grafo, dict) and self.grafo.get("__is_stress_matrix__"):
            num_aristas = self.grafo["matrix"].nnz
        else:
            num_aristas = sum(len(self.grafo[u]) for u in self.grafo if isinstance(self.grafo[u], dict))
            
        densidad_real = num_aristas / (num_nodos * (num_nodos - 1)) if num_nodos > 1 else 0
        
        # REGLA ESTRICTA: Mostrar dibujo solo si N <= 20 y D <= 0.3 y NO es modo stress
        es_stress = (isinstance(self.grafo, dict) and self.grafo.get("__is_stress_matrix__"))
        
        if num_nodos <= 20 and densidad_real <= 0.3 and not es_stress:
            self.panel_visualizacion.configure(height=500) # Restaurar tamaño
            self.panel_visualizacion.pack(fill="x", padx=20, pady=10)
            self.f_grafo_header.pack(fill="x", pady=10)
            self.f_canvas.pack(fill="x", padx=20, pady=10)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            # OCULTAR COMPLETAMENTE LA TARJETA EN MODO STRESS
            self.panel_visualizacion.pack_forget()
            return

        # 3. Mostrar panel solo si ya pasamos los filtros de N <= 15 y D <= 0.3 arriba
        if not self.panel_visualizacion.winfo_ismapped():
            self.panel_visualizacion.pack(pady=10, padx=20, fill="x")

        # Si es matriz de stress, no dibujamos (sería un caos visual)
        if isinstance(self.grafo, dict) and self.grafo.get("__is_stress_matrix__"):
            self.ax.clear()
            self.ax.text(0.5, 0.5, f"Modo stress activo\n({self.grafo['v']:,} nodos)\nVisualización simplificada", 
                         ha='center', va='center', fontsize=12, color=PRIMARY_COLOR)
            self.canvas.draw()
            return

        self.ax.clear()
        G = nx.DiGraph()
        
        # Filtrar solo nodos reales para el dibujo
        nodos_reales = [u for u in self.grafo if u not in ["inyecciones", "v", "__is_stress_matrix__"]]
        
        for u in nodos_reales:
            for v, w in self.grafo[u].items():
                if v in nodos_reales: # Asegurar que el destino también es un nodo real
                    G.add_edge(u, v, weight=w)
            # Agregar el nodo incluso si no tiene aristas
            if u not in G: G.add_node(u)
        
        if G.nodes:
            pos = nx.spring_layout(G, seed=42)
            cols = [colors.get(str(node), "skyblue") if colors else "skyblue" for node in G.nodes]
            nx.draw(G, pos, ax=self.ax, with_labels=True, node_color=cols, 
                    node_size=600, font_weight="bold", edge_color="#DDD", alpha=0.5)
        self.ax.set_axis_off(); self.canvas.draw()

    def _dibujar_reloj(self, ax, val, max_val, titulo, color):
        ax.clear()
        ax.set_theta_zero_location("W")
        ax.set_theta_direction(-1)
        ax.set_thetalim(0, np.pi)
        
        # Fondo minimalista
        ax.bar([np.pi/2], [1], width=np.pi, color="#F5F5F5", bottom=0.3, edgecolor="none")
        
        progreso = min(1.0, val / max_val) if max_val > 0 else 0
        angulo = progreso * np.pi
        
        if progreso > 0:
            ax.bar([angulo/2], [1], width=angulo, color=color, bottom=0.3, alpha=0.9, edgecolor="none")
        
        # Aguja mínima
        ax.annotate("", xy=(angulo, 1.0), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-", color="#444", lw=2))
        
        ax.plot(0, 0, 'o', color="#444", markersize=6)
        
        # ELIMINADO EL TEXTO INTERNO PARA MOVERLO A CTK
        ax.set_axis_off()

    def actualizar_graficas(self, td, tb, md, mb):
        # Escala unificada para velocímetros
        max_t = max(td, tb, 0.1) * 1.1
        
        # Colores semánticos: Verde para el ganador, Gris/Primario para el otro
        c_d = SUCCESS_COLOR if (td > 0 and td <= tb) else PRIMARY_COLOR
        c_b = SUCCESS_COLOR if (tb > 0 and tb < td) else PRIMARY_COLOR
        if tb > 0 and (self.resultados_actuales.get('bellman_ford', {}).get('salida', [0,0,False])[2]):
             c_b = ERROR_COLOR # Rojo si hay ciclo
        
        self._dibujar_reloj(self.ax_d_gauge, td, max_t, "Dijkstra", c_d)
        self._dibujar_reloj(self.ax_b_gauge, tb, max_t, "Bellman-Ford", c_b)
        
        self.lbl_dijkstra.configure(text_color=c_d)
        self.lbl_bf.configure(text_color=c_b)
        self.lbl_dijkstra_ms.configure(text_color=c_d)
        self.lbl_bf_ms.configure(text_color=c_b)
        
        # Eliminado tight_layout para usar subplots_adjust fijo
        self.canvas_gauge.draw()
        
        # 2. Barras de Memoria Minimalistas
        self.ax_mem.clear()
        if md > 0 or mb > 0:
            import matplotlib.patches as patches
            values = [md, mb]
            labels = ['Dijkstra', 'Bellman-Ford']
            
            height = 0.3
            max_val = max(values) if max(values) > 0 else 1.0
            
            for i, val in enumerate(values):
                col = SECONDARY_COLOR if i == 0 else "#CFD8DC"
                display_val = max(val, max_val * 0.12)
                
                box = patches.FancyBboxPatch(
                    (0, i - height/2), display_val, height,
                    boxstyle="round,pad=0,rounding_size=0.1",
                    linewidth=0, facecolor=col, mutation_scale=1
                )
                self.ax_mem.add_patch(box)
                self.ax_mem.text(display_val + (max_val*0.03), i, f'{val:.1f} KB', 
                                 va='center', fontsize=11, fontweight='bold', color="#333") 
            
            self.ax_mem.set_yticks([0, 1])
            self.ax_mem.set_yticklabels(labels, fontsize=10, color="#444")
            self.ax_mem.set_xlim(0, max_val * 1.35)
        else:
            self.ax_mem.set_axis_off()
            
        self.ax_mem.set_title("Uso de memoria (KB)", fontsize=10, color="#888", pad=15) # Título con aire
        for s in ['top', 'right', 'left', 'bottom']: self.ax_mem.spines[s].set_visible(False)
        self.ax_mem.tick_params(axis='both', which='both', length=0)
        self.ax_mem.set_xticks([])
        
        self.fig_mem.tight_layout()
        self.canvas_mem.draw()

    def actualizar_tarjetas_costo(self, d_val, bf_val, has_cycle):
        val_d = f"{d_val:.0f}" if d_val != float('inf') else "∞"
        val_bf = f"{bf_val:.0f}" if bf_val != float('inf') else "∞"
        
        # Lógica Dijkstra
        if has_cycle:
            txt_d = f"  Dijkstra: {val_d} (Ignora ciclo negativo)"
            bg_d = "#FFEBEE"; fg_d = "#C62828" # Rojo error
        elif abs(d_val - bf_val) > 0.1:
            txt_d = f"  Dijkstra: {val_d} (Inexacto por pesos negativos)"
            bg_d = "#FFF3E0"; fg_d = "#E65100" # Naranja aviso
        else:
            txt_d = f"  Dijkstra: {val_d} (Resultado válido)"
            bg_d = "#E8F5E9"; fg_d = "#2E7D32" # Verde éxito
            
        # Lógica Bellman-Ford
        if has_cycle:
            txt_bf = f"  Bellman-Ford: {val_bf} (Ciclo negativo detectado)"
            bg_bf = "#E8F5E9"; fg_bf = "#2E7D32" # Sigue siendo verde porque detectó el error
        else:
            txt_bf = f"  Bellman-Ford: {val_bf} (Resultado válido)"
            bg_bf = "#E8F5E9"; fg_bf = "#2E7D32"
            
        self.lbl_res_d.configure(text=txt_d, fg_color=bg_d, text_color=fg_d)
        self.lbl_res_bf.configure(text=txt_bf, fg_color=bg_bf, text_color=fg_bf)

    def inyectar_negativo(self):
        if not self.grafo: return
        n = self.get_n_nodos()
        # Lógica equilibrada: 10% de N, máximo 1000
        limite = min(max(1, int(n * 0.1)), 1000)
        try:
            raw = self.entry_qty_neg.get().strip()
            if not raw or int(raw) <= 0: return 
            qty = min(int(raw), limite)
        except: return
        
        self.grafo = inyectar_peso_negativo(self.grafo, qty, self.seed)
        self.inyecciones["negativos"] += qty
        self.lbl_iny_total.configure(text=f"Inyecciones: {self.inyecciones['negativos']} negativos | {self.inyecciones['ciclos']} ciclos")
        self.actualizar_lienzo()
        self.actualizar_tabla_desde_grafo() # Refrescar monitor
        self.lbl_status_iny.configure(text=f"✅ +{qty} peso(s) negativos inyectados", text_color="#B8860B")
        self.lbl_status_iny.pack(side="bottom", pady=(5, 10))
        # Bloquear edición tras inyectar para fijar el valor
        self.entry_qty_neg.configure(state="readonly")
        self.btn_iny_neg.configure(state="disabled")
        self.after(3000, lambda: self.lbl_status_iny.configure(text=""))

    def inyectar_ciclo(self):
        if not self.grafo: return
        n = self.get_n_nodos()
        # Lógica equilibrada: 10% de N, máximo 100
        limite = min(max(1, int(n * 0.1)), 100)
        try:
            raw = self.entry_qty_ciclo.get().strip()
            if not raw or int(raw) <= 0: return
            qty = min(int(raw), limite)
        except: return

        self.grafo = inyectar_ciclo_negativo(self.grafo, qty, self.seed)
        self.inyecciones["ciclos"] += qty
        self.lbl_iny_total.configure(text=f"Inyecciones: {self.inyecciones['negativos']} negativos | {self.inyecciones['ciclos']} ciclos")
        self.actualizar_lienzo()
        self.actualizar_tabla_desde_grafo() # Refrescar monitor
        self.lbl_status_iny.configure(text=f"✅ +{qty} ciclo(s) negativos inyectados", text_color=ERROR_COLOR)
        self.lbl_status_iny.pack(side="bottom", pady=(5, 10))
        # Bloquear edición tras inyectar para fijar el valor
        self.entry_qty_ciclo.configure(state="readonly")
        self.btn_iny_ciclo.configure(state="disabled")
        self.after(3000, lambda: self.lbl_status_iny.configure(text=""))

    def limpiar_pesos(self):
        """Restaura los pesos y resetea los campos de inyección silenciosamente."""
        self.grafo = sanitizar_pesos(self.grafo)
        self.inyecciones = {"negativos": 0, "ciclos": 0}
        self.lbl_iny_total.configure(text="Inyecciones: 0 negativos | 0 ciclos")
        
        # Resetear cuadros de cantidad (desbloquear y limpiar)
        self.entry_qty_neg.configure(state="normal")
        self.entry_qty_ciclo.configure(state="normal")
        self.entry_qty_neg.delete(0, "end")
        self.entry_qty_ciclo.delete(0, "end")
        
        self.actualizar_lienzo()
        self.actualizar_tabla_desde_grafo()
        self.lbl_status_iny.configure(text="🧹 Pesos restaurados a valores positivos", text_color="#666")
        self.after(3000, lambda: self.lbl_status_iny.configure(text=""))

    def confirmar_grafo(self): 
        if not self.grafo and not (isinstance(self.grafo, dict) and self.grafo.get("__is_stress_matrix__")):
            self.show_modal("Error", "No hay un grafo cargado.")
            return
        
        self.btn_confirmar.grid_forget()
        self.btn_ejecutar.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        self.btn_modificar.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        self.cambiar_estado("BLOQUEADO")

    def acc_modificar(self):
        """Desbloquea los campos para editar parámetros y limpia la vista previa."""
        # 1. OCULTAR TODO DE INMEDIATO PARA RESPUESTA INSTANTÁNEA
        self.f_middle.pack_forget()
        self.panel_visualizacion.pack_forget()
        self.panel_res.pack_forget()
        if hasattr(self, 'panel_monitor'): self.panel_monitor.pack_forget()
        self.f_flow_footer.pack_forget() 
        self.f_footer_res.pack_forget() 
        self.btn_limpiar.pack_forget()
        self.lbl_status_iny.pack_forget()
        
        # 2. Resetear datos
        self.grafo = None
        self.cambiar_estado("EDITABLE")
        self.bloquear_configuracion(False)
        self.inyecciones = {"negativos": 0, "ciclos": 0}
        self.lbl_status_iny.configure(text="")
        
        # Resetear cuadros de cantidad
        self.entry_qty_neg.configure(state="normal")
        self.entry_qty_ciclo.configure(state="normal")
        self.entry_qty_neg.delete(0, "end")
        self.entry_qty_ciclo.delete(0, "end")
        
        # Limpiar controles de flujo
        self.btn_confirmar.grid_forget()
        self.btn_ejecutar.grid_forget()
        self.btn_modificar.grid_forget()

        # 3. FORZAR REFRESCO DE VENTANA Y SCROLL
        self.update_idletasks()
        try: self.main_container._parent_canvas.yview_moveto(0.0)
        except: pass
        
        # Ocultar herramientas de inyección
        self.f_iny.grid_remove() 
        self.btn_limpiar.grid_remove()
        
        # Forzar scroll al inicio para que el usuario vea la tarjeta de parámetros inmediatamente
        self.update_idletasks()
        self.main_container._parent_canvas.yview_moveto(0.0)

    def acc_nueva_prueba(self):
        """Limpia todo y regresa a la vista inicial (solo entrada de nodos)."""
        self.acc_modificar()
        
        # Limpiar entrada de nodos y disparar actualización por defecto
        self.entry_nodos.delete(0, "end")
        self.entry_densidad.delete(0, "end")
        self.lbl_hint_densidad.configure(text="")
        
        # Resetear contadores de inyección
        self.lbl_iny_total.configure(text="Inyecciones: 0 negativos | 0 ciclos")
        self.actualizar_nodos_defecto()
        
        # Resetear semilla interna por defecto
        self.seed = 42

    def acc_exportar(self):
        try:
            import tkinter.filedialog as fd

            filename = fd.asksaveasfilename(
                title="Guardar reporte PDF",
                defaultextension=".pdf",
                filetypes=[("Archivo PDF", "*.pdf")],
                initialfile="Reporte_Benchmarking.pdf"
            )
            if not filename:
                return  # El usuario canceló el diálogo

            res = self.resultados_actuales
            t_d = res['dijkstra']['tiempo_promedio_ms']
            t_b = res['bellman_ford']['tiempo_promedio_ms']

            # Texto de velocidad
            if t_d > 0 and t_b > 0:
                winner = "Dijkstra" if t_d < t_b else "Bellman-Ford"
                perc = (abs(t_d - t_b) / max(t_d, t_b)) * 100
                insight_speed = f"{winner} fue un {perc:.1f}% más rápido en este escenario"
            else:
                insight_speed = ""

            # Extraer costo de ruta y ciclo
            salida_d  = res['dijkstra']['salida']
            salida_bf = res['bellman_ford']['salida']
            stats_d   = salida_d[0]  if isinstance(salida_d,  (tuple, list)) else salida_d
            stats_bf  = salida_bf[0] if isinstance(salida_bf, (tuple, list)) else salida_bf
            d_val     = stats_d.get("dist_target", "inf")
            bf_val    = stats_bf.get("dist_target", "inf")
            has_cycle = salida_bf[2] if isinstance(salida_bf, (tuple, list)) and len(salida_bf) > 2 else False

            # Texto del insight pedagógico (sin emojis para PDF limpio)
            try:
                d_num  = float(d_val)  if str(d_val).replace('.','').replace('-','').isdigit()  else float('inf')
                bf_num = float(bf_val) if str(bf_val).replace('.','').replace('-','').isdigit() else float('inf')
            except:
                d_num = bf_num = float('inf')

            if has_cycle:
                insight_cost = "Ciclo negativo detectado: Dijkstra es invalido en este caso. Bellman-Ford detecto la anomalia."
            elif abs(d_num - bf_num) > 0.1 and self.has_negativos():
                insight_cost = "Pesos negativos presentes: Dijkstra perdio precision. El resultado de Bellman-Ford es el correcto."
            elif d_num == bf_num and d_num != float('inf'):
                insight_cost = "Consistencia: ambos algoritmos coinciden en el costo de ruta. Dijkstra fue mas rapido."
            else:
                insight_cost = "Bellman-Ford es preferible para validar grafos con pesos negativos."

            params = {
                "nodos":       self.entry_nodos.get(),
                "densidad":    self.entry_densidad.get(),
                "source":      str(self.entry_source.get()).split()[0],
                "target":      str(self.entry_target.get()).split()[0],
                "seed":        self.seed,
                "iny_neg":     self.inyecciones.get("negativos", 0),
                "iny_ciclo":   self.inyecciones.get("ciclos", 0),
                "t_d":         t_d,
                "t_b":         t_b,
                "m_d":         res['dijkstra']['memoria_pico_kb'],
                "m_b":         res['bellman_ford']['memoria_pico_kb'],
                "d_val":       d_val,
                "bf_val":      bf_val,
                "has_cycle":   has_cycle,
                "insight_speed": insight_speed,
                "insight_cost":  insight_cost,
            }

            exportar_pdf(res, params, filename)
            self.show_modal("Reporte guardado", f"Archivo guardado en:\n{filename}", SUCCESS_COLOR)

        except Exception as e:
            import traceback
            self.show_modal("Error al exportar", f"{str(e)}")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    ctk.set_appearance_mode("light")
    BenchmarkingUI().mainloop()
