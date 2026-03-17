"""
collectors/social_listener.py
Social listening usando Claude API + web_search tool.

Por cada query definida en config.py:
1. Envía la query a Claude con web_search habilitado
2. Claude busca, lee resultados y extrae menciones estructuradas
3. Agrega todo en un corpus de insights

Output: lista de mentions con texto, fuente, sentimiento, temas.
"""

import os
import json
import time
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SEARCH_QUERIES, KAVAK_CONTEXT


ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Prompt base para extracción de menciones
EXTRACTION_PROMPT = """Sos un analista de brand intelligence para Kavak México.

Contexto sobre Kavak:
{kavak_context}

Tu tarea: buscar en internet menciones, comentarios, reviews y opiniones sobre Kavak México 
relacionadas con la siguiente búsqueda: "{query}"

Instrucciones:
1. Busca la query en la web
2. Analiza los resultados que encuentres (reviews, comentarios, foros, redes sociales, artículos)
3. Extrae menciones concretas y reales que encuentres

Para cada mención encontrada, responde ÚNICAMENTE con un JSON array con esta estructura:
[
  {{
    "fuente": "Twitter/Reddit/Google Reviews/YouTube/Foros/Noticias/etc",
    "url": "URL si está disponible, sino null",
    "texto": "Cita o paráfrasis del comentario/mención (máx 200 caracteres)",
    "sentimiento": "positivo|negativo|neutro|mixto",
    "temas": ["tema1", "tema2"],  // De: precio, confianza, proceso, garantía, servicio, variedad, financiamiento, entrega, postventa, comparativa
    "intensidad": 1-5,  // 1=débil, 5=muy fuerte
    "fecha_aprox": "2024-Q1|2024-Q2|2024-Q3|2024-Q4|2025-Q1|2025-Q2|desconocida"
  }}
]

Si no encontrás menciones relevantes, devolvé un array vacío: []
Responde SOLO el JSON, sin texto adicional ni markdown.
"""


def run_social_listening(
    queries: Optional[list] = None,
    max_queries: int = 20,
    delay_between_queries: float = 2.0,
    cache_file: str = "outputs/social_listening_cache.json",
) -> list:
    """
    Ejecuta social listening para todas (o un subconjunto de) queries.
    
    Args:
        queries: lista de queries custom (default: usa ALL_QUERIES de config)
        max_queries: límite para no quemar tokens en dev
        delay_between_queries: segundos entre llamadas (rate limiting)
        cache_file: si existe, carga cache en vez de volver a correr
    
    Returns:
        Lista de menciones agregadas de todas las queries
    """
    try:
        import anthropic
    except ImportError:
        print("[Social Listener] anthropic no instalado. Corriendo: pip install anthropic")
        return []

    if not ANTHROPIC_API_KEY:
        print("[Social Listener] ⚠️  ANTHROPIC_API_KEY no seteada en environment.")
        print("   Setear con: export ANTHROPIC_API_KEY='sk-ant-...'")
        return []

    # Cargar cache si existe y es reciente (< 24h)
    cache = _load_cache(cache_file)
    if cache:
        print(f"[Social Listener] Cache cargado: {len(cache)} menciones")
        return cache

    # Construir lista de queries
    if queries is None:
        all_q = [q for qs in SEARCH_QUERIES.values() for q in qs]
        queries = all_q[:max_queries]

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    all_mentions = []

    print(f"[Social Listener] Iniciando {len(queries)} búsquedas...")

    for i, query in enumerate(queries, 1):
        print(f"  [{i}/{len(queries)}] Buscando: {query}")
        mentions = _search_single_query(client, query)
        all_mentions.extend(mentions)
        print(f"    → {len(mentions)} menciones encontradas")

        if i < len(queries):
            time.sleep(delay_between_queries)

    print(f"\n[Social Listener] Total menciones: {len(all_mentions)}")

    # Guardar cache
    _save_cache(all_mentions, cache_file)

    return all_mentions


def _search_single_query(client, query: str) -> list:
    """
    Llama a Claude con web_search para una sola query.
    Returns lista de mentions parseadas.
    """
    try:
        prompt = EXTRACTION_PROMPT.format(
            kavak_context=KAVAK_CONTEXT,
            query=query,
        )

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        # Extraer texto de la respuesta
        full_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                full_text += block.text

        if not full_text.strip():
            return []

        # Parsear JSON
        mentions = _parse_mentions_json(full_text)
        # Agregar la query de origen
        for m in mentions:
            m["query_origen"] = query

        return mentions

    except Exception as e:
        print(f"    ✗ Error en query '{query}': {e}")
        return []


def _parse_mentions_json(text: str) -> list:
    """Parsea el JSON de menciones de forma resiliente."""
    # Limpiar markdown fences si los hay
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text

    # Intentar parsear directo
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Buscar array JSON dentro del texto
    import re
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return []


def aggregate_insights(mentions: list) -> dict:
    """
    Agrega menciones en insights resumidos.
    
    Returns dict con:
    - sentiment_distribution: % por sentimiento
    - top_themes: temas más mencionados
    - by_source: menciones por fuente
    - verbatims_by_sentiment: selección de verbatims
    - negative_clusters: clusters de quejas
    - positive_clusters: clusters de elogios
    """
    if not mentions:
        return {
            "total_mentions": 0,
            "sentiment_distribution": {},
            "top_themes": [],
            "by_source": {},
            "verbatims": {"positivo": [], "negativo": [], "mixto": []},
            "negative_clusters": [],
            "positive_clusters": [],
        }

    from collections import Counter

    # Sentimiento
    sentiments = [m.get("sentimiento", "neutro") for m in mentions]
    sentiment_counts = Counter(sentiments)
    total = len(mentions)
    sentiment_dist = {k: round(v / total * 100, 1) for k, v in sentiment_counts.items()}

    # Temas
    all_themes = [t for m in mentions for t in m.get("temas", [])]
    theme_counts = Counter(all_themes)
    top_themes = [{"tema": t, "count": c, "pct": round(c / total * 100, 1)}
                  for t, c in theme_counts.most_common(10)]

    # Por fuente
    sources = Counter(m.get("fuente", "unknown") for m in mentions)
    by_source = dict(sources.most_common())

    # Verbatims por sentimiento (top 5 de cada uno por intensidad)
    verbatims = {"positivo": [], "negativo": [], "mixto": [], "neutro": []}
    for sentiment in verbatims:
        filtered = [m for m in mentions if m.get("sentimiento") == sentiment]
        filtered.sort(key=lambda x: x.get("intensidad", 0), reverse=True)
        verbatims[sentiment] = filtered[:8]

    # Clusters negativos (temas más frecuentes en menciones negativas)
    negative_mentions = [m for m in mentions if m.get("sentimiento") == "negativo"]
    neg_themes = Counter([t for m in negative_mentions for t in m.get("temas", [])])
    negative_clusters = [{"tema": t, "count": c} for t, c in neg_themes.most_common(5)]

    # Clusters positivos
    positive_mentions = [m for m in mentions if m.get("sentimiento") == "positivo"]
    pos_themes = Counter([t for m in positive_mentions for t in m.get("temas", [])])
    positive_clusters = [{"tema": t, "count": c} for t, c in pos_themes.most_common(5)]

    return {
        "total_mentions": total,
        "sentiment_distribution": sentiment_dist,
        "top_themes": top_themes,
        "by_source": by_source,
        "verbatims": verbatims,
        "negative_clusters": negative_clusters,
        "positive_clusters": positive_clusters,
        "raw_mentions": mentions,
    }


def get_social_summary_for_llm(aggregated: dict) -> str:
    """
    Convierte los insights agregados a texto para el LLM analyzer.
    """
    if not aggregated or aggregated.get("total_mentions", 0) == 0:
        return "No hay datos de social listening disponibles."

    lines = ["=== SOCIAL LISTENING DATA ===\n"]
    lines.append(f"Total menciones analizadas: {aggregated['total_mentions']}")

    # Sentimiento
    sd = aggregated.get("sentiment_distribution", {})
    lines.append("\nDISTRIBUCIÓN DE SENTIMIENTO:")
    for sentiment, pct in sorted(sd.items(), key=lambda x: -x[1]):
        lines.append(f"  • {sentiment}: {pct}%")

    # Top themes
    lines.append("\nTEMAS MÁS MENCIONADOS:")
    for t in aggregated.get("top_themes", [])[:7]:
        lines.append(f"  • {t['tema']}: {t['count']} menciones ({t['pct']}%)")

    # Clusters negativos
    lines.append("\nCLUSTERS DE QUEJAS/PROBLEMAS:")
    for c in aggregated.get("negative_clusters", []):
        lines.append(f"  • {c['tema']}: {c['count']} menciones negativas")

    # Clusters positivos
    lines.append("\nCLUSTERS DE ELOGIOS/DIFERENCIADORES:")
    for c in aggregated.get("positive_clusters", []):
        lines.append(f"  • {c['tema']}: {c['count']} menciones positivas")

    # Sample verbatims negativos (los más intensos)
    neg_verbs = aggregated.get("verbatims", {}).get("negativo", [])
    if neg_verbs:
        lines.append("\nVERBATIMS NEGATIVOS (muestra):")
        for v in neg_verbs[:5]:
            lines.append(f'  [{v.get("fuente", "?")}] "{v.get("texto", "")}"')

    pos_verbs = aggregated.get("verbatims", {}).get("positivo", [])
    if pos_verbs:
        lines.append("\nVERBATIMS POSITIVOS (muestra):")
        for v in pos_verbs[:5]:
            lines.append(f'  [{v.get("fuente", "?")}] "{v.get("texto", "")}"')

    return "\n".join(lines)


def _load_cache(cache_file: str) -> list:
    """Carga cache si existe y fue generado hace menos de 24 horas."""
    import time as time_module
    cache_path = Path(cache_file)
    if not cache_path.exists():
        return []

    # Verificar antigüedad
    mtime = cache_path.stat().st_mtime
    age_hours = (time_module.time() - mtime) / 3600
    if age_hours > 24:
        print(f"[Social Listener] Cache expirado ({age_hours:.1f}h). Volviendo a correr.")
        return []

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_cache(mentions: list, cache_file: str) -> None:
    """Guarda menciones en cache."""
    cache_path = Path(cache_file)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(mentions, f, ensure_ascii=False, indent=2)
        print(f"[Social Listener] Cache guardado: {cache_file}")
    except Exception as e:
        print(f"[Social Listener] No se pudo guardar cache: {e}")
