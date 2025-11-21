# ===== Backend API - AI Act Evaluation Engine =====
# Image: python:3.11-slim (minimal, optimized for production)
# Includes: FastAPI, semantic reasoning (SWRL), SHACL validation

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Includes:
# - FastAPI: API framework
# - uvicorn: ASGI server
# - motor: Async MongoDB driver
# - rdflib: RDF/Semantic Web processing
# - pyshacl: SHACL validation for data quality
# - httpx: Async HTTP client for reasoner communication
# - pymongo: MongoDB support
# - requests: HTTP library
# - pyld: JSON-LD processing

COPY . .

# Health check: verify API is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/reasoning/status || exit 1

# Start FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]