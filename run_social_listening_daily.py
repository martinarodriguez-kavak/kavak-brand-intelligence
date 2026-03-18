#!/usr/bin/env python3
"""
run_social_listening_daily.py
─────────────────────────────
Herramienta propia de Social Listening de Kavak.

Modo de uso:
  python run_social_listening_daily.py                   # busca menciones de ayer
  python run_social_listening_daily.py --fecha 2026-03-17  # fecha específica
  python run_social_listening_daily.py --reset           # descarta acumulado y arranca de cero

Qué hace:
  1. Inyecta la fecha objetivo en queries multi-plataforma
  2. Llama a Claude API con web_search para cada query
  3. Extrae menciones estructuradas (JSON)
  4. Deduplica contra el cache existente
  5. Acumula (rolling 90 días) y guarda
  6. Imprime resumen de ejecución

Usado por el GitHub Action diario y también manualmente.
"""

import argparse
import json
import os
import sys
import time
import hashlib
from datetime import date, timedelta
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────────

CACHE_FILE     = Path("outputs/social_listening_cache.json")
MAX_DAYS_KEEP  = 90          # rolling window: descarta menciones de >90 días
DELAY_SECS     = 3.0         # segundos entre llamadas a la API (rate limiting)
MODEL          = "claude-opus-4-6"

KAVAK_CONTEXT = """
Kavak es el marketplace líder de autos usados certificados en LATAM y GCC.
Opera en México, Brasil, Argentina, Chile, Turquía, UAE y otros mercados.
Productos: compra/venta de autos, Kavak Crédito (financiamiento), garantía 3-12 meses.
Canales digitales: Instagram @kavak.com (263K), TikTok, YouTube, X/Twitter @KavakMexico.
"""

# Templates de queries — {fecha} se reemplaza por la fecha objetivo (ej: "18 de marzo de 2026")
# {fecha_iso} se reemplaza por "2026-03-18"
QUERY_TEMPLATES = [
    # Redes sociales generales
    "Kavak México {fecha} opiniones",
    "Kavak {fecha} experiencia compra",
    "Kavak {fecha} vender auto",
    "@KavakMexico {fecha}",

    # Plataformas específicas
    "Kavak TikTok {fecha}",
    "Kavak Instagram comentarios {fecha}",
    "Kavak YouTube reseña {fecha}",
    "Kavak Twitter {fecha}",
    "Kavak Threads {fecha}",

    # Temas críticos (monitoreo de riesgo)
    "Kavak queja garantía {fecha}",
    "Kavak fraude estafa {fecha}",
    "Kavak documentos tardanza {fecha}",
    "Kavak precio bait switch {fecha}",

    # Temas positivos / producto
    "Kavak experiencia positiva {fecha}",
    "Kavak Crédito {fecha}",
    "Kavak noticias {fecha_iso}",

    # Queries de "ayer" / recientes (sin fecha explícita para capturar lo más nuevo)
    "Kavak México ayer opiniones",
    "Kavak reciente queja",
    "\"kavak.com\" review {fecha_iso}",
    "Kavak México últimas 24 horas",
]

EXTRACTION_PROMPT = """Sos un analista de social listening para Kavak México.

Contexto sobre Kavak:
{kavak_context}

Fecha objetivo: {fecha_larga} (busca menciones de ESTE día específicamente, o las más recientes si no hay de ese día exacto).

Tu tarea: buscar en internet menciones, comentarios, reviews y opiniones sobre Kavak México
relacionadas con: "{query}"

Busca en: Twitter/X, TikTok, Instagram, Facebook, YouTube, Reddit, foros, reviews, noticias.

Para CADA mención real encontrada, incluí en el JSON:
[
  {{
    "fuente": "Twitter/X | TikTok | Instagram | Facebook | YouTube | Reddit | Foros | Noticias | Trustpilot | Google Reviews",
    "plataforma_normalizada": "twitter | tiktok | instagram | facebook | youtube | reddit | foros | medios | reviews",
    "url": "URL completa si está disponible, sino null",
    "texto": "Cita textual o paráfrasis fiel del comentario (máx 250 caracteres)",
    "autor": "Handle o nombre si es visible, sino null",
    "sentimiento": "positivo | negativo | neutro | mixto",
    "temas": ["precio", "confianza", "proceso", "garantía", "servicio", "variedad", "financiamiento", "entrega", "postventa", "comparativa"],
    "intensidad": 1,
    "fecha_mencion": "YYYY-MM-DD si la conocés, sino null",
    "fecha_aprox": "2026-Q1"
  }}
]

Reglas:
- Solo menciones REALES que encontraste en la búsqueda, no ejemplos inventados
- Si no encontrás ninguna mención relevante: devolvé []
- "intensidad" va de 1 (mención débil/neutral) a 5 (queja viral o elogio fuerte)
- Responde SOLO el JSON array, sin markdown ni texto extra
"""


# ── Lógica principal ───────────────────────────────────────────────────────────

def build_queries(fecha_obj: date) -> list[str]:
    """Genera queries con la fecha inyectada."""
    meses_es = ["enero","febrero","marzo","abril","mayo","junio",
                 "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    fecha_larga = f"{fecha_obj.day} de {meses_es[fecha_obj.month - 1]} de {fecha_obj.year}"
    fecha_iso   = fecha_obj.strftime("%Y-%m-%d")

    queries = []
    for tpl in QUERY_TEMPLATES:
        q = tpl.replace("{fecha}", fecha_larga).replace("{fecha_iso}", fecha_iso)
        queries.append(q)
    return queries, fecha_larga


def fingerprint(mention: dict) -> str:
    """Hash único por texto para deduplicar."""
    key = (mention.get("texto", "") + mention.get("url", "") or "").lower().strip()[:150]
    return hashlib.md5(key.encode()).hexdigest()


def load_cache() -> list:
    if not CACHE_FILE.exists():
        return []
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Cache] Error al cargar: {e}")
        return []


def save_cache(mentions: list) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(mentions, f, ensure_ascii=False, indent=2)


def trim_old_mentions(mentions: list, max_days: int) -> list:
    """Descarta menciones con fetch_date más antiguo que max_days."""
    from datetime import datetime
    cutoff = date.today() - timedelta(days=max_days)
    kept, dropped = [], 0
    for m in mentions:
        fd = m.get("fetch_date")
        if fd:
            try:
                if date.fromisoformat(fd) >= cutoff:
                    kept.append(m)
                    continue
            except ValueError:
                pass
        kept.append(m)  # si no tiene fecha, conservar
    dropped = len(mentions) - len(kept)
    if dropped:
        print(f"[Trim] Descartadas {dropped} menciones con más de {max_days} días")
    return kept


def search_query(client, query: str, fecha_larga: str) -> list:
    """Llama a Claude con web_search y extrae menciones."""
    try:
        prompt = EXTRACTION_PROMPT.format(
            kavak_context=KAVAK_CONTEXT,
            fecha_larga=fecha_larga,
            query=query,
        )
        response = client.messages.create(
            model=MODEL,
            max_tokens=2500,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )
        full_text = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )
        if not full_text.strip():
            return []
        return _parse_json(full_text)
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return []


def _parse_json(text: str) -> list:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    import re
    m = re.search(r'\[.*\]', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return []


def run(fecha_obj: date, reset: bool = False) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("❌  ANTHROPIC_API_KEY no seteada.")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("❌  pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    queries, fecha_larga = build_queries(fecha_obj)
    fetch_date = date.today().isoformat()

    print(f"\n{'='*60}")
    print(f"  KAVAK SOCIAL LISTENING — {fecha_larga}")
    print(f"  {len(queries)} queries | modelo: {MODEL}")
    print(f"{'='*60}\n")

    # Cargar cache existente
    existing = [] if reset else load_cache()
    existing_fps = {fingerprint(m) for m in existing}
    print(f"[Cache] {len(existing)} menciones existentes cargadas")

    # Buscar
    new_mentions = []
    for i, query in enumerate(queries, 1):
        print(f"  [{i:02d}/{len(queries)}] {query}")
        results = search_query(client, query, fecha_larga)

        added = 0
        for m in results:
            m["query_origen"] = query
            m["fetch_date"]   = fetch_date
            fp = fingerprint(m)
            if fp not in existing_fps:
                existing_fps.add(fp)
                new_mentions.append(m)
                added += 1

        print(f"         → {len(results)} encontradas | {added} nuevas")

        if i < len(queries):
            time.sleep(DELAY_SECS)

    # Combinar, trim y guardar
    all_mentions = existing + new_mentions
    all_mentions = trim_old_mentions(all_mentions, MAX_DAYS_KEEP)
    save_cache(all_mentions)

    print(f"\n{'='*60}")
    print(f"  RESUMEN")
    print(f"  Nuevas menciones hoy:  {len(new_mentions)}")
    print(f"  Total acumulado:       {len(all_mentions)}")
    print(f"  Cache guardado en:     {CACHE_FILE}")
    print(f"{'='*60}\n")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kavak Social Listening — runner diario")
    parser.add_argument("--fecha", type=str, default="",
                        help="Fecha objetivo YYYY-MM-DD (default: ayer)")
    parser.add_argument("--reset", action="store_true",
                        help="Descarta cache acumulado y arranca de cero")
    args = parser.parse_args()

    # Soporte para variable de entorno del GitHub Action
    fecha_env = os.environ.get("FECHA_OBJETIVO", "").strip()
    fecha_str = args.fecha or fecha_env

    if fecha_str:
        try:
            fecha_obj = date.fromisoformat(fecha_str)
        except ValueError:
            print(f"❌  Formato de fecha inválido: {fecha_str}. Usá YYYY-MM-DD")
            sys.exit(1)
    else:
        fecha_obj = date.today() - timedelta(days=1)

    run(fecha_obj, reset=args.reset)
