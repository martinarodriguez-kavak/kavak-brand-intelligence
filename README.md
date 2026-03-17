# Kavak Brand Intelligence Dashboard

Panel de inteligencia de marca que integra:
- **Brand Health Tracker** (por ola)
- **Social Listening** con IA (Claude API + web_search)
- **Accionables Growth & Content** filtrados por palancas de marketing

---

## Setup rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Setear API key
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Cargar datos BHT
Copiar archivos BHT a la carpeta `/data`:
```
data/
├── bht_ola1_2024Q1.csv
├── bht_ola2_2024Q3.csv
└── bht_ola3_2025Q1.csv
```

**Formato esperado (CSV long format):**
```csv
ola,metrica,valor,segmento,mercado
ola1_2024Q1,Top of Mind,18.5,total,nacional
ola1_2024Q1,NPS,28.0,total,nacional
ola1_2024Q1,Consideración,35.7,total,nacional
```

**Formato alternativo (Excel wide):**
Columnas: una por métrica, filas: una por ola/segmento.

Si no tenés datos reales todavía, generá una muestra:
```bash
python run.py --sample
```

### 4. Correr el pipeline completo
```bash
python run.py
```

Esto:
1. Carga los BHTs de `/data`
2. Ejecuta ~20 búsquedas de social listening vía Claude API
3. Genera el análisis con accionables
4. Lanza el dashboard en `http://localhost:8501`

---

## Comandos disponibles

```bash
python run.py                    # pipeline completo + lanza dashboard
python run.py --collect-only     # solo recolecta (BHT + social), sin análisis
python run.py --analyze-only     # solo re-analiza (usa cache de social)
python run.py --dashboard        # solo lanza dashboard (usa cache completo)
python run.py --refresh          # fuerza refresh de todo
python run.py --sample           # genera datos BHT de muestra
python run.py --status           # muestra estado del sistema
```

---

## Estructura del dashboard

### Tab 1: Brand Health Tracker
- Métricas por ola con tendencias
- Gráfico de evolución interactivo (seleccionable)
- Insights de cada KPI con urgencia
- Brechas percepción/realidad

### Tab 2: Social Listening
- Total menciones + distribución de sentimiento
- Temas más mencionados (bar chart)
- Fuentes de menciones
- Narrativas detectadas por IA
- Verbatims negativos, positivos, mixtos

### Tab 3: Accionables Growth
- Solo palancas de marketing/contenido (sin ops, sin pricing)
- Agrupados por lever: Mensajería, Contenido, Awareness, Consideración, Confianza, Precio como comunicación
- Para cada accionable: descripción, hipótesis, canales sugeridos, KPI de éxito, timeline
- Temas excluidos (transparencia hacia otras áreas)

---

## Actualización de datos

### Social Listening
El cache dura **24 horas**. Para refrescar antes:
```bash
python run.py --refresh
```

### BHT
Agregar nuevos archivos CSV/Excel a `/data` y correr:
```bash
python run.py --analyze-only
```

---

## Cache

```
outputs/
├── social_listening_cache.json   # menciones crudas (24h TTL)
└── analysis_cache.json           # análisis generado (12h TTL)
```

---

## Siguiente entregable: CRM Interno

El módulo de integración con datos de clientes (caso por caso, status, historial)
se añadirá en una nueva tab "Customer Intelligence" que conectará con la fuente
interna de Kavak vía API o Google Sheets.

---

## Estructura de archivos

```
brand_health_dashboard/
├── run.py                          # orchestrator principal
├── config.py                       # queries, levers, contexto Kavak
├── analyzer.py                     # synthesis + accionables (Claude API)
├── collectors/
│   ├── bht_loader.py               # carga BHT CSV/Excel
│   └── social_listener.py          # Claude API + web_search
├── dashboard/
│   └── app.py                      # Streamlit dashboard
├── data/                           # BHT files van acá
├── outputs/                        # caches generados automáticamente
└── requirements.txt
```
