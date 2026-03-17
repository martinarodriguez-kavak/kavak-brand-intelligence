"""
config.py — Kavak Brand Health Dashboard
Centraliza queries de social listening, levers de Growth,
y estructura esperada del BHT.
"""

# ──────────────────────────────────────────────
# SOCIAL LISTENING QUERIES
# Organizadas por tema para búsquedas estructuradas
# ──────────────────────────────────────────────
SEARCH_QUERIES = {
    "experiencia_general": [
        "Kavak México opiniones 2025",
        "Kavak comprar auto usado experiencia",
        "Kavak vender auto experiencia cliente",
        "Kavak México confiable site:reddit.com",
        "Kavak review Google Maps",
    ],
    "percepcion_precio": [
        "Kavak caro precio autos usados México",
        "Kavak precio vs mercado",
        "Kavak precios justos opiniones",
    ],
    "confianza_credibilidad": [
        "Kavak fraude estafa México",
        "Kavak fraude Twitter",
        "Kavak confiable garantía experiencia",
        "Kavak certificado verificación autos",
    ],
    "proceso_compra": [
        "Kavak proceso compra autos fácil difícil",
        "Kavak crédito auto financiamiento opiniones",
        "Kavak Kavak Crédito experiencia",
        "Kavak entrega tiempo demora",
    ],
    "competencia": [
        "Kavak vs Seminuevos opiniones",
        "Kavak vs Mercado Libre autos",
        "alternativas Kavak México autos usados",
    ],
    "contenido_social": [
        "Kavak México Instagram comentarios",
        "Kavak México TikTok viral",
        "Kavak México YouTube reseña",
    ],
}

# Todas las queries en lista plana para el runner
ALL_QUERIES = [q for queries in SEARCH_QUERIES.values() for q in queries]

# ──────────────────────────────────────────────
# LEVERS DE GROWTH / MARKETING
# Solo estos son accionables para el equipo
# ──────────────────────────────────────────────
GROWTH_LEVERS = {
    "mensajería_y_propuesta_de_valor": {
        "description": "Ajustar qué comunicamos y cómo posicionamos la marca",
        "examples": ["reformular el claim de precio", "destacar garantía", "comunicar proceso"],
    },
    "contenido_y_creativos": {
        "description": "Qué producir, en qué tono, qué temas abordar",
        "examples": ["UGC de experiencias positivas", "contenido educativo proceso", "testimoniales"],
    },
    "awareness_y_alcance": {
        "description": "Aumentar cobertura y frecuencia de marca",
        "examples": ["campañas upper funnel", "reach en nuevas audiencias", "OOH"],
    },
    "consideracion_y_enganche": {
        "description": "Mover intención de compra",
        "examples": ["retargeting con propuesta de valor", "contenido de consideración", "comparativos"],
    },
    "confianza_y_prueba_social": {
        "description": "Generar credibilidad y reducir fricción percibida",
        "examples": ["reviews y testimoniales", "certificaciones visibles", "casos de éxito"],
    },
    "precio_como_comunicacion": {
        "description": "No podemos mover precios, pero SÍ podemos comunicar valor",
        "examples": ["comparativa costo-beneficio", "financiamiento como solución", "transparencia de precio"],
        "note": "Lever de comunicación, no de pricing. Enmarcar el precio en contexto de valor.",
    },
}

# Temas que NO son palancas de Growth
NON_GROWTH_LEVERS = [
    "operaciones",
    "taller mecánico",
    "tiempo de inspección",
    "staffing",
    "logística de entrega interna",
    "política de precios",
]

# ──────────────────────────────────────────────
# ESTRUCTURA ESPERADA DEL BHT
# Columnas mínimas que debe tener cada archivo CSV/Excel
# ──────────────────────────────────────────────
BHT_REQUIRED_COLUMNS = [
    "ola",          # número o fecha de la ola
    "metrica",      # nombre del KPI (ej: "Top of Mind", "Awareness", "NPS")
    "valor",        # valor numérico
    "segmento",     # total / género / NSE / edad (opcional)
    "mercado",      # CDMX / MTY / GDL / Nacional
]

BHT_METRICS_CATALOG = {
    "funnel": ["Top of Mind", "Awareness Espontáneo", "Awareness Asistido",
               "Consideración", "Compra Reciente", "Preferencia"],
    "percepcion": ["Precio Justo", "Confianza", "Calidad Percibida",
                   "Facilidad de Proceso", "Garantía", "Variedad"],
    "nps": ["NPS", "Recomendaría", "Satisfacción General"],
    "competencia": ["Share of Mind", "Preferencia vs Competencia"],
}

# ──────────────────────────────────────────────
# KAVAK CONTEXT (para el prompt del analyzer)
# ──────────────────────────────────────────────
KAVAK_CONTEXT = """
Kavak es el marketplace de autos usados certificados líder en LATAM y GCC.
Opera en México, Brasil, Argentina, Colombia, Chile, Turquía, UAE y otros mercados.

PROPUESTA DE VALOR CORE:
- Autos usados certificados con garantía
- Proceso de compra/venta 100% digital
- Precios fijos (sin regateo)
- Financiamiento propio (Kavak Capital / Kuna Capital en MX)

EQUIPO DE GROWTH / ONLINE BRANDING trabaja en:
- Google Ads, Meta Ads, TikTok Ads
- Campañas de branding upper funnel
- Contenido de marca y consideración

LO QUE NO CONTROLAMOS:
- Precio de los autos (decisión de negocio/revenue)
- Operaciones del taller / mecánicos
- Tiempos logísticos de entrega
- Políticas de devolución (en su mayoría)

MERCADO PRINCIPAL: México (CDMX, MTY, GDL, QRO, etc.)
"""

# ──────────────────────────────────────────────
# DASHBOARD CONFIG
# ──────────────────────────────────────────────
DASHBOARD_CONFIG = {
    "title": "Kavak Brand Intelligence",
    "subtitle": "Brand Health + Social Listening + Accionables",
    "primary_color": "#0057FF",
    "secondary_color": "#000000",
    "font": "Helvetica Neue, Helvetica, Arial, sans-serif",
    "refresh_interval_hours": 24,
}
