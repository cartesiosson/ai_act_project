# main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from rdflib import Graph
from models.system import IntelligentSystem
from db import get_database
import os, json

app = FastAPI(title="AI Act Backend")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}



# Montar estáticos y cargar ontologías igual que antes...
app.mount("/static", StaticFiles(directory="schema"), name="static")
ont = Graph()
for ttl in os.listdir("ontologias"):
    if ttl.endswith(".ttl"):
        ont.parse(f"ontologias/{ttl}", format="turtle")

# Tu router importado
from routers.systems import router as systems_router
app.include_router(systems_router)


from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Busca la clave de paths que corresponda a nuestro endpoint systems
    path_key = None
    for p in openapi_schema["paths"].keys():
        if p.rstrip("/") == "/systems":
            path_key = p
            break

    if not path_key:
        # Si no la encuentra, devolvemos el esquema sin modificar
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    post_op = openapi_schema["paths"][path_key].get("post")
    if post_op:
        # Sobrescribimos solo el requestBody de POST
        post_op["requestBody"] = {
            "required": True,
            "content": {
                "application/ld+json": {
                    "schema": {"$ref": "#/components/schemas/IntelligentSystem"},
                    "example": {
                        "@context": "http://localhost:8000/static/json-ld-context.json",
                        "@type": "ai:IntelligentSystem",
                        "hasName": "Sim-01",
                        "hasPurpose": "ai:ForEducation",
                        "hasRiskLevel": "ai:HighRisk",
                        "hasDeploymentContext": "ai:Education",
                        "hasTrainingDataOrigin": "ai:InternalDataset",
                        "hasVersion": "1.0.0"
                    }
                }
            }
        }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Finalmente, sobrescribimos la función
app.openapi = custom_openapi
