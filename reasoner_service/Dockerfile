# Dockerfile para reasoner_service (FastAPI + owlready2)
FROM python:3.11-slim

# Variables de entorno para UTF-8 y sin bytecode
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Crear directorio de la app
WORKDIR /app

# Instalar dependencias del sistema necesarias para owlready2, FastAPI y Java (Pellet)
RUN apt-get update && \
    apt-get install -y gcc build-essential libffi-dev default-jre && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y la carpeta ontology (si existe)
COPY app/ ./app/

# Exponer el puerto por defecto de FastAPI
EXPOSE 8000

# Mostrar la versión de la ontología al arrancar el contenedor
RUN echo "Reasoner image built for CURRENT_RELEASE=$CURRENT_RELEASE"
ENTRYPOINT ["/bin/sh", "-c", "echo 'Reasoner ejecutando con CURRENT_RELEASE=$CURRENT_RELEASE'; exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
