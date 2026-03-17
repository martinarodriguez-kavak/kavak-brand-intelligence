"""
run.py — Kavak Brand Intelligence Dashboard
Orchestrator principal: carga datos, corre análisis, lanza dashboard.

USO:
    python run.py                    # pipeline completo + lanza dashboard
    python run.py --collect-only     # solo recolecta datos (BHT + social)
    python run.py --analyze-only     # solo corre análisis (usa cache de social)
    python run.py --dashboard        # solo lanza el dashboard (usa cache completo)
    python run.py --refresh          # fuerza refresh de todo (ignora cache)
    python run.py --sample           # genera datos BHT de muestra en /data
    python run.py --status           # muestra estado del sistema
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# ──────────────────────────────────────────────
# CHECKS PREVIOS
# ──────────────────────────────────────────────

def check_environment():
    """Verifica que todo esté configurado antes de correr."""
    issues = []
    warnings = []

    # API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        issues.append("ANTHROPIC_API_KEY no seteada. Setear con: export ANTHROPIC_API_KEY='sk-ant-...'")

    # Python packages
    required = ["anthropic", "streamlit", "pandas"]
    optional = ["plotly", "openpyxl"]

    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            issues.append(f"Paquete requerido no instalado: {pkg}")

    for pkg in optional:
        try:
            __import__(pkg)
        except ImportError:
            warnings.append(f"Paquete opcional no instalado (mejora visualizaciones): {pkg}")

    # Data directory
    if not Path("data").exists():
        Path("data").mkdir(parents=True)
        warnings.append("Directorio /data creado. Agregar archivos BHT ahí.")

    # Outputs directory
    Path("outputs").mkdir(parents=True, exist_ok=True)

    return issues, warnings


def print_status():
    """Muestra estado del sistema."""
    print("\n=== KAVAK BRAND INTELLIGENCE — STATUS ===\n")

    # API key
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        print(f"✓ ANTHROPIC_API_KEY: seteada (...{key[-4:]})")
    else:
        print("✗ ANTHROPIC_API_KEY: NO SETEADA")

    # BHT files
    import glob
    bht_files = glob.glob("data/bht_*.csv") + glob.glob("data/bht_*.xlsx")
    if bht_files:
        print(f"✓ Archivos BHT: {len(bht_files)} encontrados")
        for f in bht_files:
            print(f"    - {f}")
    else:
        print("✗ Archivos BHT: ninguno en /data (correr --sample para generar datos de prueba)")

    # Cache status
    sl_cache = Path("outputs/social_listening_cache.json")
    if sl_cache.exists():
        import time
        age = (time.time() - sl_cache.stat().st_mtime) / 3600
        try:
            with open(sl_cache) as f:
                mentions = json.load(f)
            print(f"✓ Cache social listening: {len(mentions)} menciones ({age:.1f}h de antigüedad)")
        except Exception:
            print(f"⚠️  Cache social listening: existe pero corrupto")
    else:
        print("✗ Cache social listening: no existe (correr pipeline para generarlo)")

    analysis_cache = Path("outputs/analysis_cache.json")
    if analysis_cache.exists():
        import time
        age = (time.time() - analysis_cache.stat().st_mtime) / 3600
        print(f"✓ Cache análisis: existe ({age:.1f}h de antigüedad)")
    else:
        print("✗ Cache análisis: no existe")

    print()


# ──────────────────────────────────────────────
# PIPELINE STEPS
# ──────────────────────────────────────────────

def step_load_bht():
    print("\n[1/3] Cargando Brand Health Tracker...")
    from collectors.bht_loader import load_bht_files, get_bht_summary_for_llm
    waves = load_bht_files("data")
    if not waves:
        print("  ⚠️  Sin datos BHT. El análisis usará solo social listening.")
        return "", {}
    summary = get_bht_summary_for_llm(waves)
    print(f"  ✓ {len(waves)} olas cargadas")
    return summary, waves


def step_social_listening(force_refresh: bool = False):
    print("\n[2/3] Ejecutando social listening...")
    if force_refresh:
        cache_file = "outputs/social_listening_cache.json"
        if Path(cache_file).exists():
            Path(cache_file).unlink()
            print("  Cache de social listening eliminado (force refresh)")

    from collectors.social_listener import run_social_listening, aggregate_insights, get_social_summary_for_llm
    mentions = run_social_listening(
        max_queries=20,
        cache_file="outputs/social_listening_cache.json",
    )
    aggregated = aggregate_insights(mentions)
    summary = get_social_summary_for_llm(aggregated)
    print(f"  ✓ {len(mentions)} menciones analizadas")
    return summary, aggregated


def step_analysis(bht_summary: str, social_summary: str, force_refresh: bool = False):
    print("\n[3/3] Generando análisis con Claude...")
    from analyzer import run_analysis
    analysis = run_analysis(
        bht_summary=bht_summary,
        social_summary=social_summary,
        force_refresh=force_refresh,
    )
    n_actionables = len(analysis.get("accionables_growth", []))
    print(f"  ✓ {n_actionables} accionables generados")
    return analysis


def launch_dashboard():
    print("\n🚀 Lanzando dashboard...")
    print("   URL: http://localhost:8501\n")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "dashboard/app.py",
        "--server.headless", "true",
        "--theme.primaryColor", "#0057FF",
        "--theme.backgroundColor", "#FFFFFF",
        "--theme.secondaryBackgroundColor", "#F5F5F5",
        "--theme.textColor", "#000000",
        "--theme.font", "sans serif",
    ])


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Kavak Brand Intelligence Dashboard")
    parser.add_argument("--collect-only", action="store_true", help="Solo recolecta datos")
    parser.add_argument("--analyze-only", action="store_true", help="Solo corre análisis")
    parser.add_argument("--dashboard", action="store_true", help="Solo lanza dashboard")
    parser.add_argument("--refresh", action="store_true", help="Fuerza refresh completo")
    parser.add_argument("--sample", action="store_true", help="Genera datos BHT de muestra")
    parser.add_argument("--status", action="store_true", help="Muestra estado del sistema")
    args = parser.parse_args()

    # Status
    if args.status:
        print_status()
        return

    # Sample data
    if args.sample:
        from collectors.bht_loader import generate_sample_bht
        generate_sample_bht("data")
        return

    # Solo dashboard (usa cache)
    if args.dashboard:
        launch_dashboard()
        return

    # Checks
    print("\n=== KAVAK BRAND INTELLIGENCE ===")
    issues, warnings = check_environment()

    if warnings:
        for w in warnings:
            print(f"  ⚠️  {w}")

    if issues:
        print("\n❌ ERRORES DE CONFIGURACIÓN:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nCorregir los errores antes de continuar.")
        sys.exit(1)

    print("  ✓ Configuración OK\n")

    # Solo análisis (usa cache de social)
    if args.analyze_only:
        # Cargar caches existentes
        sl_cache_path = Path("outputs/social_listening_cache.json")
        if not sl_cache_path.exists():
            print("❌ No hay cache de social listening. Correr sin --analyze-only primero.")
            sys.exit(1)

        with open(sl_cache_path) as f:
            mentions = json.load(f)

        from collectors.social_listener import aggregate_insights, get_social_summary_for_llm
        from collectors.bht_loader import load_bht_files, get_bht_summary_for_llm

        aggregated = aggregate_insights(mentions)
        social_summary = get_social_summary_for_llm(aggregated)
        waves = load_bht_files("data")
        bht_summary = get_bht_summary_for_llm(waves)

        step_analysis(bht_summary, social_summary, force_refresh=True)
        return

    # Pipeline completo
    bht_summary, waves = step_load_bht()

    if not args.analyze_only:
        social_summary, aggregated = step_social_listening(force_refresh=args.refresh)
    
    if not args.collect_only:
        analysis = step_analysis(bht_summary, social_summary, force_refresh=args.refresh)

        # Preview rápido en consola
        print("\n═══ PREVIEW DEL ANÁLISIS ═══")
        print(f"\nEXECUTIVE SUMMARY:")
        print(f"  {analysis.get('executive_summary', 'N/A')[:200]}...")

        actionables = analysis.get("accionables_growth", [])
        altas = [a for a in actionables if a.get("prioridad") == "alta"]
        if altas:
            print(f"\nACCIONABLES DE ALTA PRIORIDAD ({len(altas)}):")
            for a in altas:
                print(f"  • [{a.get('lever', '?')}] {a.get('titulo', '')}")

    # Lanzar dashboard
    launch_dashboard()


if __name__ == "__main__":
    main()
