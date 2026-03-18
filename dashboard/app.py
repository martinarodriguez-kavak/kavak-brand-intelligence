"""
dashboard/app.py
Kavak Brand Intelligence Dashboard — Consumer Centric
"""

import os
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

st.set_page_config(
    page_title="Consumer Perception Tracker",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# DESIGN SYSTEM — Kavak (Online Branding ref)
# ──────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  :root {
    --kavak-blue: #0467FC;
    --kavak-blue-dark: #0352C9;
    --kavak-blue-light: #E8F1FF;
    --kavak-lime: #C5E50B;
    --bg: #F5F7FA;
    --card: #FFFFFF;
    --border: #E2E8F0;
    --text: #1A202C;
    --text-muted: #718096;
    --text-light: #A0AEC0;
    --green: #38A169;
    --green-bg: #F0FFF4;
    --yellow: #D69E2E;
    --yellow-bg: #FFFFF0;
    --red: #E53E3E;
    --red-bg: #FFF5F5;
    --purple: #805AD5;
    --purple-bg: #FAF5FF;
  }

  html, body, [class*="css"] {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    background: var(--bg) !important;
  }

  /* Hide Streamlit chrome */
  header[data-testid="stHeader"] { display: none !important; }
  #MainMenu { visibility: hidden !important; }
  footer { visibility: hidden !important; }
  .main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
  }

  /* ─── NAVBAR ─── */
  .navbar {
    background: var(--kavak-blue);
    color: white;
    padding: 0 32px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 8px rgba(4,103,252,0.2);
    position: sticky;
    top: 0;
    z-index: 100;
    margin-bottom: 0;
  }
  .navbar-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 15px;
    font-weight: 600;
  }
  .kavak-wordmark {
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
  }
  .navbar-divider {
    width: 1px;
    height: 20px;
    background: rgba(255,255,255,0.3);
  }
  .navbar-title {
    font-size: 14px;
    font-weight: 500;
    opacity: 0.85;
  }
  .navbar-meta {
    display: flex;
    gap: 12px;
    align-items: center;
    font-size: 12px;
    opacity: 0.85;
  }
  .period-badge {
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.3px;
  }
  .api-badge-off {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    color: rgba(255,255,255,0.7);
  }

  /* ─── CONTAINER ─── */
  .container {
    max-width: 1440px;
    margin: 0 auto;
    padding: 24px 32px;
  }

  /* ─── SECTION HEADER ─── */
  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px;
    padding-bottom: 0;
  }
  .section-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--kavak-blue);
    flex-shrink: 0;
  }
  .section-dot.green { background: var(--green); }
  .section-dot.yellow { background: var(--yellow); }
  .section-dot.red { background: var(--red); }
  .section-dot.purple { background: var(--purple); }
  .section-title {
    font-size: 17px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.3px;
  }
  .section-count {
    background: var(--bg);
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 12px;
    margin-left: auto;
  }

  /* ─── KPI BLOCKS (reference: Meta Ads dashboard) ─── */
  .kpi-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 24px;
  }
  /* kpi-block base defined later, near button styles */
  .kpi-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--text-muted);
    margin-bottom: 5px;
  }
  .kpi-value {
    font-size: 22px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
    line-height: 1;
    margin-bottom: 4px;
  }
  .kpi-sub {
    font-size: 11px;
    color: var(--text-light);
    margin-top: 3px;
  }
  .kpi-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
    flex-shrink: 0;
  }
  .kpi-arrow {
    font-size: 9px;
    color: var(--text-light);
    transition: transform 0.2s ease;
    margin-top: 2px;
  }
  .kpi-block[open] .kpi-arrow { transform: rotate(180deg); }
  .kpi-detail {
    margin-top: 10px;
    border-top: 1px solid #E2E8F0;
    padding-top: 10px;
  }
  .kpi-detail-def {
    font-size: 11px;
    color: var(--text-muted);
    line-height: 1.55;
    margin-bottom: 8px;
  }
  .kpi-detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 3px 0;
    font-size: 11px;
    color: var(--text-muted);
  }
  .kpi-detail-label { flex: 1; }
  .kpi-detail-val {
    font-weight: 700;
    color: var(--text);
    text-align: right;
    min-width: 40px;
  }
  .kpi-section-label {
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #A0AEC0;
    margin: 8px 0 3px;
  }
  .delta-up   { color: var(--green); font-size: 11px; font-weight: 700; }
  .delta-down { color: var(--red);   font-size: 11px; font-weight: 700; }
  .delta-flat { color: var(--text-light); font-size: 11px; font-weight: 600; }

  /* KPI card visual */
  .kpi-block {
    flex: 0 0 auto;
    width: 100%;
    background: #F9FAFB;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 14px;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
    position: relative;
  }

  /* Transparent click-target button rendered BEFORE the card HTML */
  div[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    height: 95px !important;
    min-height: 0 !important;
    width: 100% !important;
    cursor: pointer !important;
    box-shadow: none !important;
    padding: 0 !important;
    color: transparent !important;
    font-size: 0 !important;
    line-height: 0 !important;
  }

  /* Card markdown: overlaid on the button via negative margin, passes clicks through */
  div[data-testid="stMarkdownContainer"]:has(.kpi-block) {
    pointer-events: none !important;
    margin-top: -95px !important;
    position: relative !important;
    z-index: 2 !important;
  }

  /* Hover: button receives it, card visual updates via sibling selector */
  div[data-testid="stButton"]:has(button:hover) ~ div[data-testid="stMarkdownContainer"] .kpi-block {
    background: #EBF2FF !important;
    border-color: var(--kavak-blue) !important;
    box-shadow: 0 2px 8px rgba(4,103,252,0.08) !important;
  }


  /* ─── INSIGHT / KPI CARDS (border-left) ─── */
  .kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--kavak-blue);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: box-shadow 0.15s;
  }
  .kpi-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
  .kpi-card.urgencia-alta { border-left-color: var(--red); }
  .kpi-card.urgencia-media { border-left-color: var(--yellow); }
  .kpi-card.urgencia-baja { border-left-color: var(--green); }
  .kpi-card.sentimiento-positivo { border-left-color: var(--green); }
  .kpi-card.sentimiento-negativo { border-left-color: var(--red); }
  .kpi-card.sentimiento-mixto { border-left-color: var(--purple); }
  .kpi-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }
  .kpi-card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    flex: 1;
  }
  .kpi-card-text {
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.55;
  }

  /* ─── TAG / BADGE ─── */
  .tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2px;
  }
  .tag-blue { background: var(--kavak-blue-light); color: var(--kavak-blue); }
  .tag-green { background: var(--green-bg); color: var(--green); }
  .tag-red { background: var(--red-bg); color: var(--red); }
  .tag-yellow { background: var(--yellow-bg); color: var(--yellow); }
  .tag-purple { background: var(--purple-bg); color: var(--purple); }
  .tag-gray { background: var(--bg); color: var(--text-muted); }
  .tag-alta { background: var(--red-bg); color: var(--red); }
  .tag-media { background: var(--yellow-bg); color: var(--yellow); }
  .tag-baja { background: var(--green-bg); color: var(--green); }

  /* ─── ACTIONABLE CARD ─── */
  .action-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
    border-left: 4px solid var(--kavak-blue);
    transition: box-shadow 0.15s;
  }
  .action-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
  .action-card.prioridad-alta { border-left-color: var(--red); }
  .action-card.prioridad-media { border-left-color: var(--yellow); }
  .action-card.prioridad-baja { border-left-color: var(--green); }
  .action-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 6px;
    letter-spacing: -0.2px;
  }
  .action-desc {
    font-size: 13px;
    color: #4A5568;
    line-height: 1.6;
    margin-bottom: 10px;
  }
  .action-hypothesis {
    background: var(--kavak-blue-light);
    border-radius: 8px;
    padding: 9px 13px;
    font-size: 12px;
    color: var(--kavak-blue);
    font-style: italic;
    line-height: 1.5;
    margin-bottom: 10px;
  }
  .action-meta {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    align-items: center;
    margin-top: 8px;
  }
  .action-footer {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    font-size: 12px;
    color: var(--text-muted);
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
  }
  .action-footer strong { color: var(--text); }

  /* ─── METRICS ROW (inside cards) ─── */
  .metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
    margin-top: 12px;
  }
  .metric-block {
    background: var(--bg);
    border-radius: 8px;
    padding: 10px 8px;
    text-align: center;
  }
  .metric-block .m-label {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    margin-bottom: 3px;
  }
  .metric-block .m-value {
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.3px;
  }

  /* ─── EXEC SUMMARY BANNER ─── */
  .exec-banner {
    background: linear-gradient(135deg, #0467FC 0%, #001D6C 100%);
    border-radius: 14px;
    padding: 24px 28px;
    margin-top: 8px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
  }
  .exec-banner::after {
    content: '';
    position: absolute;
    bottom: -40px; right: -40px;
    width: 140px; height: 140px;
    background: rgba(197,229,11,0.12);
    border-radius: 50%;
  }
  .exec-banner .e-eyebrow {
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--kavak-lime);
    margin-bottom: 10px;
  }
  .exec-banner .e-text {
    font-size: 14px;
    line-height: 1.7;
    color: rgba(255,255,255,0.85);
    max-width: 100%;
  }

  /* ─── EMPTY STATE ─── */
  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    margin: 12px 0;
  }
  .empty-state .e-icon { font-size: 44px; margin-bottom: 14px; }
  .empty-state h3 { font-size: 17px; font-weight: 700; color: var(--text); margin-bottom: 8px; }
  .empty-state p { font-size: 13px; line-height: 1.6; color: var(--text-muted); }

  /* ─── SUMMARY STAT CARDS ─── */
  .summary-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
  }
  .summary-card.highlight { border-left: 3px solid var(--kavak-blue); }
  .s-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .6px;
    color: var(--text-muted);
    margin-bottom: 6px;
  }
  .s-value {
    font-size: 24px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
    line-height: 1;
  }

  /* ─── VERBATIM ─── */
  .verbatim {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
    font-size: 13px;
    line-height: 1.6;
    color: #2D3748;
  }
  .verbatim.neg { border-left-color: var(--red); }
  .verbatim.pos { border-left-color: var(--green); }
  .verbatim.neu { border-left-color: var(--text-light); }
  .verbatim-text { margin-bottom: 10px; }
  .verbatim-footer {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .verbatim-source {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--bg);
    padding: 2px 8px;
    border-radius: 10px;
  }
  .verbatim-source a {
    color: var(--kavak-blue);
    text-decoration: none;
    font-weight: 600;
  }
  .verbatim-source a:hover { text-decoration: underline; }
  .verbatim-date {
    font-size: 11px;
    color: var(--text-light);
  }

  /* ─── TABS override ─── */
  .stTabs [data-baseweb="tab-list"] {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    margin-bottom: 8px !important;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    padding: 7px 18px !important;
    font-family: 'Helvetica Neue', sans-serif !important;
  }
  .stTabs [aria-selected="true"] {
    background: var(--kavak-blue) !important;
    color: white !important;
    font-weight: 600 !important;
  }

  /* ─── Kill Streamlit default table borders ─── */
  div[data-testid="stMarkdownContainer"] table,
  div[data-testid="stMarkdownContainer"] tbody,
  div[data-testid="stMarkdownContainer"] thead,
  div[data-testid="stMarkdownContainer"] tr,
  div[data-testid="stMarkdownContainer"] td,
  div[data-testid="stMarkdownContainer"] th {
    border: none !important;
    border-collapse: collapse !important;
    border-spacing: 0 !important;
    background: transparent !important;
  }

  /* hide top padding from streamlit */
  .block-container { padding-top: 0 !important; margin-top: 0 !important; }
  .block-container > div:first-child { padding-top: 0 !important; margin-top: 0 !important; }
  div[data-testid="stVerticalBlock"] > div:first-child { padding-top: 0 !important; margin-top: 0 !important; }
  div[data-testid="stVerticalBlock"] { gap: 0 !important; }
  section[data-testid="stAppViewContainer"] > div:first-child { padding-top: 0 !important; }
  div[data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
  div[data-testid="stMainBlockContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
  .main > div:first-child { padding-top: 0 !important; margin-top: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def load_all_data(force_refresh: bool = False):
    from collectors.bht_loader import load_bht_files, get_bht_summary_for_llm
    from analyzer import run_analysis

    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))

    all_waves = load_bht_files("data")
    bht_summary = get_bht_summary_for_llm(all_waves)

    mentions, aggregated_social, social_summary = [], {}, ""
    from collectors.social_listener import run_social_listening, aggregate_insights, get_social_summary_for_llm
    mentions = run_social_listening(max_queries=15, cache_file="outputs/social_listening_cache.json")
    aggregated_social = aggregate_insights(mentions)
    social_summary = get_social_summary_for_llm(aggregated_social)

    analysis = {}
    if has_api_key:
        analysis = run_analysis(bht_summary=bht_summary, social_summary=social_summary, force_refresh=force_refresh)

    return {"waves": all_waves, "mentions": mentions, "social": aggregated_social, "analysis": analysis}


# ──────────────────────────────────────────────
# HELPER RENDERERS
# ──────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_logo_html() -> str:
    import base64, io
    from PIL import Image
    logo_path = Path(__file__).parent / "static" / "kavak_logo.png"
    if not logo_path.exists():
        logo_path = Path(__file__).parent.parent.parent / "KAVAK_LOGO_MAIN_WHITE (3).png"
    if logo_path.exists():
        img = Image.open(logo_path).convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f'<img src="data:image/png;base64,{b64}" style="height:30px;width:auto;display:block;" />'
    return '<span class="kavak-wordmark">KAVAK</span>'


@st.cache_data(ttl=3600, show_spinner=False)
def load_bht_real() -> "pd.DataFrame | None":
    import pandas as pd
    csv_path = Path(__file__).parent.parent / "data" / "bht_kavak_mexico_W0-W9.csv"
    if not csv_path.exists():
        return None
    df = pd.read_csv(csv_path)
    # Handle both string "True" and boolean True
    mask = df["es_kavak"].astype(str).str.strip().str.lower() == "true"
    return df[mask].copy()


def navbar(has_api_key: bool):
    import datetime
    import zoneinfo
    tz_mx = zoneinfo.ZoneInfo("America/Mexico_City")
    now = datetime.datetime.now(tz=tz_mx).strftime("%d %b %Y")
    api_badge = "" if has_api_key else '<span class="api-badge-off">⚠ Sin API key</span>'
    st.markdown(f"""
    <div class="navbar">
      <div class="navbar-brand">
        {get_logo_html()}
        <div class="navbar-divider"></div>
        <span class="navbar-title">Consumer Perception Tracker</span>
      </div>
      <div class="navbar-meta">
        {api_badge}
        <span class="period-badge">📅 {now}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, dot_color: str = "blue", count: int = None):
    count_html = f'<span class="section-count">{count}</span>' if count is not None else ""
    st.markdown(f"""
    <div class="section-header">
      <div class="section-dot {dot_color}"></div>
      <span class="section-title">{title}</span>
      {count_html}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(insight: dict, card_type: str = "brand"):
    if card_type == "brand":
        urgencia = insight.get("urgencia", "baja")
        tend = insight.get("tendencia", "estable")
        icon = "↑" if tend == "creciendo" else "↓" if tend == "cayendo" else "→"
        tend_tag = f'<span class="tag tag-green">↑ creciendo</span>' if tend == "creciendo" else \
                   f'<span class="tag tag-red">↓ cayendo</span>' if tend == "cayendo" else \
                   f'<span class="tag tag-gray">→ estable</span>'
        urgencia_tag = f'<span class="tag tag-{urgencia}">{urgencia}</span>'
        st.markdown(f"""
        <div class="kpi-card urgencia-{urgencia}">
          <div class="kpi-card-header">
            <span class="kpi-card-title">{insight.get('metrica', '?')}</span>
            {tend_tag} {urgencia_tag}
          </div>
          <div class="kpi-card-text">{insight.get('interpretacion', '')}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        sent = insight.get("sentimiento_neto", "neutro")
        freq = insight.get("frecuencia", "")
        freq_tag = f'<span class="tag tag-gray">{freq}</span>' if freq else ""
        opr = insight.get("oportunidad_o_riesgo", "")
        opr_tag = f'<span class="tag tag-green">oportunidad</span>' if opr == "oportunidad" else \
                  f'<span class="tag tag-red">riesgo</span>' if opr == "riesgo" else ""
        st.markdown(f"""
        <div class="kpi-card sentimiento-{sent}">
          <div class="kpi-card-header">
            <span class="kpi-card-title">{insight.get('tema', '?')}</span>
            {freq_tag} {opr_tag}
          </div>
          <div class="kpi-card-text">{insight.get('narrativa', '')}</div>
        </div>
        """, unsafe_allow_html=True)


def render_actionable(action: dict):
    priority = action.get("prioridad", "media")
    lever = action.get("lever", "")
    lever_labels = {
        "mensajería_y_propuesta_de_valor": "💬 Mensajería",
        "contenido_y_creativos": "🎨 Contenido",
        "awareness_y_alcance": "📡 Awareness",
        "consideracion_y_enganche": "🎯 Consideración",
        "confianza_y_prueba_social": "✅ Confianza",
        "precio_como_comunicacion": "💰 Precio (comm.)",
    }
    lever_label = lever_labels.get(lever, lever.replace("_", " ").title())
    channels = " · ".join(action.get("canales_sugeridos", []))
    timeline = action.get("timeline_sugerido", "")
    kpi = action.get("kpi_de_exito", "")
    evidencia = action.get("evidencia", "")

    channels_html = f'<span class="tag tag-gray">📱 {channels}</span>' if channels else ""
    timeline_html = f'<span class="tag tag-purple">⏱ {timeline}</span>' if timeline else ""

    st.markdown(f"""
    <div class="action-card prioridad-{priority}">
      <div class="action-title">{action.get('titulo', 'Sin título')}</div>
      <div class="action-desc">{action.get('descripcion', '')}</div>
      <div class="action-hypothesis">💡 {action.get('hipotesis', '')}</div>
      <div class="action-meta">
        <span class="tag tag-blue">{lever_label}</span>
        <span class="tag tag-{priority}">Prioridad {priority.upper()}</span>
        {timeline_html}
        {channels_html}
      </div>
      <div class="action-footer">
        {'<span><strong>Evidencia:</strong> ' + evidencia + '</span>' if evidencia else ''}
        {'<span><strong>KPI:</strong> ' + kpi + '</span>' if kpi else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)


def empty_state(icon: str, title: str, body: str):
    st.markdown(f"""
    <div class="empty-state">
      <div class="e-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{body}</p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    navbar(has_api_key)

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown("### ⚙️ Controles")
        force_refresh = st.button("🔄 Actualizar datos", use_container_width=True, type="primary")
        st.divider()
        st.markdown("**Filtros — Accionables**")
        filter_priority = st.multiselect(
            "Prioridad",
            options=["alta", "media", "baja"],
            default=["alta", "media"],
        )
        filter_lever = st.multiselect(
            "Lever",
            options=[
                "mensajería_y_propuesta_de_valor",
                "contenido_y_creativos",
                "awareness_y_alcance",
                "consideracion_y_enganche",
                "confianza_y_prueba_social",
                "precio_como_comunicacion",
            ],
            default=[],
            format_func=lambda x: x.replace("_", " ").title(),
        )
        st.divider()
        if st.button("🗑️ Limpiar cache", use_container_width=True, type="primary"):
            for f in ["outputs/social_listening_cache.json", "outputs/analysis_cache.json"]:
                if Path(f).exists():
                    Path(f).unlink()
            st.cache_data.clear()
            st.success("Cache eliminado")

    # ── LOAD DATA ──
    with st.spinner("Cargando datos..."):
        try:
            data = load_all_data(force_refresh=force_refresh)
        except Exception as e:
            st.error(f"Error cargando datos: {e}")
            data = {"waves": {}, "mentions": [], "social": {}, "analysis": {}}

    analysis = data.get("analysis", {})
    social   = data.get("social", {})
    waves    = data.get("waves", {})

    # ── CONTAINER START ──
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # ── TABS ──
    tab0, tab1, tab2, tab3 = st.tabs([
        "🎯  Overview Ejecutivo",
        "📊  Brand Health Tracker",
        "🌐  Social Listening",
        "⚡  Accionables Growth",
    ])

    # ════════════════════════════════════════
    # TAB 0 — OVERVIEW EJECUTIVO
    # ════════════════════════════════════════
    with tab0:
        import pandas as pd
        import math as _math
        _bht_ov = load_bht_real()

        # ── Data prep ──────────────────────────────────────────
        _soc_ov  = data.get("social", {})
        _raw_ov  = _soc_ov.get("raw_mentions", [])
        _sd_ov   = _soc_ov.get("sentiment_distribution", {})
        _pct_neg = _sd_ov.get("negativo", 0)
        _pct_pos = _sd_ov.get("positivo", 0)
        _top_neg = _soc_ov.get("negative_clusters", [{}])[0].get("tema", "–") if _soc_ov.get("negative_clusters") else "–"
        _tot_men = _soc_ov.get("total_mentions", 0)

        def _safe(v):
            return None if (v is None or _math.isnan(v)) else v

        if _bht_ov is not None and not _bht_ov.empty:
            _OLA_ORDER_OV = ["Ola 0","Ola 1","Ola 2","Ola 3","Ola 4","Ola 5","Ola 6","Ola 7","Ola 8","Ola 9 Ligth","W10","W11","W12"]
            _piv_ov = _bht_ov.pivot_table(index="ola", columns="metrica", values="valor", aggfunc="mean")
            _piv_ov = _piv_ov.reindex([o for o in _OLA_ORDER_OV if o in _piv_ov.index])
            _latest_ov = _piv_ov.iloc[-1] if len(_piv_ov) > 0 else pd.Series(dtype=float)
            _prev_ov   = _piv_ov.iloc[-2] if len(_piv_ov) > 1 else pd.Series(dtype=float)
            _first_ov  = _piv_ov.iloc[0]  if len(_piv_ov) > 0 else pd.Series(dtype=float)
            def _ov_val(col): return _safe(_latest_ov.get(col, None))
            def _ov_first(col): return _safe(_first_ov.get(col, None))
            def _ov_delta(col):
                v, p = _safe(_latest_ov.get(col)), _safe(_prev_ov.get(col))
                return round(v - p, 1) if (v is not None and p is not None) else None
            _tom  = _ov_val("Top_of_Mind")
            _awa  = _ov_val("Awareness_Asistida")
        else:
            _ov_val   = lambda col: None
            _ov_first = lambda col: None
            _ov_delta = lambda col: None
            _tom = _awa = None

        def _fmt(v, unit=""): return f"{round(v)}{unit}" if v is not None else "–"
        def _delta_chip(d, unit="%"):
            if d is None: return ""
            col = "#38A169" if d > 0 else "#E53E3E"
            arr = "▲" if d > 0 else "▼"
            return f'<span style="font-size:11px;font-weight:600;color:{col};margin-left:6px">{arr} {abs(d)}{unit}</span>'

        # ── Hero: Executive Summary ─────────────────────────────
        # Build narrative from BHT data (first → latest ola)
        _tom_f   = _ov_first("Top_of_Mind")        if _bht_ov is not None and not _bht_ov.empty else None
        _awa_f   = _ov_first("Awareness_Asistida") if _bht_ov is not None and not _bht_ov.empty else None
        _con_f   = _ov_first("Consideracion")      if _bht_ov is not None and not _bht_ov.empty else None
        _tom_l   = _ov_val("Top_of_Mind")
        _awa_l   = _ov_val("Awareness_Asistida")
        _con_l   = _ov_val("Consideracion")
        _nps_l   = _ov_val("NPS_Score")
        _bei_l   = _ov_val("Brand_Equity_Index")
        _con_d   = _ov_delta("Consideracion")
        _int_d   = _ov_delta("Intencion_de_Compra")

        def _range_str(f, l, unit="%"):
            if f is not None and l is not None:
                return f"<strong>de {round(f)}{unit} a {round(l)}{unit}</strong>"
            if l is not None:
                return f"<strong>{round(l)}{unit}</strong>"
            return "–"

        _body_parts = [
            f"Kavak México muestra un crecimiento sostenido de marca en los últimos 5 años: "
            f"el Top of Mind pasó {_range_str(_tom_f, _tom_l)}, "
            f"el Awareness Asistido {_range_str(_awa_f, _awa_l)} "
            f"y la Consideración {_range_str(_con_f, _con_l)}."
        ]
        _kpi_parts = []
        if _nps_l is not None: _kpi_parts.append(f"El NPS alcanzó <strong>{round(_nps_l)} puntos</strong>")
        if _bei_l is not None: _kpi_parts.append(f"el Brand Equity Index se ubica en <strong>{round(_bei_l)}</strong>")
        if _kpi_parts:
            _body_parts.append(", ".join(_kpi_parts) + ". La marca se consolidó como líder indiscutida en seminuevos en México.")

        _body_html = " ".join(_body_parts)

        # Alert signal: highlight negative deltas from last period
        _alert_parts = []
        if _con_d is not None and _con_d < 0:
            _alert_parts.append(f"Consideración cayó {abs(_con_d)}pp")
        if _int_d is not None and _int_d < 0:
            _alert_parts.append(f"Intención de Compra {abs(_int_d)}pp")
        _alert_html = ""
        if _alert_parts:
            _alert_text = " e ".join(_alert_parts)
            _alert_html = ('<div style="margin-top:16px;font-size:14px">'
                           '<span style="color:#C5E50B;font-weight:700;margin-right:4px">&#9888;</span>'
                           '<span style="color:#C5E50B;font-weight:700">Se&#241;al a monitorear:</span>'
                           '<span style="color:#C5E50B"> ' + _alert_text + ' en el &#250;ltimo per&#237;odo.</span>'
                           '</div>')

        _hero = (
            '<div style="background:#0467FC;border-radius:12px;padding:28px 36px;margin-bottom:20px;position:relative;overflow:hidden">'
            '<div style="position:absolute;right:-40px;top:-40px;width:220px;height:220px;border-radius:50%;background:rgba(255,255,255,0.07)"></div>'
            '<div style="position:absolute;right:60px;bottom:-60px;width:160px;height:160px;border-radius:50%;background:rgba(255,255,255,0.05)"></div>'
            '<div style="position:relative;z-index:1">'
            '<div style="font-size:14px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#C5E50B;margin-bottom:14px">Executive Summary &middot; Brand Health Tracker Analysis</div>'
            '<div style="font-size:15px;font-weight:400;color:rgba(255,255,255,0.95);line-height:1.7">' + _body_html + '</div>'
            + _alert_html +
            '</div></div>'
        )
        st.markdown(_hero, unsafe_allow_html=True)

        # ── BHT KPI row ────────────────────────────────────────
        section_header("Brand Health · Última Ola", dot_color="blue")
        if _bht_ov is not None and not _bht_ov.empty:
            _kpi_defs = [
                ("Top_of_Mind",               "Top of Mind",    "%"),
                ("Awareness_Asistida",         "Awareness",      "%"),
                ("Consideracion",              "Consideración",  "%"),
                ("NPS_Score",                 "NPS Score",       " pts"),
                ("Brand_Equity_Index",         "Brand Equity",   ""),
                ("Brand_Satisfaction_Top2box", "Satisfacción",   "%"),
            ]
            _kpi_cols = st.columns(len(_kpi_defs))
            for _col, (_metric, _label, _unit) in zip(_kpi_cols, _kpi_defs):
                _v = _ov_val(_metric)
                _d = _ov_delta(_metric)
                _v_str   = _fmt(_v, _unit)
                _d_chip  = _delta_chip(_d, unit=_unit.strip())
                with _col:
                    st.markdown(f"""
                    <div style="background:#fff;border:1px solid #EDF0F7;border-radius:12px;
                      padding:20px 10px;text-align:center;
                      box-shadow:0 2px 8px rgba(4,103,252,0.06)">
                      <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                        letter-spacing:.6px;color:#A0AEC0;margin-bottom:10px">{_label}</div>
                      <div style="font-size:28px;font-weight:800;color:var(--kavak-blue);line-height:1">{_v_str}</div>
                      <div style="margin-top:8px;min-height:18px">{_d_chip}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Cargá archivos BHT en /data para ver los KPIs.")

        # ── Social Snapshot + Señales ────────────────────────────
        _pct_pos_r = round(_sd_ov.get("positivo", 0))
        _pct_neg_r = round(_sd_ov.get("negativo", 0))
        _pct_mix_r = round(_sd_ov.get("mixto", 0))
        _pct_neu_r = round(_sd_ov.get("neutro", 0))
        _tt        = _soc_ov.get("top_themes", [])[:5]

        # Stacked bar proportions
        _tp = _pct_pos_r + _pct_neg_r + _pct_mix_r + _pct_neu_r
        if _tp == 0: _tp = 1
        _bp = round(_pct_pos_r / _tp * 100)
        _bn = round(_pct_neg_r / _tp * 100)
        _bm = round(_pct_mix_r / _tp * 100)
        _bu = max(0, 100 - _bp - _bn - _bm)

        # Sentiment stat cell — refined
        def _sent_cell(pct, label, color):
            return (
                '<td style="padding:0 28px 16px 0;vertical-align:top">'
                '<div style="font-size:26px;font-weight:800;color:' + color + ';line-height:1;letter-spacing:-0.5px">'
                + str(pct) + '%</div>'
                '<div style="font-size:9px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;'
                'color:#C8D0DC;margin-top:5px">' + label + '</div>'
                '</td>'
            )

        # Theme dots — colored by rank
        _THEME_COLORS = ["#0467FC","#3685FD","#68A4FD","#94BBFE","#BDD4FE"]
        _themes_col = (
            '<div style="font-size:9px;font-weight:700;letter-spacing:1.8px;text-transform:uppercase;'
            'color:#C8D0DC;margin-bottom:10px">Temas principales</div>'
            + "".join(
                '<div style="margin-bottom:7px">'
                '<span style="display:inline-block;width:7px;height:7px;border-radius:50%;'
                'background:' + _THEME_COLORS[min(i, len(_THEME_COLORS)-1)] + ';'
                'vertical-align:middle;margin-right:8px"></span>'
                '<span style="font-size:12px;font-weight:600;color:#2D3748;vertical-align:middle">' + t["tema"] + '</span>'
                '<span style="font-size:11px;color:#C8D0DC;margin-left:5px;vertical-align:middle">' + str(t["count"]) + '</span>'
                '</div>'
                for i, t in enumerate(_tt)
            )
        )

        _social_snap_html = (
            # Three columns: hero | 2×2 stats | themes
            '<table style="width:100%;border-collapse:collapse;margin-bottom:18px"><tr style="vertical-align:top">'
            # Hero + bar in same cell
            '<td style="width:38%;padding-right:24px;border-right:1px solid #EDF2F7;vertical-align:middle">'
            '<div style="font-size:60px;font-weight:800;color:#0E1829;line-height:1;letter-spacing:-4px">'
            + str(_tot_men) + '</div>'
            '<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
            'color:#C8D0DC;margin-top:8px">menciones analizadas</div>'
            '</td>'
            # 2×2 sentiment stats
            '<td style="width:38%;vertical-align:top;padding:0 24px;border-right:1px solid #EDF2F7">'
            '<table style="border-collapse:collapse"><tr>'
            + _sent_cell(_pct_pos_r, "Positivas", "#38A169")
            + _sent_cell(_pct_neg_r, "Negativas", "#E53E3E")
            + '</tr><tr>'
            + _sent_cell(_pct_mix_r, "Mixtas",    "#D69E2E")
            + _sent_cell(_pct_neu_r, "Neutras",   "#C8D0DC")
            + '</tr></table>'
            '</td>'
            # Themes vertical list
            '<td style="vertical-align:top;padding-left:24px">' + _themes_col + '</td>'
            '</tr></table>'
        )

        # Señales
        _pos_clusters = _soc_ov.get("positive_clusters", [])[:2]
        _neg_clusters = _soc_ov.get("negative_clusters", [])[:3]
        _strengths = (
            ([f"Top of Mind {round(_tom)}% — liderazgo de categoría"] if _tom else []) +
            ["Serie F $300M · Primera rentabilidad global dic 2025"] +
            [f"Percepción positiva en {c['tema']}" for c in _pos_clusters]
        )[:3]
        _risks = (
            [f"{round(_pct_neg or 0)}% menciones negativas · tema crítico: {_top_neg}"] +
            [f"Quejas en {c['tema']} ({c['count']} menciones)"
             for c in _neg_clusters if c.get("tema") != _top_neg]
        )[:3]

        # Signal item — table for reliable dot/text alignment (borders killed by global CSS)
        def _sig_row(text, color):
            return (
                '<div style="padding:1px 0">'
                '<table style="width:100%;border-collapse:collapse">'
                '<tr style="vertical-align:top">'
                '<td style="width:14px;padding-top:3px;padding-right:8px">'
                '<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:' + color + '"></span>'
                '</td>'
                '<td style="font-size:13px;color:#2D3748;line-height:1.6">' + text + '</td>'
                '</tr></table>'
                '</div>'
            )

        def _col_label(text, color):
            return (
                '<div style="font-size:13px;font-weight:700;text-transform:uppercase;'
                'letter-spacing:1.5px;color:' + color + ';margin-bottom:14px">' + text + '</div>'
            )

        _str_col = _col_label("Fortalezas", "#0467FC") + "".join(_sig_row(s, "#0467FC") for s in _strengths)
        _risk_col = _col_label("Riesgos", "#E53E3E")   + "".join(_sig_row(r, "#E53E3E") for r in _risks)
        _senales_html = (
            '<div style="height:16px"></div>'
            '<table style="width:100%;border-collapse:collapse"><tr style="vertical-align:top">'
            '<td style="width:50%;padding-right:20px;border:none">' + _str_col + '</td>'
            '<td style="width:50%;padding-left:4px;border:none">'  + _risk_col + '</td>'
            '</tr></table>'
        )

        _col_snap, _col_sig = st.columns([1, 1])
        with _col_snap:
            section_header("Social Listening · Snapshot", dot_color="blue")
            st.markdown(_social_snap_html, unsafe_allow_html=True)
        with _col_sig:
            section_header("Se&#241;ales Estrat&#233;gicas", dot_color="blue")
            st.markdown(_senales_html, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # TAB 1 — BRAND HEALTH
    # ════════════════════════════════════════
    with tab1:
        import pandas as pd
        bht_df = load_bht_real()

        if bht_df is None or bht_df.empty:
            empty_state("📋", "No hay datos BHT", "Copiá los archivos BHT en /data o verificá el CSV consolidado.")
        else:
            # ── Mapeo de olas a fechas legibles ──
            OLA_LABELS = {
                "Ola 0": "W0 Jul'20", "Ola 1": "W1 Oct'20", "Ola 2": "W2 Feb'21",
                "Ola 3": "W3 Jun'21", "Ola 4": "W4 Sep'21", "Ola 5": "W5 Mar'22",
                "Ola 6": "W6 Nov'22", "Ola 7": "W7 Mar'23", "Ola 8": "W8 Nov'23",
                "Ola 9 Ligth": "W9 Jun'24",
                "W10": "W10 Dic'24", "W11": "W11 Jul'25", "W12": "W12 Dic'25",
            }
            OLA_ORDER = list(OLA_LABELS.keys())

            # Pivot: ola x metrica
            pivot = bht_df.pivot_table(index="ola", columns="metrica", values="valor", aggfunc="mean")
            pivot = pivot.reindex([o for o in OLA_ORDER if o in pivot.index])
            pivot.index = [OLA_LABELS.get(o, o) for o in pivot.index]

            # ── KPI Summary Cards — última ola ──
            latest_label = pivot.index[-1]
            prev_label   = pivot.index[-2] if len(pivot.index) >= 2 else None

            METRIC_CONFIG = [
                ("Top_of_Mind",        "Top of Mind",         "#0467FC", True),
                ("Awareness_Asistida", "Awareness Asistida",  "#0352C9", True),
                ("Consideracion",      "Consideración",       "#3685FD", True),
                ("NPS_Score",          "NPS Score",           "#C8ED02", False),
                ("Brand_Equity_Index", "Brand Equity Index",  "#38A169", False),
                ("Intencion_Compra_Total", "Intención Compra", "#68A4FD", True),
                ("Brand_Favorability_T2B", "Favorabilidad",   "#805AD5", True),
                ("Brand_Satisfaction_Top2box", "Satisfacción", "#D69E2E", True),
            ]

            METRIC_DEFINITIONS = {
                "Top_of_Mind": (
                    "Top of Mind (TOM)",
                    "Primera marca que viene a la mente al pensar en compra/venta de autos seminuevos, "
                    "sin ningún estímulo previo. Es el indicador más fuerte de liderazgo de marca. "
                    "Se mide como % de personas que mencionan Kavak en primer lugar."
                ),
                "Awareness_Asistida": (
                    "Awareness Asistida",
                    "% de personas que conocen o han escuchado hablar de Kavak cuando se les muestra "
                    "el nombre o logo de la marca. Mide el alcance total del reconocimiento de marca "
                    "en la categoría de seminuevos."
                ),
                "Awareness_Espontanea": (
                    "Awareness Espontáneo",
                    "% de personas que mencionan Kavak sin recibir ninguna ayuda o estímulo, "
                    "al preguntar qué marcas conocen de compra/venta de autos seminuevos. "
                    "Más exigente que el awareness asistido."
                ),
                "Consideracion": (
                    "Consideración",
                    "% de personas que considerarían comprar o vender su auto con Kavak en los "
                    "próximos 12 meses. Es un indicador clave del funnel de conversión: "
                    "quienes conocen la marca y estarían dispuestos a usarla."
                ),
                "NPS_Score": (
                    "NPS — Net Promoter Score",
                    "Índice de lealtad y recomendación: % Promotores (9-10) menos % Detractores (0-6). "
                    "Rango: -100 a +100. Un NPS > 50 se considera excelente. "
                    "Mide qué tan probable es que los clientes recomienden Kavak a amigos/familia."
                ),
                "Brand_Equity_Index": (
                    "Brand Equity Index",
                    "Índice compuesto que combina favorabilidad, diferenciación y cercanía emocional "
                    "con la marca. Refleja la fortaleza integral del brand equity de Kavak vs la competencia. "
                    "Escala de 0 a 100."
                ),
                "Intencion_Compra_Total": (
                    "Intención de Compra Total",
                    "% de personas que declaran intención de comprar un auto seminuevo con Kavak "
                    "en el corto/mediano plazo, incluyendo primera y segunda mención. "
                    "Indicador directo de demanda potencial."
                ),
                "Brand_Favorability_T2B": (
                    "Favorabilidad de Marca (T2B)",
                    "Top 2 Box de opinión favorable hacia Kavak: % de personas con opinión "
                    "'muy favorable' o 'favorable'. Mide la simpatía general hacia la marca "
                    "independientemente de si son clientes actuales."
                ),
                "Brand_Satisfaction_Top2box": (
                    "Satisfacción (T2B)",
                    "Top 2 Box de satisfacción: % de clientes que califican su experiencia "
                    "con Kavak como 'muy satisfactoria' o 'satisfactoria'. "
                    "Indicador de calidad del servicio post-venta."
                ),
                "Brand_Affinity_Top2box": (
                    "Afinidad de Marca (T2B)",
                    "% de personas que sienten conexión o afinidad con Kavak. "
                    "Mide el vínculo emocional entre la marca y el consumidor, "
                    "más allá de la transacción racional."
                ),
                "Experiencia_Compra_Pasada": (
                    "Experiencia de Compra Pasada",
                    "% de personas que han tenido una experiencia de compra/venta con Kavak "
                    "y la califican positivamente. Refleja la satisfacción real basada en "
                    "interacción directa con la marca."
                ),
            }

            # helper: safe get from pivot
            def pv(col, label=latest_label):
                try:
                    v = pivot.loc[label, col]
                    return None if pd.isna(v) else v
                except Exception:
                    return None

            first_label = pivot.index[0]

            def build_detail(col_name, val, suffix, definition_text):
                rows = f'<div class="kpi-detail-def">{definition_text}</div>'

                # Trend from first ola
                v0 = pv(col_name, first_label)
                if v0 is not None:
                    rows += '<div class="kpi-section-label">Evolución</div>'
                    growth = val - v0
                    sign = "+" if growth >= 0 else ""
                    rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">Desde {first_label}</span><span class="kpi-detail-val">{v0:.1f}{suffix}</span></div>'
                    rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">Crecimiento total</span><span class="kpi-detail-val" style="color:#38A169">{sign}{growth:.1f}pp</span></div>'

                # Metric-specific breakdowns
                if col_name == "Top_of_Mind":
                    esp = pv("Awareness_Espontanea")
                    if esp is not None:
                        rows += '<div class="kpi-section-label">Contexto</div>'
                        rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">Awareness Espontáneo</span><span class="kpi-detail-val">{esp:.1f}%</span></div>'

                elif col_name == "Awareness_Asistida":
                    esp = pv("Awareness_Espontanea")
                    if esp is not None:
                        rows += '<div class="kpi-section-label">Comparativa</div>'
                        rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">Espontáneo</span><span class="kpi-detail-val">{esp:.1f}%</span></div>'
                        rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">Asistido</span><span class="kpi-detail-val">{val:.1f}%</span></div>'
                        conv = (esp / val * 100) if val else 0
                        rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">Ratio espontáneo/asistido</span><span class="kpi-detail-val">{conv:.0f}%</span></div>'

                elif col_name == "NPS_Score":
                    prom = pv("NPS_Promotores_pct")
                    pas  = pv("NPS_Pasivos_pct")
                    det  = pv("NPS_Detractores_pct")
                    if any(x is not None for x in [prom, pas, det]):
                        rows += '<div class="kpi-section-label">Desglose</div>'
                        if prom is not None:
                            rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">🟢 Promotores (9-10)</span><span class="kpi-detail-val" style="color:#38A169">{prom:.0f}%</span></div>'
                        if pas is not None:
                            rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">🟡 Pasivos (7-8)</span><span class="kpi-detail-val" style="color:#D69E2E">{pas:.0f}%</span></div>'
                        if det is not None:
                            rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">🔴 Detractores (0-6)</span><span class="kpi-detail-val" style="color:#E53E3E">{det:.0f}%</span></div>'

                elif col_name == "Brand_Equity_Index":
                    for sub_col, sub_label in [
                        ("Brand_Overall_Rating_T3B",   "Valoración general (T3B)"),
                        ("Brand_Favorability_T2B",      "Favorabilidad (T2B)"),
                        ("Brand_Differentiation_T2B",   "Diferenciación (T2B)"),
                        ("Brand_Closeness_T3B",         "Cercanía emocional (T3B)"),
                    ]:
                        sv = pv(sub_col)
                        if sv is not None:
                            rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">{sub_label}</span><span class="kpi-detail-val">{sv:.0f}%</span></div>'

                elif col_name == "Intencion_Compra_Total":
                    v1 = pv("Intencion_Compra_1a")
                    if v1 is not None:
                        rows += '<div class="kpi-section-label">Desglose</div>'
                        rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">Primera mención</span><span class="kpi-detail-val">{v1:.1f}%</span></div>'
                        rows += f'<div class="kpi-detail-row"><span class="kpi-detail-label">Total (1a + 2a)</span><span class="kpi-detail-val">{val:.1f}%</span></div>'

                return rows

            # ── Dialog definition ──
            @st.dialog(" ", width="large")
            def kpi_dialog(col_name, label, color, val, suffix, prev_val, prev_label_d):
                import plotly.graph_objects as go

                def_title, def_text = METRIC_DEFINITIONS.get(col_name, (label, "Sin definición disponible."))
                diff = (val - prev_val) if prev_val is not None else None
                diff_color = "#38A169" if (diff and diff > 0) else ("#E53E3E" if (diff and diff < 0) else "#A0AEC0")
                diff_str = (f'{"+" if diff >= 0 else ""}{diff:.1f}pp vs {prev_label_d}') if diff is not None else ""

                # ── Title block ──
                st.markdown(
                    f'<div style="margin-bottom:2px;">'
                    f'<h2 style="font-size:24px;font-weight:800;color:#1A202C;margin:0 0 4px 0;letter-spacing:-0.5px;">{def_title}</h2>'
                    f'<div style="font-size:13px;color:#A0AEC0;">BHT México · {latest_label}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

                # ── Big centered stat ──
                delta_line = (
                    f'<div style="font-size:13px;font-weight:700;color:{diff_color};margin-top:6px;">{diff_str}</div>'
                    if diff_str else ""
                )
                st.markdown(
                    f'<div style="text-align:center;padding:16px 0 24px;">'
                    f'<div style="font-size:64px;font-weight:800;color:#1A202C;letter-spacing:-3px;line-height:1;">{val:.1f}{suffix}</div>'
                    f'<div style="font-size:12px;font-weight:600;color:#A0AEC0;margin-top:8px;letter-spacing:.3px;">'
                    f'{label} &nbsp;·&nbsp; {latest_label}</div>'
                    f'{delta_line}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # ── Definition ──
                st.markdown(
                    f'<div style="font-size:13px;color:#4A5568;line-height:1.7;'
                    f'padding:16px 0;border-top:1px solid #E2E8F0;border-bottom:1px solid #E2E8F0;">'
                    f'{def_text}</div>',
                    unsafe_allow_html=True
                )

                # ── Helper: render a whole section (label + rows) as one block ──
                def render_section(title, rows_data):
                    """rows_data: list of (label, value_str, color_hex)"""
                    rows_html = "".join(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'padding:9px 0;border-bottom:1px solid #F7FAFC;">'
                        f'<span style="font-size:13px;color:#2D3748;">{lbl}</span>'
                        f'<span style="font-size:13px;font-weight:700;color:{vc};">{v}</span>'
                        f'</div>'
                        for lbl, v, vc in rows_data
                    )
                    st.markdown(
                        f'<div style="margin-top:20px;">'
                        f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                        f'letter-spacing:.8px;color:#0467FC;margin-bottom:10px;">{title}</div>'
                        f'{rows_html}</div>',
                        unsafe_allow_html=True
                    )

                # Evolución
                v0 = pv(col_name, first_label)
                if v0 is not None:
                    growth = val - v0
                    render_section("Evolución", [
                        (f"Valor inicial ({first_label})", f"{v0:.1f}{suffix}", "#2D3748"),
                        (f"Valor actual ({latest_label})", f"{val:.1f}{suffix}", color),
                        ("Crecimiento total", f'{"+" if growth >= 0 else ""}{growth:.1f}pp',
                         "#38A169" if growth > 0 else "#E53E3E"),
                    ])

                # Metric-specific breakdowns
                if col_name == "NPS_Score":
                    prom = pv("NPS_Promotores_pct")
                    pas  = pv("NPS_Pasivos_pct")
                    det  = pv("NPS_Detractores_pct")
                    breakdown = []
                    if prom is not None: breakdown.append(("Promotores (9–10)", f"{prom:.0f}%", "#38A169"))
                    if pas  is not None: breakdown.append(("Pasivos (7–8)",     f"{pas:.0f}%",  "#D69E2E"))
                    if det  is not None: breakdown.append(("Detractores (0–6)", f"{det:.0f}%",  "#E53E3E"))
                    if breakdown:
                        render_section("Desglose NPS", breakdown)

                elif col_name == "Brand_Equity_Index":
                    sub_items = [
                        ("Brand_Overall_Rating_T3B", "Valoración general (T3B)"),
                        ("Brand_Favorability_T2B",   "Favorabilidad (T2B)"),
                        ("Brand_Differentiation_T2B","Diferenciación (T2B)"),
                        ("Brand_Closeness_T3B",      "Cercanía emocional (T3B)"),
                    ]
                    breakdown = [(lbl, f"{pv(c):.0f}%", "#2D3748") for c, lbl in sub_items if pv(c) is not None]
                    if breakdown:
                        render_section("Submétricas", breakdown)

                elif col_name == "Awareness_Asistida":
                    esp = pv("Awareness_Espontanea")
                    if esp is not None:
                        render_section("Comparativa", [
                            ("Awareness Espontáneo", f"{esp:.1f}%", "#2D3748"),
                            ("Awareness Asistido",   f"{val:.1f}%", "#2D3748"),
                            ("Ratio espontáneo/asistido", f"{esp/val*100:.0f}%" if val else "—", "#2D3748"),
                        ])

                elif col_name == "Intencion_Compra_Total":
                    v1 = pv("Intencion_Compra_1a")
                    if v1 is not None:
                        render_section("Desglose", [
                            ("Primera mención", f"{v1:.1f}%", "#2D3748"),
                            ("Total (1ª + 2ª)", f"{val:.1f}%", "#2D3748"),
                        ])

                # ── Mini chart ──
                if col_name in pivot.columns:
                    pairs = [(x, v) for x, v in zip(pivot.index.tolist(), pivot[col_name].tolist()) if v is not None and not pd.isna(v)]
                    if len(pairs) > 1:
                        xs, ys = zip(*pairs)
                        st.markdown(
                            '<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                            'letter-spacing:.8px;color:#0467FC;margin-top:24px;margin-bottom:4px;">'
                            'Tendencia histórica</div>',
                            unsafe_allow_html=True
                        )
                        fig = go.Figure()
                        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
                        fig.add_trace(go.Scatter(
                            x=list(xs), y=list(ys), mode="lines+markers",
                            line=dict(color=color, width=2.5),
                            marker=dict(size=6, color=color, line=dict(color="white", width=1.5)),
                            fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.07)",
                            hovertemplate="%{x}: <b>%{y:.1f}" + suffix + "</b><extra></extra>",
                        ))
                        fig.update_layout(
                            height=200, margin=dict(l=0, r=0, t=8, b=0),
                            plot_bgcolor="white", paper_bgcolor="white",
                            xaxis=dict(showgrid=False, tickangle=-30, tickfont=dict(size=10)),
                            yaxis=dict(showgrid=True, gridcolor="#F0F4F8", zeroline=False, tickfont=dict(size=10)),
                            showlegend=False,
                        )
                        st.plotly_chart(fig, use_container_width=True)

            # ── Cards (plain, no expand — click opens dialog) ──
            section_header(f"Brand Health — Última Ola ({latest_label})", dot_color="blue")

            visible_cards = []
            for (col_name, label, color, is_pct) in METRIC_CONFIG:
                if col_name not in pivot.columns:
                    continue
                val = pv(col_name)
                if val is None:
                    continue
                prev_val = pv(col_name, prev_label) if prev_label else None
                visible_cards.append((col_name, label, color, is_pct, val, prev_val))

            for row_start in range(0, len(visible_cards), 4):
                row = visible_cards[row_start:row_start + 4]
                cols = st.columns(4)
                for idx, (col_name, label, color, is_pct, val, prev_val) in enumerate(row):
                    suffix = "%" if is_pct else ""
                    val_str = f"{val:.1f}{suffix}"
                    if prev_val is not None:
                        diff = val - prev_val
                        if diff > 0:
                            delta_html = f'<span class="delta-up">▲ +{diff:.1f}pp</span>'
                        elif diff < 0:
                            delta_html = f'<span class="delta-down">▼ {diff:.1f}pp</span>'
                        else:
                            delta_html = '<span class="delta-flat">→</span>'
                        sub_html = f'<div class="kpi-sub">vs {prev_label}: {prev_val:.1f}{suffix}</div>'
                    else:
                        delta_html = ""
                        sub_html = ""

                    with cols[idx]:
                        # Button FIRST — transparent click target
                        if st.button(" ", key=f"kpi_dlg_{col_name}", use_container_width=True):
                            kpi_dialog(col_name, label, color, val, suffix, prev_val, prev_label)
                        # Card HTML SECOND — overlaid via CSS negative margin, pointer-events: none
                        st.markdown(
                            f'<div class="kpi-block" style="border-top:3px solid {color};">'
                            f'  <div class="kpi-label">{label.upper()}</div>'
                            f'  <div style="display:flex;justify-content:space-between;align-items:center;">'
                            f'    <div class="kpi-value" style="color:{color}">{val_str}</div>'
                            f'    <div>{delta_html}</div>'
                            f'  </div>'
                            f'  {sub_html}'
                            f'</div>',
                            unsafe_allow_html=True
                        )

            # ── Gráfico de evolución ──
            section_header("Evolución Brand Health — W0 a W12 (2020–2025)", dot_color="blue")
            try:
                import plotly.graph_objects as go

                EVOL_METRICS = {
                    "Top_of_Mind":            ("Top of Mind",        "#0467FC", "solid"),
                    "Awareness_Asistida":      ("Awareness Asistida", "#C8ED02", "solid"),
                    "Consideracion":           ("Consideración",      "#E53E3E", "dot"),
                    "NPS_Score":               ("NPS Score",          "#805AD5", "dash"),
                    "Brand_Equity_Index":      ("Brand Equity Index", "#38A169", "dash"),
                    "Intencion_Compra_Total":  ("Intención Compra",   "#D69E2E", "dot"),
                }

                available = [k for k in EVOL_METRICS if k in pivot.columns]
                default_sel = [k for k in ["Top_of_Mind", "Awareness_Asistida", "Consideracion", "NPS_Score"] if k in available]

                selected_keys = st.multiselect(
                    "Métricas:",
                    options=available,
                    default=default_sel,
                    format_func=lambda k: EVOL_METRICS[k][0],
                    key="bht_evol_select",
                )

                if selected_keys:
                    fig = go.Figure()
                    for k in selected_keys:
                        meta_name, color, dash = EVOL_METRICS[k]
                        y_vals = pivot[k].tolist()
                        fig.add_trace(go.Scatter(
                            x=pivot.index.tolist(), y=y_vals,
                            name=meta_name,
                            mode="lines+markers",
                            line=dict(color=color, width=2.5, dash=dash),
                            marker=dict(size=7, line=dict(color="white", width=1.5)),
                            connectgaps=True,
                            hovertemplate=f"<b>{meta_name}</b><br>%{{x}}: %{{y:.1f}}<extra></extra>",
                        ))
                    fig.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white",
                        font=dict(family="Helvetica Neue", size=12, color="#1A202C"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12)),
                        margin=dict(l=0, r=0, t=40, b=0),
                        xaxis=dict(showgrid=False, linecolor="#E2E8F0", tickangle=-30),
                        yaxis=dict(showgrid=True, gridcolor="#F0F4F8", zeroline=False),
                        height=360,
                        hovermode="x unified",
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                st.info("Instalá `plotly`: `pip install plotly`")

            # ── Tabla completa de datos ──
            section_header("Datos completos por ola", dot_color="blue")
            METRIC_LABELS = {
                "Top_of_Mind": "Top of Mind (%)",
                "Awareness_Espontanea": "Awareness Espontánea (%)",
                "Awareness_Asistida": "Awareness Asistida (%)",
                "Consideracion": "Consideración (%)",
                "Intencion_Compra_1a": "Intención Compra 1ra (%)",
                "Intencion_Compra_Total": "Intención Compra Total (%)",
                "NPS_Score": "NPS Score",
                "NPS_Promotores_pct": "Promotores (%)",
                "NPS_Detractores_pct": "Detractores (%)",
                "Brand_Satisfaction_Top2box": "Satisfacción Top2Box (%)",
                "Brand_Affinity_Top2box": "Afinidad Top2Box (%)",
                "Experiencia_Compra_Pasada": "Exp. Compra (%)",
                "Experiencia_Venta_Pasada": "Exp. Venta (%)",
            }
            display_df = pivot[[c for c in METRIC_LABELS if c in pivot.columns]].copy()
            display_df.columns = [METRIC_LABELS[c] for c in display_df.columns]
            display_df = display_df.round(1).T
            st.dataframe(display_df, use_container_width=True)

            # ── Insights BHT (si hay análisis IA) ──
            insights_bht = analysis.get("brand_health_insights", [])
            if insights_bht:
                section_header("Insights IA de Brand Health", dot_color="blue", count=len(insights_bht))
                col_l, col_r = st.columns(2)
                mid = (len(insights_bht) + 1) // 2
                with col_l:
                    for ins in insights_bht[:mid]:
                        render_kpi_card(ins, "brand")
                with col_r:
                    for ins in insights_bht[mid:]:
                        render_kpi_card(ins, "brand")

            # ── Brechas ──
            brechas = analysis.get("brechas_detectadas", [])
            if brechas:
                section_header("Brechas Percepción / Realidad", dot_color="red", count=len(brechas))
                for b in brechas:
                    impact = b.get("impacto", "bajo")
                    border_color = "#E53E3E" if impact == "alto" else "#D69E2E" if impact == "medio" else "#38A169"
                    bht_ev = b.get("evidencia_bht", "")
                    soc_ev = b.get("evidencia_social", "")
                    tag_color = "red" if impact == "alto" else "yellow" if impact == "medio" else "green"
                    st.markdown(f"""
                    <div class="kpi-card" style="border-left-color:{border_color}">
                      <div class="kpi-card-header">
                        <span class="kpi-card-title">⚠️ {b.get('brecha', '')}</span>
                        <span class="tag tag-{tag_color}">impacto {impact}</span>
                      </div>
                      <div class="kpi-card-text">
                        {"<strong>BHT:</strong> " + bht_ev + "<br>" if bht_ev else ""}
                        {"<strong>Social:</strong> " + soc_ev if soc_ev else ""}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # TAB 2 — SOCIAL LISTENING
    # ════════════════════════════════════════
    with tab2:
        total_mentions = social.get("total_mentions", 0)

        if total_mentions == 0:
            empty_state("🌐", "Sin datos de social listening", "Corrés <code>python run.py</code> para recolectar menciones.")
        else:
            # ── Filtro de fechas ──────────────────────────────────────
            import datetime as _dt

            _QUARTER_START = {
                "2025-Q1": _dt.date(2025, 1, 1), "2025-Q2": _dt.date(2025, 4, 1),
                "2025-Q3": _dt.date(2025, 7, 1), "2025-Q4": _dt.date(2025, 10, 1),
                "2026-Q1": _dt.date(2026, 1, 1), "2026-Q2": _dt.date(2026, 4, 1),
            }

            def _mention_date(m):
                """Devuelve un date aproximado de una mención para filtrar."""
                fd = m.get("fecha_mencion")
                if fd:
                    try:
                        return _dt.date.fromisoformat(str(fd)[:10])
                    except ValueError:
                        pass
                fa = m.get("fecha_aprox", "")
                return _QUARTER_START.get(fa, _dt.date(2025, 1, 1))

            raw_mentions = social.get("raw_mentions", [])

            _fcol1, _fcol2, _fcol3 = st.columns([2, 2, 3])
            with _fcol1:
                date_start = st.date_input(
                    "Desde",
                    value=_dt.date(2025, 1, 1),
                    min_value=_dt.date(2025, 1, 1),
                    max_value=_dt.date.today(),
                    key="sl_date_start",
                )
            with _fcol2:
                date_end = st.date_input(
                    "Hasta",
                    value=_dt.date.today(),
                    min_value=_dt.date(2025, 1, 1),
                    max_value=_dt.date.today(),
                    key="sl_date_end",
                )
            with _fcol3:
                all_platforms = sorted(set(
                    (m.get("plataforma_normalizada") or m.get("fuente", "otro")).split(" —")[0][:30]
                    for m in raw_mentions
                ))
                selected_platforms = st.multiselect(
                    "Plataformas",
                    options=all_platforms,
                    default=[],
                    placeholder="Todas",
                    key="sl_platforms",
                )

            # Filtrar menciones
            filtered_mentions = [
                m for m in raw_mentions
                if date_start <= _mention_date(m) <= date_end
                and (not selected_platforms or
                     (m.get("plataforma_normalizada") or m.get("fuente", ""))[:30] in selected_platforms)
            ]

            if not filtered_mentions:
                filtered_mentions = raw_mentions  # fallback: mostrar todo si el filtro no matchea

            from collectors.social_listener import aggregate_insights
            social = aggregate_insights(filtered_mentions)
            total_mentions = social.get("total_mentions", 0)

            sentiment_dist = social.get("sentiment_distribution", {})

            # ── verbatim_card helper (defined early so drill-down can use it) ──
            def verbatim_card(v, css_class):
                texto = v.get("texto", "")
                fuente = v.get("fuente", "?")
                url = v.get("url") or ""
                fecha = v.get("fecha_aprox", "")
                fecha_html = f'<span class="verbatim-date">{fecha}</span>' if fecha and fecha != "desconocida" else ""
                source_inner = (
                    f'<a href="{url}" target="_blank" rel="noopener">{fuente}</a>'
                    if url else fuente
                )
                st.markdown(
                    f'<div class="verbatim {css_class}">'
                    f'  <div class="verbatim-text">"{texto}"</div>'
                    f'  <div class="verbatim-footer">'
                    f'    <span class="verbatim-source">{source_inner}</span>'
                    f'    {fecha_html}'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # ── Summary cards ──
            section_header("Resumen de Menciones", dot_color="blue")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="summary-card highlight"><div class="s-label">Total menciones</div><div class="s-value">{total_mentions}</div></div>', unsafe_allow_html=True)
            with c2:
                pct_pos = sentiment_dist.get("positivo", 0)
                st.markdown(f'<div class="summary-card"><div class="s-label">Positivas</div><div class="s-value" style="color:var(--green)">{pct_pos}%</div></div>', unsafe_allow_html=True)
            with c3:
                pct_neg = sentiment_dist.get("negativo", 0)
                st.markdown(f'<div class="summary-card"><div class="s-label">Negativas</div><div class="s-value" style="color:var(--red)">{pct_neg}%</div></div>', unsafe_allow_html=True)
            with c4:
                top_t = social.get("top_themes", [{}])[0].get("tema", "–") if social.get("top_themes") else "–"
                st.markdown(f'<div class="summary-card"><div class="s-label">Tema #1</div><div class="s-value" style="font-size:18px">{top_t}</div></div>', unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

            # ── Charts ──
            col_themes, col_sources = st.columns([3, 2])
            with col_themes:
                section_header("Temas más mencionados", dot_color="blue")
                top_themes = social.get("top_themes", [])
                if top_themes:
                    try:
                        import plotly.graph_objects as go
                        names = [t["tema"] for t in top_themes[:8]]
                        vals  = [t["count"] for t in top_themes[:8]]
                        bar_colors = ["#0467FC" if i == 0 else "#93B4FF" for i in range(len(names))]
                        fig = go.Figure(go.Bar(x=vals, y=names, orientation="h", marker_color=bar_colors))
                        fig.update_layout(
                            plot_bgcolor="white", paper_bgcolor="white",
                            font=dict(family="Helvetica Neue", size=12),
                            margin=dict(l=0, r=20, t=10, b=0),
                            xaxis=dict(showgrid=True, gridcolor="#F0F4F8"),
                            yaxis=dict(autorange="reversed"),
                            height=280,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except ImportError:
                        for t in top_themes[:6]:
                            st.write(f"• **{t['tema']}**: {t['count']} ({t['pct']}%)")

            with col_sources:
                section_header("Fuentes populares", dot_color="blue")
                by_source = social.get("by_source", {})
                if by_source:
                    import plotly.graph_objects as go
                    _src_items = list(by_source.items())[:6]
                    _src_labels = [s[0] for s in _src_items]
                    _src_vals   = [s[1] for s in _src_items]
                    _src_colors = ["#0467FC","#E53E3E","#38A169","#D69E2E","#718096","#9F7AEA"]
                    _fig_src = go.Figure(go.Pie(
                        labels=_src_labels, values=_src_vals, hole=0.52,
                        marker=dict(colors=_src_colors[:len(_src_labels)]),
                        textinfo="percent", textfont=dict(size=11),
                    ))
                    _fig_src.update_layout(
                        showlegend=True,
                        legend=dict(orientation="v", x=0.75, y=0.5, font=dict(size=11)),
                        margin=dict(l=0, r=0, t=4, b=4),
                        height=260, paper_bgcolor="white",
                        font=dict(family="Helvetica Neue"),
                    )
                    st.plotly_chart(_fig_src, use_container_width=True)

            # ── Distribución menciones por período / sentimiento ───
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            section_header("Distribución de menciones por sentimiento", dot_color="blue")
            _QUARTER_ORDER = ["2025-Q1","2025-Q2","2025-Q3","2025-Q4","2026-Q1","2026-Q2"]
            _QUARTER_LABEL = {"2025-Q1":"Q1 '25","2025-Q2":"Q2 '25","2025-Q3":"Q3 '25",
                               "2025-Q4":"Q4 '25","2026-Q1":"Q1 '26","2026-Q2":"Q2 '26"}
            from collections import defaultdict
            _trend_buckets = defaultdict(lambda: {"positivo":0,"negativo":0,"neutro":0,"mixto":0,"total":0})
            for _m in filtered_mentions:
                _fa = _m.get("fecha_aprox","desconocida")
                if _fa in _QUARTER_ORDER:
                    _s = _m.get("sentimiento","neutro")
                    _trend_buckets[_fa][_s] = _trend_buckets[_fa].get(_s,0) + 1
                    _trend_buckets[_fa]["total"] += 1
            _trend_periods = [q for q in _QUARTER_ORDER if q in _trend_buckets]
            if len(_trend_periods) >= 1:
                try:
                    import plotly.graph_objects as go
                    _xlabels = [_QUARTER_LABEL.get(p, p) for p in _trend_periods]
                    _neu_vals = [_trend_buckets[p].get("neutro",0) + _trend_buckets[p].get("mixto",0) for p in _trend_periods]
                    _neg_vals = [_trend_buckets[p].get("negativo",0) for p in _trend_periods]
                    _pos_vals = [_trend_buckets[p].get("positivo",0) for p in _trend_periods]
                    _fig_stack = go.Figure()
                    _fig_stack.add_trace(go.Bar(name="Neutral", x=_xlabels, y=_neu_vals,
                        marker_color="#718096", text=_neu_vals, textposition="inside",
                        textfont=dict(color="white", size=11)))
                    _fig_stack.add_trace(go.Bar(name="Negativo", x=_xlabels, y=_neg_vals,
                        marker_color="#E53E3E", text=_neg_vals, textposition="inside",
                        textfont=dict(color="white", size=11)))
                    _fig_stack.add_trace(go.Bar(name="Positivo", x=_xlabels, y=_pos_vals,
                        marker_color="#38A169", text=_pos_vals, textposition="inside",
                        textfont=dict(color="white", size=11)))
                    _fig_stack.update_layout(
                        barmode="stack",
                        plot_bgcolor="white", paper_bgcolor="white",
                        font=dict(family="Helvetica Neue", size=12),
                        margin=dict(l=0, r=20, t=10, b=0),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#F0F4F8", title="menciones"),
                        legend=dict(orientation="h", y=1.08, x=0),
                        height=300,
                    )
                    st.plotly_chart(_fig_stack, use_container_width=True)
                except ImportError:
                    for _p in _trend_periods:
                        _b = _trend_buckets[_p]
                        st.write(f"**{_QUARTER_LABEL.get(_p,_p)}** — neg {_b['negativo']} | pos {_b['positivo']} | neutro {_b['neutro']}")
            else:
                st.caption("Sin datos suficientes para mostrar tendencia temporal.")

            # ── Palabras que dominan (word cloud CSS) ─────────────
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            section_header("Palabras que dominan", dot_color="blue")
            import re as _re
            from collections import Counter as _Counter
            _STOP = set([
                "de","la","el","en","que","y","a","los","se","las","por","con","para",
                "un","una","es","son","lo","no","me","mi","su","sus","más","pero",
                "también","fue","como","si","ha","he","ya","era","muy","te","nos",
                "al","del","tu","le","puede","porque","están","está","han","tiene",
                "hacer","hay","sobre","cuando","este","esta","estos","estas","todo",
                "toda","todos","todas","bien","así","vez","sin","ni","o","e","u",
                "les","kavak","que","les","nos","os","le","me","nos","les","si",
                "the","and","for","are","this","that","with","from","they","have",
                "was","pero","más","había","tiene","para","sobre","desde","hasta",
                "ser","estar","ir","ver","dar","aunque","solo","mismo","cada",
                "otro","otra","otros","otras","aquí","allí","donde","cómo","quién",
            ])
            _all_words = []
            for _m in filtered_mentions:
                _txt = _m.get("texto","").lower()
                _words = _re.findall(r'\b[a-záéíóúüñ]{4,}\b', _txt)
                _all_words.extend([w for w in _words if w not in _STOP])
            _word_counts = _Counter(_all_words).most_common(45)
            if _word_counts:
                _max_c = _word_counts[0][1]
                _min_c = _word_counts[-1][1]
                _wc_colors = ["#0467FC","#0352C9","#E53E3E","#38A169","#D69E2E","#718096","#9F7AEA","#DD6B20"]
                _cloud_html = '<div style="padding:20px 10px;line-height:3;text-align:center">'
                for _i, (_word, _cnt) in enumerate(_word_counts):
                    _sz = 13 + int((_cnt - _min_c) / max(_max_c - _min_c, 1) * 22)
                    _fw = "800" if _sz > 26 else "600" if _sz > 18 else "400"
                    _col = _wc_colors[_i % len(_wc_colors)]
                    _cloud_html += (
                        f'<span style="font-size:{_sz}px;font-weight:{_fw};color:{_col};'
                        f'margin:0 10px;display:inline-block">{_word}</span>'
                    )
                _cloud_html += '</div>'
                st.markdown(_cloud_html, unsafe_allow_html=True)
            else:
                st.caption("Sin suficientes menciones para generar el word cloud.")

            # ── Crisis Radar ────────────────────────────────────
            _crisis = [m for m in filtered_mentions if m.get("intensidad", 0) >= 4 and m.get("sentimiento") == "negativo"]
            if _crisis:
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                section_header(f"Crisis Radar · {len(_crisis)} menciones de alto impacto", dot_color="red")
                _crisis_sorted = sorted(_crisis, key=lambda x: x.get("intensidad", 0), reverse=True)
                for _cm in _crisis_sorted[:6]:
                    _cfuente = _cm.get("fuente", "?")
                    _curl    = _cm.get("url") or ""
                    _ctext   = _cm.get("texto", "")[:220]
                    _cfecha  = _cm.get("fecha_aprox","")
                    _cint    = _cm.get("intensidad", 0)
                    _ctemas  = ", ".join(_cm.get("temas", []))
                    _csrc    = f'<a href="{_curl}" target="_blank">{_cfuente}</a>' if _curl else _cfuente
                    _badge   = "🔥 viral" if _cint == 5 else "⚡ alto impacto"
                    _bcol    = "#E53E3E" if _cint == 5 else "#D69E2E"
                    st.markdown(f"""
                    <div class="verbatim neg" style="border-left-color:{_bcol};background:#FFFAF0">
                      <div class="verbatim-text">"{_ctext}"</div>
                      <div class="verbatim-footer" style="gap:6px">
                        <span class="verbatim-source">{_csrc}</span>
                        <span class="verbatim-date">{_cfecha}</span>
                        <span style="font-size:11px;color:var(--text-muted)">{_ctemas}</span>
                        <span style="font-size:11px;background:{_bcol};color:white;padding:2px 8px;border-radius:10px;margin-left:auto">{_badge}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)

            # ── Drill-down por tema ─────────────────────────────
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            section_header("Drill-down por Tema", dot_color="purple")
            _all_themes_dd = [t["tema"] for t in social.get("top_themes", [])]
            if _all_themes_dd:
                _selected_theme = st.selectbox(
                    "Seleccioná un tema para ver sus menciones",
                    options=_all_themes_dd,
                    key="sl_theme_drill",
                )
                _theme_mentions = [m for m in filtered_mentions if _selected_theme in m.get("temas", [])]
                _theme_neg = [m for m in _theme_mentions if m.get("sentimiento") == "negativo"]
                _theme_pos = [m for m in _theme_mentions if m.get("sentimiento") == "positivo"]
                _tc1, _tc2, _tc3 = st.columns(3)
                with _tc1:
                    st.markdown(f'<div class="summary-card"><div class="s-label">Menciones</div><div class="s-value">{len(_theme_mentions)}</div></div>', unsafe_allow_html=True)
                with _tc2:
                    st.markdown(f'<div class="summary-card"><div class="s-label">Negativas</div><div class="s-value" style="color:var(--red)">{len(_theme_neg)}</div></div>', unsafe_allow_html=True)
                with _tc3:
                    st.markdown(f'<div class="summary-card"><div class="s-label">Positivas</div><div class="s-value" style="color:var(--green)">{len(_theme_pos)}</div></div>', unsafe_allow_html=True)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                _tab_dn, _tab_dp = st.tabs([f"😤 Negativos ({len(_theme_neg)})", f"😊 Positivos ({len(_theme_pos)})"])
                with _tab_dn:
                    for _v in sorted(_theme_neg, key=lambda x: x.get("intensidad",0), reverse=True)[:8]:
                        verbatim_card(_v, "neg")
                with _tab_dp:
                    for _v in sorted(_theme_pos, key=lambda x: x.get("intensidad",0), reverse=True)[:8]:
                        verbatim_card(_v, "pos")

            # ── Narrativas ──
            social_insights = analysis.get("social_insights", [])
            if social_insights:
                section_header("Narrativas detectadas", dot_color="purple", count=len(social_insights))
                col_l, col_r = st.columns(2)
                mid = (len(social_insights) + 1) // 2
                with col_l:
                    for si in social_insights[:mid]:
                        render_kpi_card(si, "social")
                with col_r:
                    for si in social_insights[mid:]:
                        render_kpi_card(si, "social")

            # ── Verbatims ──
            verbatims = social.get("verbatims", {})
            if verbatims:
                section_header("Comentarios", dot_color="blue")

                tab_pos, tab_neu, tab_neg = st.tabs(["😊  Positivos", "😐  Neutrales", "😤  Negativos"])
                with tab_pos:
                    items = verbatims.get("positivo", [])[:8]
                    if items:
                        for v in items:
                            verbatim_card(v, "pos")
                    else:
                        st.markdown('<p style="color:var(--text-muted);font-size:13px;padding:12px 0">Sin comentarios positivos en este período.</p>', unsafe_allow_html=True)
                with tab_neu:
                    items = verbatims.get("neutro", [])[:4] + verbatims.get("mixto", [])[:4]
                    if items:
                        for v in items[:8]:
                            verbatim_card(v, "neu")
                    else:
                        st.markdown('<p style="color:var(--text-muted);font-size:13px;padding:12px 0">Sin comentarios neutrales en este período.</p>', unsafe_allow_html=True)
                with tab_neg:
                    items = verbatims.get("negativo", [])[:8]
                    if items:
                        for v in items:
                            verbatim_card(v, "neg")
                    else:
                        st.markdown('<p style="color:var(--text-muted);font-size:13px;padding:12px 0">Sin comentarios negativos en este período.</p>', unsafe_allow_html=True)

    # ════════════════════════════════════════
    # TAB 3 — ACCIONABLES GROWTH
    # ════════════════════════════════════════
    with tab3:
        if not has_api_key:
            empty_state(
                "🔑",
                "API key requerida",
                "Los accionables se generan con Claude analizando BHT + Social Listening.<br>"
                "Configurá <code>ANTHROPIC_API_KEY</code> para habilitar esta sección."
            )
        else:
            actionables = analysis.get("accionables_growth", [])

            if filter_priority:
                actionables = [a for a in actionables if a.get("prioridad") in filter_priority]
            if filter_lever:
                actionables = [a for a in actionables if a.get("lever") in filter_lever]

            if not actionables:
                empty_state("⚡", "Sin accionables disponibles", "Ajustá los filtros o corrés el análisis primero.")
            else:
                total_act = len(actionables)
                altas = sum(1 for a in actionables if a.get("prioridad") == "alta")
                immediates = sum(1 for a in actionables if "inmediato" in a.get("timeline_sugerido", ""))

                section_header("Resumen de Accionables", dot_color="blue")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f'<div class="summary-card highlight"><div class="s-label">Total accionables</div><div class="s-value">{total_act}</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="summary-card"><div class="s-label">Prioridad alta</div><div class="s-value" style="color:var(--red)">{altas}</div></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="summary-card"><div class="s-label">Inmediatos</div><div class="s-value" style="color:var(--purple)">{immediates}</div></div>', unsafe_allow_html=True)

                st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

                lever_labels = {
                    "mensajería_y_propuesta_de_valor": "💬 Mensajería y propuesta de valor",
                    "contenido_y_creativos": "🎨 Contenido y creativos",
                    "awareness_y_alcance": "📡 Awareness y alcance",
                    "consideracion_y_enganche": "🎯 Consideración y enganche",
                    "confianza_y_prueba_social": "✅ Confianza y prueba social",
                    "precio_como_comunicacion": "💰 Precio como comunicación",
                }
                by_lever = {}
                for a in actionables:
                    by_lever.setdefault(a.get("lever", "sin_categorizar"), []).append(a)

                def lever_score(acts):
                    m = {"alta": 3, "media": 2, "baja": 1}
                    return sum(m.get(a.get("prioridad", "baja"), 0) for a in acts)

                sorted_levers = sorted(by_lever.items(), key=lambda x: -lever_score(x[1]))

                section_header("Por lever de marketing", dot_color="blue", count=len(sorted_levers))
                for lever, lever_actions in sorted_levers:
                    label = lever_labels.get(lever, lever.replace("_", " ").title())
                    with st.expander(f"{label}  ({len(lever_actions)} accionables)", expanded=lever in ["contenido_y_creativos", "mensajería_y_propuesta_de_valor", "confianza_y_prueba_social"]):
                        for act in sorted(lever_actions, key=lambda x: {"alta": 0, "media": 1, "baja": 2}.get(x.get("prioridad"), 1)):
                            render_actionable(act)

                # Temas excluidos
                temas_excluidos = analysis.get("temas_excluidos", [])
                if temas_excluidos:
                    with st.expander("ℹ️ Temas fuera del scope de Growth"):
                        for te in temas_excluidos:
                            reco = te.get("recomendacion_para_otras_areas", "")
                            st.markdown(f"""
                            <div style="padding:10px 0;border-bottom:1px solid var(--border)">
                              <strong style="font-size:13px">{te.get('tema','')}</strong>
                              <span class="tag tag-gray" style="margin-left:8px">{te.get('mencion_frecuencia','')}</span><br>
                              <span style="font-size:12px;color:var(--text-muted)">{te.get('razon_exclusion','')}</span>
                              {"<br><span style='font-size:12px;color:var(--kavak-blue)'>→ "+reco+"</span>" if reco else ""}
                            </div>
                            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
