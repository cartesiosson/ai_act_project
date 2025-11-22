# ===== Reasoner Service - SWRL Reasoning Engine =====
# Image: python:3.11-slim (minimal, optimized for production)
# Includes: FastAPI, SWRL reasoning via Jena, OWL 2 DL processing

FROM python:3.11-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies for owlready2, FastAPI, and Java (Jena/Pellet)
RUN apt-get update && \
    apt-get install -y gcc build-essential libffi-dev default-jre curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Includes:
# - FastAPI: API framework
# - uvicorn: ASGI server
# - owlready2: OWL 2 DL semantic reasoning
# - rdflib: RDF/Semantic Web processing
# - jpype1: Java integration for Jena/Pellet reasoners
# - python-multipart: Form data support

COPY app/ ./app/

EXPOSE 8000

# Health check: verify reasoning service is responding (check docs endpoint which always exists in FastAPI)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Show ontology version when starting container
RUN echo "Reasoner image built for CURRENT_RELEASE=\${CURRENT_RELEASE}"

# Start FastAPI reasoning service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
