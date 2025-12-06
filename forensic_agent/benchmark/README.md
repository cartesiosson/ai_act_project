# Forensic Agent Benchmark

Sistema de benchmarking para evaluar el rendimiento y calidad del agente forense.

## Tipos de Benchmark

### 1. Benchmark Sintético
100 incidentes generados basados en patrones reales de AIAAIC.

### 2. Benchmark Real (AIAAIC)
Incidentes reales del repositorio [AIAAIC](https://www.aiaaic.org/aiaaic-repository).

## Estructura

```
benchmark/
├── run_benchmark_sintetico.py    # Benchmark con datos sintéticos
├── run_benchmark_real.py         # Benchmark con datos reales AIAAIC
├── generate_synthetic_incidents.py # Generador de incidentes sintéticos
├── upload_to_fuseki.py           # Subida de resultados a Fuseki
├── analyze_results.py            # Análisis de resultados
├── benchmark_incidents.json      # 100 incidentes sintéticos pre-generados
└── results/                      # Resultados de benchmarks
    ├── benchmark_results_*.json       # Resultados sintéticos
    ├── benchmark_stats_*.json         # Estadísticas sintéticas
    ├── real_benchmark_results_*.json  # Resultados reales
    └── real_benchmark_stats_*.json    # Estadísticas reales
```

## Uso

### Benchmark Sintético

#### 1. Generar Incidentes Sintéticos (opcional)

```bash
python3 generate_synthetic_incidents.py
```

Genera 100 incidentes sintéticos basados en patrones reales:
- Discriminación (40%)
- Safety failures (30%)
- Privacy violations (20%)
- Bias (10%)

#### 2. Ejecutar Benchmark Sintético

```bash
python3 run_benchmark_sintetico.py
```

Analiza los 100 incidentes sintéticos de `benchmark_incidents.json`.

### Benchmark Real (AIAAIC)

```bash
python3 run_benchmark_real.py
```

El script:
1. Descarga incidentes reales del [AIAAIC Repository](https://docs.google.com/spreadsheets/d/1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI/)
2. Pregunta cuántos casos analizar
3. Ejecuta el análisis forense
4. Genera reportes de resultados

**Ejemplo de uso:**
```
======================================================================
AIAAIC Real Incident Benchmark
======================================================================

Fetching AIAAIC incidents from Google Sheets...
Loaded 543 real incidents from AIAAIC

Total available incidents: 543

Number of cases to analyze (1-543, or 'all'): 20

Selected 20 incidents for analysis
...
```

### 3. Subir Resultados a Fuseki

```bash
python3 upload_to_fuseki.py
```

Convierte los resultados a RDF y los sube al triplestore.

## Métricas Recolectadas

**Rendimiento:**
- Tiempo de procesamiento (mean, median, min, max, stdev)
- Tasa de éxito / fallo
- Throughput (incidentes/minuto)

**Calidad de Extracción:**
- Confidence scores por dimensión:
  - `purpose` (peso 2.0) - Propósito del sistema
  - `deployment` (peso 1.5) - Contexto de despliegue
  - `data_types` (peso 1.5) - Tipos de datos procesados
  - `incident` (peso 1.0) - Clasificación del incidente
  - `affected` (peso 1.0) - Poblaciones afectadas
  - `timeline` (peso 0.5) - Información temporal

**Clasificación EU AI Act:**
- Distribución de niveles de riesgo (Unacceptable, HighRisk, LimitedRisk, MinimalRisk)
- Requisitos identificados
- Gaps de compliance

**Distribución de Incidentes:**
- Por tipo (discrimination, bias, privacy_violation, safety_failure, etc.)
- Por sector (healthcare, finance, law enforcement, etc.)
- Por país/región

## Comparación: Sintético vs Real

| Aspecto | Sintético | Real (AIAAIC) |
|---------|-----------|---------------|
| Fuente | Generado | AIAAIC Repository |
| Casos | 100 fijos | 500+ (seleccionables) |
| Calidad narrativa | Estructurada | Variable |
| Cobertura | Templates predefinidos | Casos diversos |
| Reproducibilidad | 100% | Depende de datos disponibles |
| Uso | Validación de extracción | Validación real |

## Requisitos

- Forensic Agent corriendo en `http://localhost:8002`
- Apache Jena Fuseki en `http://localhost:3030`
- Python 3.9+
- Dependencias: `requests`, `rdflib`
- Conexión a internet (para benchmark real)

## Métricas Esperadas (Llama 3.2 - 3B en Ollama)

**Rendimiento:**
- Tiempo medio: 30-35 segundos/incidente
- Tiempo total (100 incidentes): ~55 minutos
- Throughput: ~2 incidentes/minuto

**Calidad:**
- Success rate: >90%
- Confidence promedio: 0.80-0.90
- Distribución de riesgo: mayoría HighRisk y Unknown

## Troubleshooting

### Forensic agent no responde
```bash
docker-compose logs forensic_agent
docker-compose restart forensic_agent
```

### Error al descargar datos AIAAIC
- Verificar conexión a internet
- El Google Sheet puede tener restricciones temporales
- Probar acceso manual: https://docs.google.com/spreadsheets/d/1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI/

### Ollama lento
- Verificar CPU/memoria disponible
- Considerar usar GPU
- Reducir número de casos en benchmark real

### Fuseki no acepta uploads
```bash
# Verificar dataset existe
curl http://localhost:3030/$/datasets

# Recrear dataset si es necesario
curl -X POST http://localhost:3030/$/datasets \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "dbName=aiact&dbType=tdb2"
```

## Fuentes de Datos y Atribución

### AIAAIC Repository

Este benchmark utiliza datos del [AIAAIC Repository](https://www.aiaaic.org/aiaaic-repository), una colección independiente de incidentes y controversias relacionadas con IA, algoritmos y automatización.

**Versión de datos utilizada:** Diciembre 2025 (2,139 incidentes)

**Licencia:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (Attribution-ShareAlike 4.0 International)

**Atribución requerida:**
> Datos de incidentes proporcionados por [AIAAIC](https://www.aiaaic.org/aiaaic-repository) bajo licencia CC BY-SA 4.0.

**Enlaces:**
- AIAAIC Repository: https://www.aiaaic.org/aiaaic-repository
- Google Sheet: https://docs.google.com/spreadsheets/d/1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI/
- Términos de uso: https://www.aiaaic.org/terms

### Otras fuentes (alternativas)

- AI Incident Database: https://incidentdatabase.ai/
- OECD AI Incidents Monitor: https://oecd.ai/en/incidents
