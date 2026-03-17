"""
analyzer.py
Synthesizer principal: toma BHT + social listening y genera
insights consolidados + accionables filtrados para Growth/Content.

Usa Claude API (sin web_search, puro reasoning sobre datos).
"""

import os
import json
from typing import Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from config import KAVAK_CONTEXT, GROWTH_LEVERS, NON_GROWTH_LEVERS

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ──────────────────────────────────────────────
# PROMPTS
# ──────────────────────────────────────────────

SYNTHESIS_PROMPT = """Sos un estratega de Brand & Growth para Kavak México.

CONTEXTO KAVAK:
{kavak_context}

PALANCAS DE GROWTH DISPONIBLES (solo estas son accionables para el equipo):
{growth_levers}

TEMAS QUE NO SON PALANCAS DE GROWTH (ignorar para accionables):
{non_levers}

---
DATOS DISPONIBLES:

{bht_summary}

---

{social_summary}

---

Con base en toda esta información, generá un análisis completo. 
Responde ÚNICAMENTE con un JSON con esta estructura exacta:

{{
  "executive_summary": "Párrafo de 3-4 oraciones con el estado de marca actual. Qué está funcionando, qué está en riesgo.",
  
  "brand_health_insights": [
    {{
      "metrica": "nombre del KPI",
      "tendencia": "creciendo|estable|cayendo|sin_dato",
      "magnitud": "alta|media|baja",
      "interpretacion": "qué significa este dato para la marca",
      "urgencia": "alta|media|baja"
    }}
  ],
  
  "social_insights": [
    {{
      "tema": "nombre del tema",
      "sentimiento_neto": "positivo|negativo|mixto",
      "frecuencia": "alta|media|baja",
      "narrativa": "qué está diciendo la gente exactamente sobre este tema",
      "oportunidad_o_riesgo": "oportunidad|riesgo|neutral"
    }}
  ],
  
  "brechas_detectadas": [
    {{
      "brecha": "descripción de la brecha entre percepción y realidad, o entre lo que comunicamos y lo que entiende el usuario",
      "evidencia_bht": "dato del BHT que lo confirma (si aplica)",
      "evidencia_social": "verbatim o dato de social que lo confirma (si aplica)",
      "impacto": "alto|medio|bajo"
    }}
  ],
  
  "accionables_growth": [
    {{
      "titulo": "nombre corto del accionable (máx 8 palabras)",
      "lever": "mensajería_y_propuesta_de_valor|contenido_y_creativos|awareness_y_alcance|consideracion_y_enganche|confianza_y_prueba_social|precio_como_comunicacion",
      "descripcion": "qué hacer exactamente, de forma concreta",
      "hipotesis": "si hacemos X, esperamos Y porque Z",
      "canales_sugeridos": ["Meta Ads", "TikTok", "Google Ads", "Orgánico", "OOH"],
      "formato_sugerido": ["Video", "Carrusel", "Stories", "Static", "Search"],
      "prioridad": "alta|media|baja",
      "evidencia": "qué dato del BHT o social listening justifica este accionable",
      "kpi_de_exito": "cómo medimos si funcionó",
      "timeline_sugerido": "inmediato (< 2 semanas)|corto plazo (1 mes)|mediano plazo (1-3 meses)"
    }}
  ],
  
  "temas_excluidos": [
    {{
      "tema": "nombre del tema",
      "razon_exclusion": "por qué no generamos accionable (ej: es decisión de pricing, es operaciones)",
      "mencion_frecuencia": "alta|media|baja",
      "recomendacion_para_otras_areas": "si aplica, a qué área escalar"
    }}
  ]
}}

IMPORTANTE:
- Los accionables deben ser CONCRETOS y ejecutables por el equipo de Growth/Marketing.
- NO incluir accionables de operaciones, precios, mecánicos, logística.
- Para el precio: si es una queja frecuente, el accionable debe ser de COMUNICACIÓN (cómo encuadrar el precio como valor), no de bajar precios.
- Mínimo 5 accionables, máximo 12.
- Priorizar accionables de contenido y mensajería donde haya mayor gap percepción/realidad.
- Responder SOLO el JSON, sin texto adicional.
"""


# ──────────────────────────────────────────────
# MAIN ANALYZER
# ──────────────────────────────────────────────

def run_analysis(
    bht_summary: str,
    social_summary: str,
    cache_file: str = "outputs/analysis_cache.json",
    force_refresh: bool = False,
) -> dict:
    """
    Genera el análisis completo usando Claude.
    
    Args:
        bht_summary: texto con datos BHT (de bht_loader.get_bht_summary_for_llm)
        social_summary: texto con insights de social (de social_listener.get_social_summary_for_llm)
        cache_file: dónde guardar el resultado
        force_refresh: si True, no usa cache
    
    Returns:
        dict con el análisis completo
    """
    try:
        import anthropic
    except ImportError:
        print("[Analyzer] anthropic no instalado.")
        return _empty_analysis()

    if not ANTHROPIC_API_KEY:
        print("[Analyzer] ⚠️  ANTHROPIC_API_KEY no seteada.")
        return _empty_analysis()

    # Cache
    if not force_refresh:
        cached = _load_cache(cache_file)
        if cached:
            print(f"[Analyzer] Cache cargado.")
            return cached

    print("[Analyzer] Generando análisis con Claude...")

    # Formatear levers para el prompt
    levers_text = "\n".join(
        f"- {k}: {v['description']}"
        for k, v in GROWTH_LEVERS.items()
    )
    non_levers_text = ", ".join(NON_GROWTH_LEVERS)

    prompt = SYNTHESIS_PROMPT.format(
        kavak_context=KAVAK_CONTEXT,
        growth_levers=levers_text,
        non_levers=non_levers_text,
        bht_summary=bht_summary,
        social_summary=social_summary,
    )

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text
        analysis = _parse_analysis_json(text)

        if analysis:
            _save_cache(analysis, cache_file)
            print(f"[Analyzer] ✓ Análisis generado:")
            print(f"  - {len(analysis.get('brand_health_insights', []))} brand health insights")
            print(f"  - {len(analysis.get('social_insights', []))} social insights")
            print(f"  - {len(analysis.get('accionables_growth', []))} accionables de growth")
            return analysis
        else:
            print("[Analyzer] ✗ No se pudo parsear el análisis.")
            return _empty_analysis()

    except Exception as e:
        print(f"[Analyzer] ✗ Error: {e}")
        return _empty_analysis()


def _parse_analysis_json(text: str) -> Optional[dict]:
    """Parsea el JSON del análisis de forma resiliente."""
    text = text.strip()

    # Limpiar markdown
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Buscar objeto JSON
    import re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _empty_analysis() -> dict:
    """Retorna estructura vacía para no romper el dashboard."""
    return {
        "executive_summary": "No hay datos suficientes para generar un análisis.",
        "brand_health_insights": [],
        "social_insights": [],
        "brechas_detectadas": [],
        "accionables_growth": [],
        "temas_excluidos": [],
    }


def _load_cache(cache_file: str) -> Optional[dict]:
    """Carga cache si existe y tiene menos de 12 horas."""
    import time as time_module
    cache_path = Path(cache_file)
    if not cache_path.exists():
        return None

    mtime = cache_path.stat().st_mtime
    age_hours = (time_module.time() - mtime) / 3600
    if age_hours > 12:
        return None

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(data: dict, cache_file: str) -> None:
    cache_path = Path(cache_file)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Analyzer] Cache guardado: {cache_file}")


# ──────────────────────────────────────────────
# UTILS PARA EL DASHBOARD
# ──────────────────────────────────────────────

def get_actionables_by_lever(analysis: dict) -> dict:
    """Agrupa accionables por lever para mostrar en tabs del dashboard."""
    actionables = analysis.get("accionables_growth", [])
    by_lever = {}
    for a in actionables:
        lever = a.get("lever", "sin_categorizar")
        if lever not in by_lever:
            by_lever[lever] = []
        by_lever[lever].append(a)
    return by_lever


def get_priority_actionables(analysis: dict, priority: str = "alta") -> list:
    """Filtra accionables por prioridad."""
    return [
        a for a in analysis.get("accionables_growth", [])
        if a.get("prioridad") == priority
    ]


def get_insight_score(analysis: dict) -> dict:
    """
    Genera un 'score' de brand health para el header del dashboard.
    Basado en tendencias positivas vs negativas.
    """
    insights = analysis.get("brand_health_insights", [])
    if not insights:
        return {"score": None, "label": "Sin datos", "color": "gray"}

    positive = sum(1 for i in insights if i.get("tendencia") == "creciendo")
    negative = sum(1 for i in insights if i.get("tendencia") == "cayendo")
    total = len(insights)

    score = round((positive / total * 100) if total > 0 else 50)

    if score >= 60:
        return {"score": score, "label": "Positivo", "color": "#22C55E"}
    elif score >= 40:
        return {"score": score, "label": "Estable", "color": "#F59E0B"}
    else:
        return {"score": score, "label": "Atención requerida", "color": "#EF4444"}
