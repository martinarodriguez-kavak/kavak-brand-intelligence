"""
collectors/bht_loader.py
Carga y normaliza los Brand Health Tracker por ola.

Acepta:
- CSV separado por comas o punto y coma
- Excel (.xlsx / .xls)
- Formato wide (una columna por ola) o long (una fila por ola)

Output: DataFrame normalizado con columnas estándar.
"""

import os
import glob
import json
from pathlib import Path
from typing import Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import BHT_REQUIRED_COLUMNS, BHT_METRICS_CATALOG


def load_bht_files(data_dir: str = "data") -> dict:
    """
    Busca todos los archivos BHT en data_dir y los carga.
    
    Naming convention esperada:
        bht_ola1.csv, bht_ola2.xlsx, bht_2024Q1.csv, etc.
        O cualquier archivo que empiece con "bht_"
    
    Returns:
        dict con keys = nombre de ola, values = dict con métricas
    """
    try:
        import pandas as pd
    except ImportError:
        print("[BHT Loader] pandas no instalado. Corriendo: pip install pandas openpyxl")
        return {}

    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"[BHT Loader] Directorio '{data_dir}' no encontrado.")
        return {}

    # Buscar todos los archivos BHT
    patterns = ["bht_*.csv", "bht_*.xlsx", "bht_*.xls", "BHT_*.csv", "BHT_*.xlsx"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(str(data_path / pattern)))

    if not files:
        print(f"[BHT Loader] No se encontraron archivos BHT en '{data_dir}'.")
        print("  Nombrar archivos como: bht_ola1.csv, bht_ola2.xlsx, etc.")
        return {}

    all_waves = {}
    for filepath in sorted(files):
        wave_name = Path(filepath).stem  # ej: "bht_ola1"
        df = _load_single_file(filepath, pd)
        if df is not None:
            all_waves[wave_name] = _normalize_bht(df, wave_name)
            print(f"[BHT Loader] ✓ Cargada: {wave_name} ({len(df)} filas)")

    return all_waves


def _load_single_file(filepath: str, pd) -> Optional[object]:
    """Carga un archivo CSV o Excel."""
    try:
        ext = Path(filepath).suffix.lower()
        if ext == ".csv":
            # Intentar detectar separador automáticamente
            try:
                df = pd.read_csv(filepath, encoding="utf-8")
            except Exception:
                df = pd.read_csv(filepath, sep=";", encoding="utf-8")
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath)
        else:
            return None

        # Normalizar nombres de columnas
        df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]
        return df

    except Exception as e:
        print(f"[BHT Loader] ✗ Error cargando {filepath}: {e}")
        return None


def _normalize_bht(df, wave_name: str) -> dict:
    """
    Convierte un DataFrame BHT a dict estructurado.
    Intenta detectar formato wide o long.
    
    Returns dict:
    {
        "wave": "bht_ola1",
        "metrics": {
            "Top of Mind": {"total": 45.2, "cdmx": 48.1, ...},
            "NPS": {"total": 32, ...},
            ...
        },
        "raw_df": df  # para análisis adicional
    }
    """
    result = {
        "wave": wave_name,
        "metrics": {},
        "raw_df": df,
    }

    # Detectar si está en formato long (columna "metrica" + "valor")
    if "metrica" in df.columns and "valor" in df.columns:
        for _, row in df.iterrows():
            metric_name = str(row.get("metrica", "")).strip()
            if not metric_name:
                continue

            value = row.get("valor")
            segment = str(row.get("segmento", "total")).lower()
            market = str(row.get("mercado", "nacional")).lower()

            key = f"{market}_{segment}"

            if metric_name not in result["metrics"]:
                result["metrics"][metric_name] = {}
            result["metrics"][metric_name][key] = _safe_float(value)

    # Formato wide: columnas son métricas, filas son olas/segmentos
    else:
        # Buscar columnas que sean métricas conocidas
        all_known = [m for cat in BHT_METRICS_CATALOG.values() for m in cat]
        for col in df.columns:
            # Match flexible (lowercase, parcial)
            matched = next(
                (m for m in all_known if m.lower().replace(" ", "_") in col.lower()),
                None
            )
            if matched:
                # Tomar primer valor no-nulo
                vals = df[col].dropna()
                if len(vals) > 0:
                    result["metrics"][matched] = {"total": _safe_float(vals.iloc[0])}

    return result


def _safe_float(val) -> Optional[float]:
    """Convierte a float de forma segura."""
    try:
        return float(str(val).replace("%", "").replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def build_wave_comparison(all_waves: dict) -> dict:
    """
    Construye una tabla comparativa de todas las olas.
    
    Returns:
    {
        "metric_name": {
            "ola1": valor,
            "ola2": valor,
            ...
        }
    }
    """
    comparison = {}

    for wave_name, wave_data in all_waves.items():
        for metric, breakdown in wave_data.get("metrics", {}).items():
            if metric not in comparison:
                comparison[metric] = {}
            # Usar total o primer valor disponible
            val = breakdown.get("nacional_total") or breakdown.get("total") or \
                  next(iter(breakdown.values()), None) if breakdown else None
            comparison[metric][wave_name] = val

    return comparison


def get_bht_summary_for_llm(all_waves: dict) -> str:
    """
    Genera un resumen en texto plano de los BHTs para enviar al LLM.
    """
    if not all_waves:
        return "No hay datos de Brand Health Tracker disponibles."

    lines = ["=== BRAND HEALTH TRACKER DATA ===\n"]
    comparison = build_wave_comparison(all_waves)

    for metric, waves in comparison.items():
        wave_vals = ", ".join(
            f"{wave}: {val:.1f}{'%' if val and val <= 100 else ''}"
            for wave, val in sorted(waves.items())
            if val is not None
        )
        if wave_vals:
            lines.append(f"• {metric}: {wave_vals}")

    lines.append(f"\nOlas disponibles: {', '.join(sorted(all_waves.keys()))}")
    return "\n".join(lines)


def generate_sample_bht(output_dir: str = "data") -> None:
    """
    Genera archivos CSV de muestra para probar el dashboard.
    Útil para onboarding del equipo.
    """
    try:
        import pandas as pd
        import random
    except ImportError:
        print("pandas no instalado")
        return

    os.makedirs(output_dir, exist_ok=True)

    base_values = {
        "Top of Mind": 18.5,
        "Awareness Espontáneo": 42.3,
        "Awareness Asistido": 78.1,
        "Consideración": 35.7,
        "Preferencia": 22.4,
        "NPS": 28.0,
        "Precio Justo": 31.2,
        "Confianza": 58.9,
        "Facilidad de Proceso": 64.1,
        "Garantía": 71.3,
    }

    for i, ola in enumerate(["ola1_2024Q1", "ola2_2024Q3", "ola3_2025Q1"]):
        rows = []
        for metric, base in base_values.items():
            trend = base + (i * random.uniform(-2.5, 4.5))
            rows.append({
                "ola": ola,
                "metrica": metric,
                "valor": round(trend, 1),
                "segmento": "total",
                "mercado": "nacional",
            })
        pd.DataFrame(rows).to_csv(f"{output_dir}/bht_{ola}.csv", index=False)
        print(f"[Sample] Generado: bht_{ola}.csv")

    print("\n✓ Datos de muestra creados en /data. Reemplazar con datos reales.")
