"""
Script to append BHT W10, W11, W12 data to the existing CSV.
All data extracted manually from PPTX slides via python-pptx.

Sources:
- W10: 24_0212_REF_KAVAK BHT MEX W10.pptx (January 2025 report, Dec 2024 fieldwork)
- W11: 25_0269_REF_KAVAK BHT MEX W11.pptx (June 2025 fieldwork)
- W12: FinalReport.pptx in W12 Diciembre 2025 folder (December 2025 fieldwork)
"""

import csv
import os

CSV_PATH = "/Users/martinarodriguez/Desktop/Claude/skills/dashboard_consumer_centric/files (2)/data/bht_kavak_mexico_W0-W9.csv"

# ── W10 Kavak KPIs (December 2024, Base = 900) ────────────────────────────────
# Slide 9  – Awareness chart: TOM=50, Unaided=37, Total=83
# Slide 37 – NPS table (row 1 = Kavak): NPS=48, Prom=59, Pasiv=31, Detrac=11
# Slide 38 – NPS evolution chart confirms W10 Kavak NPS = 48
# Slide 35 – Brand Equity Index: Kavak = 79
# Slide 36 – Brand Equity table (row 1 = Kavak, Dec2024): OR=79, Fav=82, Diff=73, Close=67
# Slide 54 – Intenders funnel (Dec2024): Consid=64, Intent1a=35, IntentTotal=42

W10_KAVAK = [
    # ola, fecha_aprox, marca, brand_id, metrica, valor, n_total, es_kavak
    ["W10", "2024-12", "Kavak", 1, "Top_of_Mind",               50.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Awareness_Espontanea",       37.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Awareness_Asistida",         83.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Consideracion",              64.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Intencion_Compra_1a",        35.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Intencion_Compra_Total",     42.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "NPS_Score",                  48.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "NPS_Promotores_pct",         59.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "NPS_Pasivos_pct",            31.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "NPS_Detractores_pct",        11.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Brand_Equity_Index",         79.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Brand_Overall_Rating_T3B",   79.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Brand_Favorability_T2B",     82.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Brand_Differentiation_T2B",  73.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Brand_Closeness_T3B",        67.0,   900,  True],
    # Attribute highlights (Total weighted, dec-24 column from slide 71 table)
    ["W10", "2024-12", "Kavak", 1, "Attr_Cars_Good_Standing",    64.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Attr_Security_Transaction",  63.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Attr_Inspected_Certified",   64.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Attr_Car_Warranty",          61.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Attr_Reliable_Option",       60.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Attr_Premium_Option",        55.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Attr_Wide_Catalog",          69.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Attr_Online_Credit_Sim",     63.0,   900,  True],
    ["W10", "2024-12", "Kavak", 1, "Attr_Online_Offers",         63.0,   900,  True],
    # Ad Recall (slide 79, Dec 2024)
    ["W10", "2024-12", "Kavak", 1, "Ad_Recall",                  67.0,   900,  True],
]

# ── W11 Kavak KPIs (June 2025, Base = 900) ───────────────────────────────────
# Slide 10  – Awareness chart: TOM=51, Unaided=39, Total=84
# Slide 39  – NPS table (row 2 blank = Kavak, Dec24=43→W10 mismatch; but row with Jun25=48
#              matches NPS evolution last value=48; confirmed via W12 where Kavak Jun25=48)
#              Kavak W11: NPS=48, Prom=61, Pasiv=26, Detrac=13
# Slide 40  – NPS evolution chart confirms W11 Kavak NPS = 48 (last value)
# Slide 37  – Brand Equity Index: Kavak Jun 2025 = 82
# Slide 38  – Brand Equity table (row 1 = Kavak, Jun2025): OR=84, Fav=85, Diff=74, Close=76
# Slide 57  – Intenders funnel (Jun2025): Consid=69, Intent1a=39, IntentTotal=47

W11_KAVAK = [
    ["W11", "2025-07", "Kavak", 1, "Top_of_Mind",               51.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Awareness_Espontanea",       39.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Awareness_Asistida",         84.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Consideracion",              69.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Intencion_Compra_1a",        39.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Intencion_Compra_Total",     47.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "NPS_Score",                  48.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "NPS_Promotores_pct",         61.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "NPS_Pasivos_pct",            26.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "NPS_Detractores_pct",        13.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Brand_Equity_Index",         82.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Brand_Overall_Rating_T3B",   84.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Brand_Favorability_T2B",     85.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Brand_Differentiation_T2B",  74.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Brand_Closeness_T3B",        76.0,   900,  True],
    # Attribute highlights (jun-25 column from slide 75 table)
    ["W11", "2025-07", "Kavak", 1, "Attr_Cars_Good_Standing",    67.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Attr_Security_Transaction",  64.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Attr_Inspected_Certified",   64.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Attr_Car_Warranty",          59.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Attr_Reliable_Option",       62.0,   900,  True],
    ["W11", "2025-07", "Kavak", 1, "Attr_Wide_Catalog",          65.0,   900,  True],
    # Ad Recall (slide 84 W11 – Dec24=67 for Kavak, Jun25 from chart)
    # W11 slide ~84 not extracted; skip for now
]

# ── W12 Kavak KPIs (December 2025, Base = 900) ────────────────────────────────
# Slide 7  – Awareness chart: TOM=53, Unaided=43, Total=84
# Slide 20 – NPS table (row 1 blank = Kavak): NPS=53, Prom=64, Pasiv=24, Detrac=11
# Slide 19 – Brand Equity table (row 1 = Kavak, Dec2025): BEI=84, OR=87, Fav=89, Diff=83, Close=77
# Slide 30 – Intenders funnel (Dec2025): Consid=63, Intent1a=39, IntentTotal=42

W12_KAVAK = [
    ["W12", "2025-12", "Kavak", 1, "Top_of_Mind",               53.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Awareness_Espontanea",       43.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Awareness_Asistida",         84.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Consideracion",              63.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Intencion_Compra_1a",        39.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Intencion_Compra_Total",     42.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "NPS_Score",                  53.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "NPS_Promotores_pct",         64.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "NPS_Pasivos_pct",            24.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "NPS_Detractores_pct",        11.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Brand_Equity_Index",         84.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Brand_Overall_Rating_T3B",   87.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Brand_Favorability_T2B",     89.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Brand_Differentiation_T2B",  83.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Brand_Closeness_T3B",        77.0,   900,  True],
    # Attribute highlights (dec-25 column from slide 41 table)
    ["W12", "2025-12", "Kavak", 1, "Attr_Reliable_Option",       64.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Attr_Inspected_Certified",   63.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Attr_Security_Transaction",  63.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Attr_Cars_Good_Condition",   63.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Attr_Car_Warranty",          64.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Attr_Fair_Value_Car",        55.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Attr_Cars_Good_Standing",    64.0,   900,  True],
    ["W12", "2025-12", "Kavak", 1, "Attr_Clear_Complete_Info",   65.0,   900,  True],
]

# ── Append to CSV ─────────────────────────────────────────────────────────────
HEADER = ["ola", "fecha_aprox", "marca", "brand_id", "metrica", "valor", "n_total", "es_kavak"]

all_new_rows = W10_KAVAK + W11_KAVAK + W12_KAVAK

print(f"Appending {len(all_new_rows)} rows to {CSV_PATH}")

with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in all_new_rows:
        writer.writerow(row)

print("Done. Rows appended successfully.")
print(f"\nBreakdown:")
print(f"  W10: {len(W10_KAVAK)} rows")
print(f"  W11: {len(W11_KAVAK)} rows")
print(f"  W12: {len(W12_KAVAK)} rows")
