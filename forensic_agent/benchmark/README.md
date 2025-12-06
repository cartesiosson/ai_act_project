# Forensic Agent Benchmark

Sistema de benchmarking para evaluar el rendimiento y calidad del agente forense sobre 100 incidentes sintéticos.

## Estructura

```
benchmark/
├── generate_incidents.py      # Generador de incidentes sintéticos
├── run_benchmark.py           # Ejecutor del benchmark
├── upload_to_fuseki.py        # Subida de resultados a Fuseki
├── benchmark_incidents.json   # 100 incidentes generados
├── benchmark_output.log       # Log de ejecución
└── results/                   # Resultados del benchmark
    ├── benchmark_results_*.json    # Resultados completos
    └── benchmark_stats_*.json      # Estadísticas agregadas
```

## Uso

### 1. Generar Incidentes Sintéticos

```bash
python3 generate_incidents.py
```

Genera 100 incidentes sintéticos basados en patrones reales de AIAAIC:
- 40 discriminación
- 30 safety_failure
- 20 privacy_violation
- 10 bias

Tipos de sistemas cubiertos:
- Facial Recognition Bias
- Hiring Discrimination
- Credit Scoring Bias
- Healthcare AI Errors
- Predictive Policing
- Data Breaches
- Emotion Recognition
- Social Scoring
- Deepfakes
- Autonomous Vehicles

### 2. Ejecutar Benchmark

```bash
python3 run_benchmark.py
```

Ejecuta análisis forense sobre los 100 incidentes y recolecta:

**Métricas de Rendimiento:**
- Tiempo de procesamiento (mean, median, min, max, stdev)
- Tasa de éxito
- Tasa de fallo

**Métricas de Calidad:**
- Confidence scores (mean, median, min, max, stdev)
- Distribución de niveles de riesgo (Unacceptable, HighRisk, etc.)
- Distribución de tipos de incidente

**Salidas:**
- `results/benchmark_results_TIMESTAMP.json` - Resultados completos
- `results/benchmark_stats_TIMESTAMP.json` - Estadísticas agregadas
- `benchmark_output.log` - Log de ejecución

### 3. Subir Resultados a Fuseki

```bash
python3 upload_to_fuseki.py
```

Convierte los resultados del análisis forense a RDF y los sube a Fuseki.

Para cada sistema exitosamente analizado, crea:
- Sistema AI con propiedades (nombre, organización, propósito, riesgo)
- Incidente asociado (tipo, severidad, fecha, poblaciones afectadas)
- Requisitos EU AI Act aplicables
- Gaps de compliance identificados
- Confianza de extracción

**Namespaces:**
- `http://ai-act.eu/ai#` - Ontología EU AI Act
- `http://ai-act.eu/forensic#` - Extensión forense

**Named Graphs:**
- `http://ai-act.eu/forensic/systems/{incident_id}` - Un grafo por sistema

## Requisitos

- Forensic Agent corriendo en `http://localhost:8002`
- Apache Jena Fuseki en `http://localhost:3030`
- Python 3.9+
- Dependencias: requests, rdflib

## Métricas Esperadas

Con Llama 3.2 (3B) en Ollama:

**Rendimiento:**
- Tiempo medio: 15-20 segundos/incidente
- Tiempo total: ~25 minutos para 100 incidentes
- Throughput: 3-4 incidentes/minuto

**Calidad:**
- Success rate: >95%
- Confidence promedio: 0.80-0.87
- Distribución de riesgo: mayoría HighRisk (sistemas biométricos, policing, healthcare)

**Compliance:**
- Requisitos promedio por sistema: 4-6
- Gaps críticos: 1-3 por sistema
- Tipos de requisitos: Data Governance, Transparency, Human Oversight, etc.

## Comparación Ollama vs Claude

| Métrica | Llama 3.2 (Ollama) | Claude Sonnet 4.5 |
|---------|-------------------|-------------------|
| Velocidad | 15-20s | 5-10s |
| Confianza | 80-87% | 90-95% |
| Costo | Gratis | ~$1.50 (100 incidentes) |
| Privacidad | Local | Cloud |
| Precisión timeline | Buena (año) | Excelente (fecha) |
| Clasificación riesgo | Muy buena | Excelente |

## Análisis de Resultados

El benchmark genera reportes completos que incluyen:

1. **Summary**: Total, éxitos, fallos, tasa de éxito
2. **Performance**: Tiempos de procesamiento (distribución estadística)
3. **Quality**: Confidence scores (distribución estadística)
4. **Risk Distribution**: Unacceptable, HighRisk, LimitedRisk, MinimalRisk
5. **Incident Distribution**: bias, discrimination, privacy_violation, safety_failure
6. **Errors**: Detalles de fallos si los hay

## Troubleshooting

### Forensic agent no responde
```bash
docker-compose logs forensic_agent
docker-compose restart forensic_agent
```

### Ollama lento
- Verificar CPU/memoria disponible
- Considerar usar GPU (descomentar en docker-compose.yml)
- Reducir batch size en benchmark

### Fuseki no acepta uploads
```bash
# Verificar dataset existe
curl http://localhost:3030/$/datasets

# Recrear dataset si es necesario
curl -X POST http://localhost:3030/$/datasets \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "dbName=aiact&dbType=tdb2"
```

## Próximos Pasos

1. Ejecutar benchmark con Claude Sonnet 4.5 para comparación
2. Analizar distribución de requisitos más frecuentes
3. Identificar patrones en gaps de compliance
4. Mejorar prompts basándose en errores
5. Crear visualizaciones de resultados
