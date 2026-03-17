"""
dashboard/app.py
Streamlit dashboard — Kavak Brand Intelligence
3 tabs: Brand Health | Social Listening | Accionables Growth

Run: streamlit run dashboard/app.py
"""

import os
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

# ──────────────────────────────────────────────
# PAGE CONFIG (debe ir primero en Streamlit)
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Kavak Brand Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — Kavak Brand System
# ──────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
    
    :root {
        --kavak-blue: #0057FF;
        --kavak-dark: #000000;
        --kavak-white: #FFFFFF;
        --kavak-gray-100: #F5F5F5;
        --kavak-gray-200: #E5E5E5;
        --kavak-gray-500: #737373;
        --kavak-gray-800: #1A1A1A;
        --positive: #22C55E;
        --negative: #EF4444;
        --warning: #F59E0B;
        --mixed: #A855F7;
    }
    
    html, body, [class*="css"] {
        font-family: 'DM Sans', 'Helvetica Neue', Helvetica, sans-serif;
    }
    
    /* Hide default streamlit header */
    header[data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Main container */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* ─── TOP NAV BAR ─── */
    .brand-header {
        background: var(--kavak-dark);
        color: var(--kavak-white);
        padding: 16px 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 3px solid var(--kavak-blue);
        margin-bottom: 0;
    }
    .brand-header h1 {
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        color: white;
    }
    .brand-header h1 span { color: var(--kavak-blue); }
    .brand-header .subtitle {
        font-size: 12px;
        color: #888;
        font-weight: 400;
        margin-top: 2px;
    }
    .last-updated {
        font-size: 11px;
        color: #555;
        font-family: 'DM Mono', monospace;
    }
    
    /* ─── CONTENT AREA ─── */
    .content-area {
        padding: 32px 40px;
    }
    
    /* ─── METRIC CARDS ─── */
    .metric-card {
        background: white;
        border: 1px solid var(--kavak-gray-200);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: box-shadow 0.2s;
    }
    .metric-card:hover { box-shadow: 0 4px 20px rgba(0,87,255,0.1); }
    .metric-card .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: var(--kavak-dark);
        line-height: 1;
        margin-bottom: 4px;
    }
    .metric-card .metric-label {
        font-size: 12px;
        color: var(--kavak-gray-500);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .metric-delta {
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }
    .delta-up { color: var(--positive); }
    .delta-down { color: var(--negative); }
    .delta-flat { color: var(--kavak-gray-500); }
    
    /* ─── INSIGHT CARDS ─── */
    .insight-card {
        background: white;
        border: 1px solid var(--kavak-gray-200);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid var(--kavak-blue);
    }
    .insight-card.urgencia-alta { border-left-color: var(--negative); }
    .insight-card.urgencia-media { border-left-color: var(--warning); }
    .insight-card.urgencia-baja { border-left-color: var(--positive); }
    .insight-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--kavak-dark);
        margin-bottom: 6px;
    }
    .insight-text {
        font-size: 13px;
        color: var(--kavak-gray-500);
        line-height: 1.5;
    }
    
    /* ─── ACTIONABLE CARDS ─── */
    .action-card {
        background: white;
        border: 1px solid var(--kavak-gray-200);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
    }
    .action-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        background: var(--kavak-blue);
    }
    .action-card.prioridad-alta::before { background: var(--negative); }
    .action-card.prioridad-media::before { background: var(--warning); }
    .action-card.prioridad-baja::before { background: var(--positive); }
    .action-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--kavak-dark);
        margin-bottom: 8px;
    }
    .action-desc {
        font-size: 13px;
        color: #444;
        line-height: 1.6;
        margin-bottom: 12px;
    }
    .action-hypothesis {
        background: #F0F4FF;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 12px;
        color: var(--kavak-blue);
        font-style: italic;
        margin-bottom: 12px;
    }
    .action-meta {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }
    .tag {
        background: var(--kavak-gray-100);
        color: var(--kavak-gray-500);
        border-radius: 4px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 500;
    }
    .tag.lever { background: #E0EAFF; color: var(--kavak-blue); }
    .tag.priority-alta { background: #FEE2E2; color: var(--negative); }
    .tag.priority-media { background: #FEF3C7; color: #D97706; }
    .tag.priority-baja { background: #DCFCE7; color: #16A34A; }
    .tag.timeline { background: #F5F3FF; color: #7C3AED; }
    
    /* ─── SENTIMENT BADGES ─── */
    .sentiment-positivo { color: var(--positive); font-weight: 600; }
    .sentiment-negativo { color: var(--negative); font-weight: 600; }
    .sentiment-mixto { color: var(--mixed); font-weight: 600; }
    .sentiment-neutro { color: var(--kavak-gray-500); font-weight: 600; }
    
    /* ─── VERBATIM ─── */
    .verbatim-card {
        background: var(--kavak-gray-100);
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 8px;
        font-size: 13px;
        line-height: 1.5;
        color: #333;
    }
    .verbatim-source {
        font-size: 11px;
        color: var(--kavak-gray-500);
        font-family: 'DM Mono', monospace;
        margin-top: 6px;
    }
    
    /* ─── SECTION HEADERS ─── */
    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: var(--kavak-dark);
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--kavak-gray-200);
    }
    
    /* ─── EXECUTIVE SUMMARY ─── */
    .exec-summary {
        background: linear-gradient(135deg, #000 0%, #1a1a2e 100%);
        color: white;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    }
    .exec-summary::after {
        content: '';
        position: absolute;
        bottom: -30px; right: -30px;
        width: 120px; height: 120px;
        background: var(--kavak-blue);
        border-radius: 50%;
        opacity: 0.15;
    }
    .exec-summary h3 {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--kavak-blue);
        margin-bottom: 12px;
    }
    .exec-summary p {
        font-size: 15px;
        line-height: 1.7;
        color: #ddd;
        margin: 0;
    }
    
    /* ─── EMPTY STATE ─── */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: var(--kavak-gray-500);
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; }
    .empty-state h3 { font-size: 18px; color: var(--kavak-dark); }
    .empty-state p { font-size: 14px; }
    
    /* ─── TABS ─── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--kavak-gray-100);
        border-radius: 10px;
        padding: 4px;
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        color: var(--kavak-gray-500);
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--kavak-dark);
        font-weight: 600;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
    
    /* ─── TREND CHART BAR ─── */
    .trend-bar-container {
        background: var(--kavak-gray-100);
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
        margin-top: 8px;
    }
    .trend-bar-fill {
        height: 100%;
        border-radius: 6px;
        background: var(--kavak-blue);
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DATA LOADING (con cache de Streamlit)
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def load_all_data(force_refresh: bool = False):
    """Carga BHT + social + análisis. Cachea 1 hora."""
    from collectors.bht_loader import load_bht_files, get_bht_summary_for_llm
    from collectors.social_listener import run_social_listening, aggregate_insights, get_social_summary_for_llm
    from analyzer import run_analysis

    # BHT
    all_waves = load_bht_files("data")
    bht_summary = get_bht_summary_for_llm(all_waves)

    # Social listening
    mentions = run_social_listening(
        max_queries=15,
        cache_file="outputs/social_listening_cache.json",
    )
    aggregated_social = aggregate_insights(mentions)
    social_summary = get_social_summary_for_llm(aggregated_social)

    # Análisis
    analysis = run_analysis(
        bht_summary=bht_summary,
        social_summary=social_summary,
        force_refresh=force_refresh,
    )

    return {
        "waves": all_waves,
        "mentions": mentions,
        "social": aggregated_social,
        "analysis": analysis,
    }


# ──────────────────────────────────────────────
# HELPER COMPONENTS
# ──────────────────────────────────────────────

def render_header():
    import datetime
    now = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    st.markdown(f"""
    <div class="brand-header">
        <div>
            <h1><span>Kavak</span> Brand Intelligence</h1>
            <div class="subtitle">Brand Health · Social Listening · Accionables Growth</div>
        </div>
        <div class="last-updated">Actualizado: {now}</div>
    </div>
    """, unsafe_allow_html=True)


def render_exec_summary(analysis: dict):
    summary = analysis.get("executive_summary", "Sin resumen disponible.")
    st.markdown(f"""
    <div class="exec-summary">
        <h3>Executive Summary</h3>
        <p>{summary}</p>
    </div>
    """, unsafe_allow_html=True)


def render_insight_card(insight: dict, insight_type: str = "brand"):
    if insight_type == "brand":
        urgencia = insight.get("urgencia", "baja")
        tendencia_icon = {"creciendo": "↑", "cayendo": "↓", "estable": "→"}.get(
            insight.get("tendencia", ""), "–"
        )
        st.markdown(f"""
        <div class="insight-card urgencia-{urgencia}">
            <div class="insight-title">{tendencia_icon} {insight.get('metrica', '?')}</div>
            <div class="insight-text">{insight.get('interpretacion', '')}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        sent = insight.get("sentimiento_neto", "neutro")
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">
                <span class="sentiment-{sent}">{sent.upper()}</span> · {insight.get('tema', '?')}
            </div>
            <div class="insight-text">{insight.get('narrativa', '')}</div>
        </div>
        """, unsafe_allow_html=True)


def render_actionable_card(action: dict):
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
    lever_label = lever_labels.get(lever, lever)
    channels = ", ".join(action.get("canales_sugeridos", []))
    formats_str = ", ".join(action.get("formato_sugerido", []))
    timeline = action.get("timeline_sugerido", "")

    st.markdown(f"""
    <div class="action-card prioridad-{priority}">
        <div class="action-title">{action.get('titulo', 'Sin título')}</div>
        <div class="action-desc">{action.get('descripcion', '')}</div>
        <div class="action-hypothesis">💡 {action.get('hipotesis', '')}</div>
        <div class="action-meta">
            <span class="tag lever">{lever_label}</span>
            <span class="tag priority-{priority}">Prioridad {priority.upper()}</span>
            {'<span class="tag timeline">⏱ ' + timeline + '</span>' if timeline else ''}
            {'<span class="tag">📱 ' + channels + '</span>' if channels else ''}
            {'<span class="tag">🎬 ' + formats_str + '</span>' if formats_str else ''}
        </div>
        <div style="margin-top: 12px; font-size: 12px; color: #888;">
            <strong>Evidencia:</strong> {action.get('evidencia', '')} &nbsp;·&nbsp;
            <strong>KPI:</strong> {action.get('kpi_de_exito', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_verbatim(verbatim: dict, sentiment: str):
    texto = verbatim.get("texto", "")
    fuente = verbatim.get("fuente", "?")
    fecha = verbatim.get("fecha_aprox", "")
    st.markdown(f"""
    <div class="verbatim-card">
        "{texto}"
        <div class="verbatim-source">{fuente} {'· ' + fecha if fecha and fecha != 'desconocida' else ''}</div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────

def main():
    render_header()

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown("### ⚙️ Controles")
        force_refresh = st.button("🔄 Actualizar datos", use_container_width=True)
        st.divider()
        st.markdown("**Filtros de Accionables**")
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
        st.markdown("**Datos**")
        if st.button("🗑️ Limpiar cache", use_container_width=True):
            for cache_f in ["outputs/social_listening_cache.json", "outputs/analysis_cache.json"]:
                if Path(cache_f).exists():
                    Path(cache_f).unlink()
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
    social = data.get("social", {})
    waves = data.get("waves", {})

    # ── EXEC SUMMARY ──
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    render_exec_summary(analysis)

    # ── TABS ──
    tab1, tab2, tab3 = st.tabs([
        "📊 Brand Health Tracker",
        "🌐 Social Listening",
        "⚡ Accionables Growth",
    ])

    # ════════════════════════════════════════
    # TAB 1: BRAND HEALTH
    # ════════════════════════════════════════
    with tab1:
        st.markdown('<div class="section-header">Brand Health Tracker por Ola</div>', unsafe_allow_html=True)

        insights_bht = analysis.get("brand_health_insights", [])

        if not waves and not insights_bht:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">📋</div>
                <h3>No hay datos BHT cargados</h3>
                <p>Colocá tus archivos BHT en la carpeta <code>/data</code> con el formato:<br>
                <code>bht_ola1.csv</code>, <code>bht_ola2.xlsx</code>, etc.</p>
                <p>Corrés <code>python run.py --sample</code> para generar datos de muestra.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Métricas clave (top cards)
            if insights_bht:
                st.markdown("#### Tendencias Detectadas")
                cols = st.columns(min(len(insights_bht), 4))
                for i, insight in enumerate(insights_bht[:4]):
                    with cols[i % 4]:
                        tend = insight.get("tendencia", "")
                        delta_color = "up" if tend == "creciendo" else "down" if tend == "cayendo" else "flat"
                        icon = "↑" if tend == "creciendo" else "↓" if tend == "cayendo" else "→"
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{icon}</div>
                            <div class="metric-label">{insight.get('metrica', '?')}</div>
                            <div class="metric-delta delta-{delta_color}">
                                {tend.capitalize()} · urgencia {insight.get('urgencia', '?')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("")

            # Wave comparison chart si hay datos reales
            if waves:
                try:
                    import pandas as pd
                    import plotly.graph_objects as go
                    from collectors.bht_loader import build_wave_comparison

                    comparison = build_wave_comparison(waves)
                    if comparison:
                        st.markdown("#### Evolución por Ola")
                        # Selector de métricas
                        available_metrics = [m for m, vals in comparison.items()
                                             if any(v is not None for v in vals.values())]
                        selected_metrics = st.multiselect(
                            "Seleccioná métricas a visualizar:",
                            options=available_metrics,
                            default=available_metrics[:5] if len(available_metrics) >= 5 else available_metrics,
                        )
                        if selected_metrics:
                            fig = go.Figure()
                            wave_names = sorted(set(w for vals in comparison.values() for w in vals.keys()))
                            colors = ["#0057FF", "#22C55E", "#EF4444", "#F59E0B", "#A855F7", "#06B6D4"]

                            for idx, metric in enumerate(selected_metrics):
                                y_vals = [comparison[metric].get(w) for w in wave_names]
                                fig.add_trace(go.Scatter(
                                    x=wave_names, y=y_vals,
                                    name=metric,
                                    mode="lines+markers",
                                    line=dict(color=colors[idx % len(colors)], width=2.5),
                                    marker=dict(size=8),
                                ))

                            fig.update_layout(
                                plot_bgcolor="white",
                                paper_bgcolor="white",
                                font=dict(family="DM Sans", size=12),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                                margin=dict(l=0, r=0, t=40, b=0),
                                xaxis=dict(showgrid=False),
                                yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                            )
                            st.plotly_chart(fig, use_container_width=True)
                except ImportError:
                    st.info("Instalá `plotly` para ver los gráficos: `pip install plotly`")

            # Insights detallados
            if insights_bht:
                st.markdown("#### Insights de Brand Health")
                col_left, col_right = st.columns(2)
                mid = len(insights_bht) // 2
                with col_left:
                    for ins in insights_bht[:mid]:
                        render_insight_card(ins, "brand")
                with col_right:
                    for ins in insights_bht[mid:]:
                        render_insight_card(ins, "brand")

            # Brechas detectadas
            brechas = analysis.get("brechas_detectadas", [])
            if brechas:
                st.markdown("#### Brechas Percepción / Realidad")
                for b in brechas:
                    impact = b.get("impacto", "bajo")
                    color = "#EF4444" if impact == "alto" else "#F59E0B" if impact == "medio" else "#22C55E"
                    st.markdown(f"""
                    <div class="insight-card" style="border-left-color: {color}">
                        <div class="insight-title">⚠️ {b.get('brecha', '')}</div>
                        <div class="insight-text">
                            {'<strong>BHT:</strong> ' + b.get('evidencia_bht', '') if b.get('evidencia_bht') else ''}
                            {'<br><strong>Social:</strong> ' + b.get('evidencia_social', '') if b.get('evidencia_social') else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # TAB 2: SOCIAL LISTENING
    # ════════════════════════════════════════
    with tab2:
        st.markdown('<div class="section-header">Social Listening — Kavak México</div>', unsafe_allow_html=True)

        total_mentions = social.get("total_mentions", 0)
        if total_mentions == 0:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">🌐</div>
                <h3>Sin datos de social listening</h3>
                <p>Seteá <code>ANTHROPIC_API_KEY</code> y corrés <code>python run.py</code>.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Metrics row
            sentiment_dist = social.get("sentiment_distribution", {})
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_mentions}</div>
                    <div class="metric-label">Total menciones</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                pct_pos = sentiment_dist.get("positivo", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #22C55E">{pct_pos}%</div>
                    <div class="metric-label">Menciones positivas</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                pct_neg = sentiment_dist.get("negativo", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #EF4444">{pct_neg}%</div>
                    <div class="metric-label">Menciones negativas</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                top_theme = social.get("top_themes", [{}])[0].get("tema", "–") if social.get("top_themes") else "–"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size: 20px">{top_theme}</div>
                    <div class="metric-label">Tema #1</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("")

            # Charts
            col_themes, col_sources = st.columns([3, 2])

            with col_themes:
                st.markdown("#### Temas más mencionados")
                top_themes = social.get("top_themes", [])
                if top_themes:
                    try:
                        import plotly.graph_objects as go
                        themes_names = [t["tema"] for t in top_themes[:8]]
                        themes_vals = [t["count"] for t in top_themes[:8]]
                        colors_bar = ["#0057FF" if i == 0 else "#93B4FF" for i in range(len(themes_names))]

                        fig = go.Figure(go.Bar(
                            x=themes_vals, y=themes_names,
                            orientation="h",
                            marker_color=colors_bar,
                        ))
                        fig.update_layout(
                            plot_bgcolor="white", paper_bgcolor="white",
                            font=dict(family="DM Sans", size=12),
                            margin=dict(l=0, r=20, t=10, b=0),
                            xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                            yaxis=dict(autorange="reversed"),
                            height=300,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except ImportError:
                        for t in top_themes[:6]:
                            st.write(f"• **{t['tema']}**: {t['count']} ({t['pct']}%)")

            with col_sources:
                st.markdown("#### Por Fuente")
                by_source = social.get("by_source", {})
                if by_source:
                    for source, count in list(by_source.items())[:8]:
                        pct = round(count / total_mentions * 100, 1) if total_mentions else 0
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; 
                                    padding: 6px 0; border-bottom: 1px solid #F0F0F0;
                                    font-size: 13px;">
                            <span>{source}</span>
                            <span style="color: #0057FF; font-weight: 600">{count} ({pct}%)</span>
                        </div>
                        """, unsafe_allow_html=True)

            # Social Insights
            social_insights = analysis.get("social_insights", [])
            if social_insights:
                st.markdown("#### Narrativas Detectadas")
                col_l, col_r = st.columns(2)
                mid = len(social_insights) // 2 + len(social_insights) % 2
                with col_l:
                    for si in social_insights[:mid]:
                        render_insight_card(si, "social")
                with col_r:
                    for si in social_insights[mid:]:
                        render_insight_card(si, "social")

            # Verbatims
            verbatims = social.get("verbatims", {})
            if verbatims:
                st.markdown("#### Verbatims")
                v_tab1, v_tab2, v_tab3 = st.tabs(["😤 Negativos", "😊 Positivos", "😐 Mixtos"])

                with v_tab1:
                    negs = verbatims.get("negativo", [])
                    if negs:
                        for v in negs[:8]:
                            render_verbatim(v, "negativo")
                    else:
                        st.info("Sin menciones negativas encontradas.")

                with v_tab2:
                    poss = verbatims.get("positivo", [])
                    if poss:
                        for v in poss[:8]:
                            render_verbatim(v, "positivo")
                    else:
                        st.info("Sin menciones positivas encontradas.")

                with v_tab3:
                    mixs = verbatims.get("mixto", [])
                    if mixs:
                        for v in mixs[:8]:
                            render_verbatim(v, "mixto")
                    else:
                        st.info("Sin menciones mixtas.")

    # ════════════════════════════════════════
    # TAB 3: ACCIONABLES GROWTH
    # ════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-header">Accionables — Growth & Content</div>', unsafe_allow_html=True)
        st.caption("Solo palancas de marketing, mensajería y contenido. Sin operaciones ni pricing.")

        actionables = analysis.get("accionables_growth", [])

        # Filtrar por sidebar
        if filter_priority:
            actionables = [a for a in actionables if a.get("prioridad") in filter_priority]
        if filter_lever:
            actionables = [a for a in actionables if a.get("lever") in filter_lever]

        if not actionables:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">⚡</div>
                <h3>Sin accionables disponibles</h3>
                <p>Ajustá los filtros o corrés el análisis primero.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Summary row
            total_act = len(actionables)
            altas = sum(1 for a in actionables if a.get("prioridad") == "alta")
            immediates = sum(1 for a in actionables if "inmediato" in a.get("timeline_sugerido", ""))

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value">{total_act}</div>
                    <div class="metric-label">Accionables totales</div>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color: #EF4444">{altas}</div>
                    <div class="metric-label">Prioridad alta</div>
                </div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color: #7C3AED">{immediates}</div>
                    <div class="metric-label">Accionables inmediatos</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("")

            # Por lever
            lever_labels = {
                "mensajería_y_propuesta_de_valor": "💬 Mensajería y propuesta de valor",
                "contenido_y_creativos": "🎨 Contenido y creativos",
                "awareness_y_alcance": "📡 Awareness y alcance",
                "consideracion_y_enganche": "🎯 Consideración y enganche",
                "confianza_y_prueba_social": "✅ Confianza y prueba social",
                "precio_como_comunicacion": "💰 Precio como comunicación",
            }

            # Agrupar por lever
            by_lever = {}
            for a in actionables:
                lever = a.get("lever", "sin_categorizar")
                by_lever.setdefault(lever, []).append(a)

            # Ordenar levers por prioridad (los que tienen más alta primero)
            def lever_score(lever_actions):
                priority_map = {"alta": 3, "media": 2, "baja": 1}
                return sum(priority_map.get(a.get("prioridad", "baja"), 0) for a in lever_actions)

            sorted_levers = sorted(by_lever.items(), key=lambda x: -lever_score(x[1]))

            for lever, lever_actions in sorted_levers:
                with st.expander(
                    f"{lever_labels.get(lever, lever)} ({len(lever_actions)} accionables)",
                    expanded=(lever in ["contenido_y_creativos", "mensajería_y_propuesta_de_valor", "confianza_y_prueba_social"]),
                ):
                    for action in sorted(lever_actions, key=lambda x: {"alta": 0, "media": 1, "baja": 2}.get(x.get("prioridad"), 1)):
                        render_actionable_card(action)

            # Temas excluidos (transparencia)
            temas_excluidos = analysis.get("temas_excluidos", [])
            if temas_excluidos:
                with st.expander("ℹ️ Temas detectados pero fuera del scope de Growth"):
                    for te in temas_excluidos:
                        st.markdown(f"""
                        <div style="padding: 10px 0; border-bottom: 1px solid #F0F0F0;">
                            <strong>{te.get('tema', '')}</strong> 
                            <span style="color: #888; font-size: 12px"> · frecuencia {te.get('mencion_frecuencia', '?')}</span><br>
                            <span style="font-size: 13px; color: #555">{te.get('razon_exclusion', '')}</span>
                            {('<br><span style="font-size: 12px; color: #0057FF">→ ' + te.get('recomendacion_para_otras_areas', '') + '</span>') if te.get('recomendacion_para_otras_areas') else ''}
                        </div>
                        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
