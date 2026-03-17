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
    page_title="Kavak Brand Intelligence",
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
    padding-bottom: 10px;
    border-bottom: 2px solid var(--border);
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
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
  }
  .kpi-block {
    background: #F9FAFB;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
    position: relative;
  }
  .kpi-block:hover {
    background: #EBF2FF;
    border-color: var(--kavak-blue);
    box-shadow: 0 2px 8px rgba(4,103,252,0.08);
  }
  .kpi-block[open] {
    background: #EBF2FF;
    border-color: var(--kavak-blue);
  }
  .kpi-block > summary {
    list-style: none;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
    outline: none;
  }
  .kpi-block > summary::-webkit-details-marker { display: none; }
  .kpi-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--text-muted);
    margin-bottom: 5px;
  }
  .kpi-value {
    font-size: 26px;
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

  /* ─── VERBATIM ─── */
  .verbatim {
    background: var(--bg);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 13px;
    line-height: 1.55;
    color: #2D3748;
    border-left: 3px solid var(--border);
  }
  .verbatim.neg { border-left-color: var(--red); }
  .verbatim.pos { border-left-color: var(--green); }
  .verbatim.mix { border-left-color: var(--purple); }
  .verbatim-source {
    font-size: 11px;
    color: var(--text-light);
    margin-top: 6px;
    font-family: 'Courier New', monospace;
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
    if has_api_key:
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
    now = datetime.datetime.now().strftime("%d %b %Y")
    api_badge = "" if has_api_key else '<span class="api-badge-off">⚠ Sin API key</span>'
    st.markdown(f"""
    <div class="navbar">
      <div class="navbar-brand">
        {get_logo_html()}
        <div class="navbar-divider"></div>
        <span class="navbar-title">Brand Intelligence</span>
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
        force_refresh = st.button("🔄 Actualizar datos", use_container_width=True)
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
        if not has_api_key:
            st.divider()
            st.info("⚠️ Social Listening y Accionables requieren `ANTHROPIC_API_KEY`.", icon="🔑")
        st.divider()
        if st.button("🗑️ Limpiar cache", use_container_width=True):
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

    # ── EXEC SUMMARY BANNER ──
    exec_text = analysis.get("executive_summary") or (
        "Kavak México muestra un crecimiento sostenido de marca entre W0 (Jul 2020) y W12 (Dic 2025): "
        "el Top of Mind pasó de <strong>3.3%</strong> a <strong>53%</strong>, la Awareness Asistida de <strong>26%</strong> a <strong>84%</strong> "
        "y la Consideración de <strong>5%</strong> a <strong>63%</strong>. "
        "El NPS alcanzó <strong>53 puntos</strong> en W12, con un Brand Equity Index de <strong>84</strong>. "
        "La marca se consolidó como líder indiscutida en seminuevos en México en solo 5 años."
    )
    st.markdown(f"""
    <div class="exec-banner">
      <div class="e-eyebrow">Executive Summary · BHT México W0–W12 (2020–2025)</div>
      <div class="e-text">{exec_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──
    tab1, tab2, tab3 = st.tabs([
        "📊  Brand Health Tracker",
        "🌐  Social Listening",
        "⚡  Accionables Growth",
    ])

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

            section_header(f"Brand Health — Última Ola ({latest_label})", dot_color="blue")

            cards_html = '<div class="kpi-grid">'
            for (col_name, label, color, is_pct) in METRIC_CONFIG:
                if col_name not in pivot.columns:
                    continue
                val = pv(col_name)
                if val is None:
                    continue
                prev_val = pv(col_name, prev_label) if prev_label else None
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

                _, def_text = METRIC_DEFINITIONS.get(col_name, ("", "Sin definición disponible."))
                detail_html = build_detail(col_name, val, suffix, def_text)

                cards_html += f"""
                <details class="kpi-block" style="border-top:3px solid {color}">
                  <summary>
                    <div>
                      <div class="kpi-label">{label.upper()}</div>
                      <div class="kpi-value" style="color:{color}">{val_str}</div>
                      {sub_html}
                    </div>
                    <div class="kpi-right">
                      {delta_html}
                      <span class="kpi-arrow">▼</span>
                    </div>
                  </summary>
                  <div class="kpi-detail">{detail_html}</div>
                </details>"""

            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)

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

        if not has_api_key:
            empty_state(
                "🔑",
                "API key requerida",
                "Social Listening usa Claude API + web_search para rastrear menciones en tiempo real.<br>"
                "Configurá <code>ANTHROPIC_API_KEY</code> y volvé a correr el dashboard."
            )
        elif total_mentions == 0:
            empty_state("🌐", "Sin datos de social listening", "Corrés <code>python run.py</code> para recolectar menciones.")
        else:
            sentiment_dist = social.get("sentiment_distribution", {})

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
                section_header("Por fuente", dot_color="blue")
                by_source = social.get("by_source", {})
                if by_source:
                    for source, count in list(by_source.items())[:8]:
                        pct = round(count / total_mentions * 100, 1) if total_mentions else 0
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;padding:8px 0;
                             border-bottom:1px solid var(--border);font-size:13px">
                          <span style="color:var(--text)">{source}</span>
                          <span style="color:var(--kavak-blue);font-weight:600">{count} <span style="color:var(--text-muted);font-weight:400">({pct}%)</span></span>
                        </div>
                        """, unsafe_allow_html=True)

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
                section_header("Verbatims", dot_color="blue")
                v1, v2, v3 = st.tabs(["😤 Negativos", "😊 Positivos", "😐 Mixtos"])
                with v1:
                    for v in verbatims.get("negativo", [])[:8]:
                        fecha = v.get("fecha_aprox", "")
                        st.markdown(f'<div class="verbatim neg">"{v.get("texto","")}"<div class="verbatim-source">{v.get("fuente","?")}{"  ·  "+fecha if fecha and fecha!="desconocida" else ""}</div></div>', unsafe_allow_html=True)
                with v2:
                    for v in verbatims.get("positivo", [])[:8]:
                        fecha = v.get("fecha_aprox", "")
                        st.markdown(f'<div class="verbatim pos">"{v.get("texto","")}"<div class="verbatim-source">{v.get("fuente","?")}{"  ·  "+fecha if fecha and fecha!="desconocida" else ""}</div></div>', unsafe_allow_html=True)
                with v3:
                    for v in verbatims.get("mixto", [])[:8]:
                        fecha = v.get("fecha_aprox", "")
                        st.markdown(f'<div class="verbatim mix">"{v.get("texto","")}"<div class="verbatim-source">{v.get("fuente","?")}{"  ·  "+fecha if fecha and fecha!="desconocida" else ""}</div></div>', unsafe_allow_html=True)

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
