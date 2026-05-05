import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# --- Paleta de colores (espeja la UI) ---
C_PRIMARY   = HexColor("#B39DDB")  # Morado pastel
C_DARK      = HexColor("#1A237E")  # Azul oscuro (títulos)
C_SUCCESS   = HexColor("#A5D6A7")  # Verde
C_ERROR     = HexColor("#EF9A9A")  # Rojo
C_WARNING   = HexColor("#FFE082")  # Amarillo
C_LIGHT     = HexColor("#F5F5F5")  # Gris claro
C_MID       = HexColor("#78909C")  # Gris medio
C_WHITE     = colors.white
C_BLACK     = colors.black

def exportar_json(data, filename="resultado.json"):
    """Guarda los resultados crudos en un archivo JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return filename

def exportar_pdf(data, params, filename="Reporte_Benchmarking.pdf"):
    """
    Genera un reporte PDF de UNA PÁGINA en portrait con:
      - Parámetros del grafo (sin tabla de adyacencia ni dibujo)
      - Análisis comparativo de rendimiento
    params dict keys:
        nodos, densidad, source, target, seed,
        iny_neg, iny_ciclo,
        t_d, t_b, m_d, m_b,
        d_val, bf_val, has_cycle,
        insight_speed, insight_cost
    """
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        topMargin=36, bottomMargin=36,
        leftMargin=45, rightMargin=45
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=18,
        textColor=C_DARK,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=C_MID,
        spaceAfter=2,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=C_DARK,
        spaceBefore=10,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )
    insight_style = ParagraphStyle(
        "Insight",
        parent=styles["Normal"],
        fontSize=10,
        textColor=C_MID,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=0,
    )
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=C_MID,
        alignment=TA_CENTER,
    )

    elements = []
    usable_w = letter[0] - 90  # 612 - 90 margen = 522 pt

    # ── ENCABEZADO ──────────────────────────────────────────────────────────
    elements.append(Paragraph("Reporte de Benchmarking", title_style))
    elements.append(Paragraph("Dijkstra vs. Bellman-Ford", title_style))
    fecha = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
    elements.append(Paragraph(f"Generado el {fecha}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=C_PRIMARY, spaceAfter=10))

    # ── SECCIÓN 1: PARÁMETROS DEL GRAFO ─────────────────────────────────────
    elements.append(Paragraph("1. Parámetros del grafo", section_style))

    col_w = usable_w / 5
    param_data = [
        ["Nodos", "Densidad", "Nodo origen", "Nodo destino", "Semilla"],
        [
            str(params["nodos"]),
            str(params["densidad"]),
            str(params["source"]),
            str(params["target"]),
            str(params["seed"]),
        ]
    ]
    param_table = Table(param_data, colWidths=[col_w] * 5)
    param_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), C_PRIMARY),
        ("TEXTCOLOR",    (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_LIGHT]),
        ("GRID",         (0, 0), (-1, -1), 0.5, C_MID),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    elements.append(param_table)
    elements.append(Spacer(1, 6))

    # Inyecciones
    iny_neg  = params.get("iny_neg", 0)
    iny_ciclo = params.get("iny_ciclo", 0)
    iny_text = (
        f"Pesos negativos inyectados: <b>{iny_neg}</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Ciclos negativos inyectados: <b>{iny_ciclo}</b>"
    )
    elements.append(Paragraph(iny_text, ParagraphStyle(
        "Iny", parent=styles["Normal"], fontSize=9,
        textColor=C_MID, alignment=TA_CENTER, spaceAfter=0
    )))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=C_PRIMARY, spaceBefore=10, spaceAfter=6))

    # ── SECCIÓN 2: ANÁLISIS COMPARATIVO ──────────────────────────────────────
    elements.append(Paragraph("2. Análisis comparativo de rendimiento", section_style))

    t_d  = params["t_d"]
    t_b  = params["t_b"]
    m_d  = params["m_d"]
    m_b  = params["m_b"]
    d_val  = params["d_val"]
    bf_val = params["bf_val"]

    # Formateadores
    def fmt_val(v):
        try:
            return f"{float(v):.0f}" if float(v) != float('inf') else "∞"
        except:
            return str(v)

    winner_d = t_d > 0 and t_d <= t_b
    winner_b = t_b > 0 and t_b < t_d

    col_labels = ["Algoritmo", "Tiempo (ms)", "Memoria (KB)", "Complejidad", "Costo de ruta"]
    col_widths  = [100, 90, 90, 110, 90]

    def row_style(is_winner, has_cycle_row=False):
        if has_cycle_row:
            return C_ERROR
        if is_winner:
            return C_SUCCESS
        return C_LIGHT

    has_cycle = params.get("has_cycle", False)

    results_data = [
        col_labels,
        [
            "Dijkstra",
            f"{t_d:.4f}",
            f"{m_d:.2f}",
            "O((V+E) log V)",
            fmt_val(d_val),
        ],
        [
            "Bellman-Ford",
            f"{t_b:.4f}",
            f"{m_b:.2f}",
            "O(V × E)",
            fmt_val(bf_val),
        ],
    ]

    res_table = Table(results_data, colWidths=col_widths)
    res_table.setStyle(TableStyle([
        # Cabecera
        ("BACKGROUND",    (0, 0), (-1, 0), C_DARK),
        ("TEXTCOLOR",     (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        # Fila Dijkstra
        ("BACKGROUND",    (0, 1), (-1, 1), row_style(winner_d)),
        # Fila Bellman-Ford
        ("BACKGROUND",    (0, 2), (-1, 2), row_style(winner_b, has_cycle)),
        # General
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",          (0, 0), (-1, -1), 0.5, C_MID),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
    ]))
    elements.append(res_table)
    elements.append(Spacer(1, 10))

    # Interpretación de velocidad
    if params.get("insight_speed"):
        elements.append(Paragraph(f"⏱ {params['insight_speed']}", insight_style))

    # Insight pedagógico
    if params.get("insight_cost"):
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(params["insight_cost"], insight_style))

    # ── FOOTER ───────────────────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=0.5, color=C_PRIMARY, spaceBefore=14, spaceAfter=6))
    elements.append(Paragraph(
        "Plataforma de benchmarking: Dijkstra versus Bellman-Ford  ·  Proyecto Integrador — Lenguajes y Autómatas II",
        footer_style
    ))

    doc.build(elements)
    return filename
