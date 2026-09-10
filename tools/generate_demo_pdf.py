from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).parents[1]
data = json.loads((ROOT / "examples" / "planta_andina_input.json").read_text(encoding="utf-8"))
result = json.loads((ROOT / "examples" / "planta_andina_resultado_esperado.json").read_text(encoding="utf-8"))
out = ROOT / "output" / "pdf" / "SUR18_DEMO_001_R01.pdf"
out.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleSur", parent=styles["Title"], textColor=colors.HexColor("#0B5D3B"), fontSize=24, leading=30))
styles.add(ParagraphStyle(name="HeadingSur", parent=styles["Heading2"], textColor=colors.HexColor("#0B5D3B"), spaceBefore=8, spaceAfter=6))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11))

def p(text, style="BodyText"):
    return Paragraph(str(text), styles[style])

def table(rows, widths=(55*mm, 115*mm)):
    t = Table([[p(a, "Small"), p(b, "Small")] for a, b in rows], colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#E7F2EC")),
        ("GRID", (0,0), (-1,-1), .25, colors.HexColor("#B9D5C5")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    return t

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#0B5D3B"))
    canvas.line(15*mm, 13*mm, 195*mm, 13*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#456052"))
    canvas.drawString(15*mm, 8*mm, "SUR18 Solar Designer - Confidencial - Diseño preliminar")
    canvas.drawRightString(195*mm, 8*mm, "Página %d" % doc.page)
    canvas.restoreState()

story = [
    p("SUR18 SOLAR DESIGNER", "TitleSur"), p("Reporte técnico de proyecto fotovoltaico C&I", "Heading2"),
    Spacer(1, 5*mm), p("PLANTA ANDINA - COCHABAMBA", "HeadingSur"),
    table([("Código", "SUR18-DEMO-001"), ("Cliente", "Industria Andina S.R.L."),
           ("Ubicación", "Parque Industrial, Cochabamba, Bolivia"),
           ("Coordenadas", "-17.3935000, -66.1570000"), ("Estado", "Piloto - Revisión 1")]),
    Spacer(1, 6*mm), p("Resumen ejecutivo", "HeadingSur"),
    table([("Potencia instalada", "220.00 kWp DC / 200.00 kW AC"),
           ("Energía anual estimada", "351,780 kWh/año"), ("Cobertura de demanda", "73.29 %"),
           ("Configuración", "400 módulos de 550 Wp; 20 strings; 2 inversores")]),
    Spacer(1, 8*mm), p("Este informe resume un dimensionamiento preliminar. La ingeniería de detalle requiere verificación estructural, estudio de sombras, protecciones y normativa aplicable.", "Small"),
    PageBreak(),
    p("Diseño eléctrico", "TitleSur"),
    table([("Módulo", "550 Wp | Voc 49.9 V | Vmp 41.8 V | Isc 13.98 A"),
           ("String", "20 módulos por string | 20 strings en total"),
           ("Inversores", "2 x 100 kW AC"), ("Relación DC/AC", "1.10"),
           ("Voc por frío", "1,067.93 V (límite del inversor: 1,100 V)"),
           ("Vmp por calor", "870.32 V (ventana MPPT: 200 a 1,000 V)")]),
    Spacer(1, 5*mm), p("Criterios de validación", "HeadingSur"),
    p("La longitud del string se determinó verificando la tensión de circuito abierto a temperatura mínima y la tensión de máxima potencia a temperatura máxima. El resultado debe confirmarse con la ficha técnica vigente de equipos seleccionados.", "BodyText"),
    Spacer(1, 8*mm), p("Advertencias de ingeniería", "HeadingSur"),
    table([("Pendiente", "Confirmar corrientes por MPPT, fusibles, seccionamiento DC/AC y capacidad de cortocircuito."),
           ("Pendiente", "Confirmar pérdidas por sombras, suciedad, temperatura, degradación y clipping.")]),
    PageBreak(),
    p("Implantación y ubicación", "TitleSur"),
    table([("Área disponible", "3,500 m²"), ("Área de módulos", "1,032.00 m²"),
           ("Área bruta estimada", "1,962.00 m²"), ("GCR de diseño", "0.55"),
           ("Disposición", "20 filas x 20 columnas"), ("Pasillo entre filas", "0.60 m")]),
    Spacer(1, 6*mm), p("Croquis de matriz de módulos", "HeadingSur"),
]
grid = [["M" for _ in range(20)] for _ in range(20)]
g = Table(grid, colWidths=7*mm, rowHeights=5.2*mm)
g.setStyle(TableStyle([("GRID", (0,0), (-1,-1), .25, colors.white), ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#3F9B70")),
                       ("TEXTCOLOR", (0,0), (-1,-1), colors.white), ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
                       ("FONTSIZE", (0,0), (-1,-1), 5), ("ALIGN", (0,0), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
story += [g, Spacer(1, 5*mm), p("Google Earth", "HeadingSur"),
          p("Ubicación: https://earth.google.com/web/search/-17.3935,-66.1570. El software genera también un KML con el punto del proyecto.", "Small"),
          PageBreak(),
          p("Supuestos y trazabilidad", "TitleSur"),
          table([("Consumo anual de referencia", "480,000 kWh/año"), ("Irradiación anual", "2,050 kWh/m²-año"),
                 ("Performance ratio", "0.78"), ("Objetivo de cobertura", "70 %"),
                 ("Temperatura mínima / máxima", "0 °C / 65 °C"), ("Fecha de reporte", "10/09/2026")]),
          Spacer(1, 6*mm), p("Historial de revisiones", "HeadingSur"),
          table([("Revisión 1", "Piloto inicial - 220.00 kWp DC - 351,780 kWh/año - sur18_demo")]),
          Spacer(1, 6*mm), p("Descargo técnico", "HeadingSur"),
          p("Los resultados son una estimación para evaluación comercial e industrial. No sustituyen planos IFC, memorias de cálculo, revisión de red, estudio de sombras, aprobación de la distribuidora ni la validación de un profesional responsable.", "Small")]

SimpleDocTemplate(str(out), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=16*mm, bottomMargin=18*mm).build(story, onFirstPage=footer, onLaterPages=footer)
print(out)
