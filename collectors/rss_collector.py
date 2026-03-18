"""
collectors/rss_collector.py
───────────────────────────
Free-tier social listening collector for Kavak México.
No API key required — uses only Google News RSS and Reddit RSS feeds.

Dependencies (stdlib only + feedparser):
    pip install feedparser

Exported functions:
    run_rss_collection(cache_file, max_per_query) -> list
    fetch_google_news(query, max_items)           -> list
    fetch_reddit_rss(subreddit, query, max_items) -> list
"""

import hashlib
import json
import re
import time
import urllib.parse
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional

# ── Sentinel so callers know feedparser is missing ──────────────────────────
try:
    import feedparser  # type: ignore
    _FEEDPARSER_OK = True
except ImportError:
    _FEEDPARSER_OK = False

# ── Configuration ────────────────────────────────────────────────────────────

MAX_DAYS_KEEP = 90      # rolling window: drop mentions older than this
REQUEST_DELAY = 1.5     # seconds between HTTP requests (be a good citizen)

# ── Google News RSS queries (15+) ────────────────────────────────────────────
# Each item: (display_name, query_string_for_URL)

GOOGLE_NEWS_QUERIES: list[tuple[str, str]] = [
    ("Kavak México opiniones",         "Kavak México opiniones"),
    ("Kavak fraude estafa",            "Kavak fraude estafa México"),
    ("Kavak queja Profeco",            "Kavak queja Profeco"),
    ("Kavak garantía problemas",       "Kavak garantía problema"),
    ("Kavak crédito financiamiento",   "Kavak crédito financiamiento"),
    ("Kavak experiencia compra",       "Kavak experiencia comprar auto"),
    ("Kavak TikTok viral",             "Kavak TikTok"),
    ("Kavak reseña confiable",         "Kavak reseña confiable"),
    ("Kavak precio engaño",            "Kavak precio engaño sobreprecio"),
    ("Kavak entrega demora",           "Kavak entrega tardanza retraso"),
    ("Kavak serie F inversión",        "Kavak serie F inversión financiamiento"),
    ("Kavak devolución",               "Kavak devolución dinero"),
    ("Kavak taller postventa",         "Kavak taller servicio postventa"),
    ("Kavak denuncia",                 "Kavak denuncia fraude México"),
    ("Kavak Trustpilot reseña",        "Kavak Trustpilot review"),
    ("Kavak noticias recientes",       "Kavak México noticias"),
    ("Kavak Total Crédito",            "Kavak Total Kavak Crédito opinión"),
    ("Kavak caro cobro extra",         "Kavak caro cobro adicional"),
    ("Kavak experiencia positiva",     "Kavak excelente experiencia recomiendo"),
    ("Kavak patrocinio contenido",     "Kavak patrocinio publicidad"),
]

# ── Reddit RSS targets ───────────────────────────────────────────────────────
# Tuples: (subreddit, search_query)

REDDIT_TARGETS: list[tuple[str, str]] = [
    ("mexico",          "kavak"),
    ("MexicoCity",      "kavak"),
    ("personalfinance", "kavak"),
    ("mexico",          "Kavak autos usados"),
    ("mexico",          "Kavak fraude"),
]

# ── Sentiment keyword lists ──────────────────────────────────────────────────

NEGATIVE_KEYWORDS = [
    "fraude", "estafa", "queja", "pésimo", "terrible", "engaño", "devolución",
    "demora", "garantía negada", "taller", "problema", "denuncia", "profeco",
    "caro", "cobro", "tardanza", "retraso", "mal servicio", "decepcionante",
    "robaron", "mentira", "incumplimiento", "no recomiendo", "pesimo",
    "horrible", "defecto", "falla", "negligencia", "abuso", "odio",
]

POSITIVE_KEYWORDS = [
    "recomiendo", "excelente", "rápido", "fácil", "profesional",
    "buena experiencia", "serie F", "inversión", "rentabilidad", "patrocinio",
    "genial", "increíble", "recomendable", "satisfecho", "confiable",
    "transparente", "rápido", "sin problemas", "feliz", "gracias",
    "lo mejor", "5 estrellas", "muy bueno", "eficiente", "puntual",
]


# ── Quarter helper ───────────────────────────────────────────────────────────

def _to_quarter(d: Optional[date]) -> str:
    """Convert a date to a quarter string like '2026-Q1', or 'desconocida'."""
    if d is None:
        return "desconocida"
    q = (d.month - 1) // 3 + 1
    return f"{d.year}-Q{q}"


# ── Date parsing ─────────────────────────────────────────────────────────────

def _parse_rss_date(entry) -> Optional[date]:
    """
    Try to extract a date from a feedparser entry.
    Tries: published_parsed, updated_parsed, published (raw string).
    Returns a date object or None.
    """
    # feedparser gives us a time.struct_time in *_parsed fields
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return date(val.tm_year, val.tm_mon, val.tm_mday)
            except (ValueError, AttributeError):
                pass

    # Fallback: parse the raw published string with email.utils
    raw = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if raw:
        try:
            dt = parsedate_to_datetime(raw)
            return dt.date()
        except Exception:
            pass

    return None


# ── Sentiment detection ──────────────────────────────────────────────────────

def _detect_sentiment(text: str) -> str:
    """
    Basic keyword-based sentiment detection.
    Returns: 'positivo' | 'negativo' | 'neutro' | 'mixto'
    """
    text_lower = text.lower()
    neg = any(kw in text_lower for kw in NEGATIVE_KEYWORDS)
    pos = any(kw in text_lower for kw in POSITIVE_KEYWORDS)

    if neg and pos:
        return "mixto"
    if neg:
        return "negativo"
    if pos:
        return "positivo"
    return "neutro"


def _detect_intensity(text: str, sentiment: str) -> int:
    """
    Heuristic intensity score 1-5.
    Counts matching keywords and maps to scale.
    """
    text_lower = text.lower()
    if sentiment == "negativo":
        matches = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    elif sentiment == "positivo":
        matches = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    else:
        return 1

    if matches >= 5:
        return 5
    if matches >= 3:
        return 4
    if matches == 2:
        return 3
    if matches == 1:
        return 2
    return 1


def _detect_themes(text: str) -> list[str]:
    """Keyword-based topic tagging."""
    text_lower = text.lower()
    themes = []

    THEME_KEYWORDS = {
        "precio":         ["precio", "caro", "barato", "cobro", "costo", "tarifa", "sobrepr"],
        "confianza":      ["fraude", "estafa", "engaño", "confianza", "honesto", "transparente",
                           "denuncia", "profeco", "mentira"],
        "proceso":        ["proceso", "trámite", "documentos", "papeleo", "gestión", "burocracia",
                           "tardanza", "demora", "retraso"],
        "garantía":       ["garantía", "garantia", "falla", "defecto", "reparación", "taller"],
        "servicio":       ["servicio", "atención", "asesor", "empleado", "staff", "ejecutivo"],
        "variedad":       ["catálogo", "variedad", "selección", "opciones", "inventario", "auto"],
        "financiamiento": ["crédito", "credito", "financiamiento", "préstamo", "mensualidad",
                           "tasa", "kavak crédito", "kavak total"],
        "entrega":        ["entrega", "domicilio", "recoger", "recolección", "envío"],
        "postventa":      ["postventa", "taller", "mantenimiento", "seguimiento", "soporte"],
        "comparativa":    ["comparar", "vs", "versus", "mejor que", "peor que", "seminuevo",
                           "usado", "segunda mano"],
    }

    for theme, keywords in THEME_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            themes.append(theme)

    return themes if themes else ["general"]


# ── Fingerprint / deduplication ──────────────────────────────────────────────

def _fingerprint(mention: dict) -> str:
    """MD5 hash for deduplication — same logic as run_social_listening_daily.py."""
    key = (
        (mention.get("texto") or "") + (mention.get("url") or "")
    ).lower().strip()[:150]
    return hashlib.md5(key.encode()).hexdigest()


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _load_cache(cache_file: str) -> list:
    path = Path(cache_file)
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[RSS] Warning: no se pudo cargar el cache ({e})")
        return []


def _save_cache(mentions: list, cache_file: str) -> None:
    path = Path(cache_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mentions, f, ensure_ascii=False, indent=2)


def _trim_old_mentions(mentions: list, max_days: int = MAX_DAYS_KEEP) -> list:
    """Drop entries whose fetch_date is older than max_days."""
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
        kept.append(m)  # no fecha → conservar
        continue
    dropped = len(mentions) - len(kept)
    if dropped:
        print(f"[RSS] Trim: {dropped} menciones descartadas (>{ max_days} días)")
    return kept


# ── Google News RSS fetcher ──────────────────────────────────────────────────

def fetch_google_news(query: str, max_items: int = 10) -> list:
    """
    Fetch items from the Google News RSS feed for *query*.

    Args:
        query:     Human-readable query string.
        max_items: Maximum number of items to return.

    Returns:
        List of mention dicts matching the required schema.
    """
    if not _FEEDPARSER_OK:
        print("[RSS] feedparser not installed. Run: pip install feedparser")
        return []

    encoded = urllib.parse.quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=es-419&gl=MX&ceid=MX:es-419"

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"[RSS] Google News error for '{query}': {e}")
        return []

    fetch_date = date.today().isoformat()
    results = []

    for entry in feed.entries[:max_items]:
        title = getattr(entry, "title", "") or ""
        summary = getattr(entry, "summary", "") or ""
        link = getattr(entry, "link", None)
        author = getattr(entry, "author", None)

        # Prefer summary if substantially longer, else title
        raw_text = summary if len(summary) > len(title) else title
        # Strip HTML tags from summary
        raw_text = re.sub(r"<[^>]+>", " ", raw_text).strip()
        texto = raw_text[:250]

        if not texto:
            continue

        entry_date = _parse_rss_date(entry)
        sentimiento = _detect_sentiment(texto)
        themes = _detect_themes(texto)
        intensity = _detect_intensity(texto, sentimiento)

        mention = {
            "fuente":                "Google News",
            "plataforma_normalizada": "medios",
            "url":                   link,
            "texto":                 texto,
            "autor":                 author if author else None,
            "sentimiento":           sentimiento,
            "temas":                 themes,
            "intensidad":            intensity,
            "fecha_mencion":         entry_date.isoformat() if entry_date else None,
            "fecha_aprox":           _to_quarter(entry_date),
            "fetch_date":            fetch_date,
            "query_origen":          query,
        }
        results.append(mention)

    return results


# ── Reddit RSS fetcher ───────────────────────────────────────────────────────

def fetch_reddit_rss(
    query: str,
    subreddit: str = "all",
    max_items: int = 10,
) -> list:
    """
    Fetch items from a Reddit RSS search feed.

    Reddit supports two URL patterns:
      - Subreddit search: /r/{sub}/search.rss?q={query}&restrict_sr=1&sort=new
      - Sitewide search:  /search.rss?q={query}&sort=new

    Args:
        query:     Search term (e.g. "kavak").
        subreddit: Subreddit name or "all" for sitewide.
        max_items: Maximum number of items to return.

    Returns:
        List of mention dicts matching the required schema.
    """
    if not _FEEDPARSER_OK:
        print("[RSS] feedparser not installed. Run: pip install feedparser")
        return []

    encoded = urllib.parse.quote_plus(query)
    if subreddit and subreddit.lower() != "all":
        url = (
            f"https://www.reddit.com/r/{subreddit}/search.rss"
            f"?q={encoded}&restrict_sr=1&sort=new&limit={max_items}"
        )
    else:
        url = f"https://www.reddit.com/search.rss?q={encoded}&sort=new&limit={max_items}"

    try:
        # Reddit blocks default user agents; provide a descriptive one
        feed = feedparser.parse(
            url,
            request_headers={"User-Agent": "KavakSocialListening/1.0 (monitoring bot)"},
        )
    except Exception as e:
        print(f"[RSS] Reddit error for r/{subreddit} '{query}': {e}")
        return []

    fetch_date = date.today().isoformat()
    query_label = f"reddit:r/{subreddit}:{query}"
    results = []

    for entry in feed.entries[:max_items]:
        title = getattr(entry, "title", "") or ""
        summary = getattr(entry, "summary", "") or ""
        link = getattr(entry, "link", None)
        author = getattr(entry, "author", None)

        raw_text = summary if len(summary) > len(title) else title
        raw_text = re.sub(r"<[^>]+>", " ", raw_text).strip()
        texto = raw_text[:250]

        if not texto:
            continue

        entry_date = _parse_rss_date(entry)
        sentimiento = _detect_sentiment(texto)
        themes = _detect_themes(texto)
        intensity = _detect_intensity(texto, sentimiento)

        mention = {
            "fuente":                "Reddit",
            "plataforma_normalizada": "reddit",
            "url":                   link,
            "texto":                 texto,
            "autor":                 author if author else None,
            "sentimiento":           sentimiento,
            "temas":                 themes,
            "intensidad":            intensity,
            "fecha_mencion":         entry_date.isoformat() if entry_date else None,
            "fecha_aprox":           _to_quarter(entry_date),
            "fetch_date":            fetch_date,
            "query_origen":          query_label,
        }
        results.append(mention)

    return results


# ── Main entry point ─────────────────────────────────────────────────────────

def run_rss_collection(
    cache_file: str = "outputs/social_listening_cache.json",
    max_per_query: int = 10,
) -> list:
    """
    Main entry point for the free RSS-based social listening collector.

    1. Loads the existing cache from *cache_file*.
    2. Runs all Google News queries and Reddit searches.
    3. Deduplicates new mentions against the existing cache (MD5 fingerprint).
    4. Appends new mentions, trims to a rolling 90-day window.
    5. Saves back to *cache_file* and returns the full updated list.

    Args:
        cache_file:    Path to the JSON cache (relative to cwd or absolute).
        max_per_query: Maximum RSS items to fetch per query.

    Returns:
        Full updated list of mentions (existing + new).
    """
    if not _FEEDPARSER_OK:
        print(
            "[RSS] ERROR: feedparser is not installed.\n"
            "       Install it with:  pip install feedparser\n"
            "       Then re-run this script."
        )
        return []

    print("\n" + "=" * 60)
    print("  KAVAK RSS SOCIAL LISTENING")
    print(
        f"  {len(GOOGLE_NEWS_QUERIES)} Google News queries"
        f" + {len(REDDIT_TARGETS)} Reddit feeds"
    )
    print("=" * 60 + "\n")

    # Load existing cache
    existing = _load_cache(cache_file)
    existing_fps: set[str] = {_fingerprint(m) for m in existing}
    print(f"[Cache] {len(existing)} menciones existentes cargadas\n")

    new_mentions: list[dict] = []
    fetch_date = date.today().isoformat()

    # ── Google News ──────────────────────────────────────────────────────────
    print("--- Google News RSS ---")
    for idx, (label, query) in enumerate(GOOGLE_NEWS_QUERIES, 1):
        print(f"  [{idx:02d}/{len(GOOGLE_NEWS_QUERIES)}] {label}")
        items = fetch_google_news(query, max_items=max_per_query)

        added = 0
        for m in items:
            fp = _fingerprint(m)
            if fp not in existing_fps:
                existing_fps.add(fp)
                new_mentions.append(m)
                added += 1

        print(f"         → {len(items)} obtenidas | {added} nuevas")

        if idx < len(GOOGLE_NEWS_QUERIES):
            time.sleep(REQUEST_DELAY)

    # ── Reddit RSS ───────────────────────────────────────────────────────────
    print("\n--- Reddit RSS ---")
    for idx, (subreddit, query) in enumerate(REDDIT_TARGETS, 1):
        label = f"r/{subreddit} · '{query}'"
        print(f"  [{idx:02d}/{len(REDDIT_TARGETS)}] {label}")
        items = fetch_reddit_rss(query, subreddit=subreddit, max_items=max_per_query)

        added = 0
        for m in items:
            fp = _fingerprint(m)
            if fp not in existing_fps:
                existing_fps.add(fp)
                new_mentions.append(m)
                added += 1

        print(f"         → {len(items)} obtenidas | {added} nuevas")

        if idx < len(REDDIT_TARGETS):
            time.sleep(REQUEST_DELAY)

    # ── Merge, trim, save ────────────────────────────────────────────────────
    all_mentions = existing + new_mentions
    all_mentions = _trim_old_mentions(all_mentions, MAX_DAYS_KEEP)
    _save_cache(all_mentions, cache_file)

    print(f"\n{'='*60}")
    print("  RESUMEN RSS COLLECTION")
    print(f"  Nuevas menciones:  {len(new_mentions)}")
    print(f"  Total acumulado:   {len(all_mentions)}")
    print(f"  Cache guardado:    {cache_file}")
    print(f"{'='*60}\n")

    return all_mentions


# ── CLI usage ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Kavak RSS Social Listening — free collector, no API key required"
    )
    parser.add_argument(
        "--cache",
        default="outputs/social_listening_cache.json",
        help="Path to the JSON cache file (default: outputs/social_listening_cache.json)",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=10,
        help="Max items to fetch per RSS query (default: 10)",
    )
    args = parser.parse_args()

    run_rss_collection(cache_file=args.cache, max_per_query=args.max)
