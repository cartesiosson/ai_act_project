from fastapi import FastAPI, File, UploadFile, Form
from fastapi import responses
from fastapi import status
from fastapi.responses import Response
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from owlready2 import get_ontology, onto_path, World, sync_reasoner_pellet
import tempfile
import shutil
import os
from typing import List

app = FastAPI(title="SWRL Reasoner Service", description="Microservicio para inferencia OWL+SWRL usando owlready2", version="1.0.0")

# Permitir CORS para facilitar pruebas y despliegue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Leer la ruta de la ontología base desde la variable de entorno
ONTOLOGY_PATH = os.environ.get("ONTOLOGY_PATH", os.path.join(os.path.dirname(__file__), "ontology", "ontologia.ttl"))
ONTOLOGY_IRI = "http://example.org/ontologia#"  # Cambia esto por el IRI real de tu ontología

# Depuración: mostrar la ruta de la ontología y verificar si el archivo existe
print("DEBUG ONTOLOGY_PATH:", ONTOLOGY_PATH)
print("DEBUG exists:", os.path.isfile(ONTOLOGY_PATH))

# Cargar la ontología base al iniciar el servidor
base_world = World()
base_onto = base_world.get_ontology(f"file://{ONTOLOGY_PATH}").load(format="turtle")

@app.post(
    "/reason",
    response_class=Response,
    responses={
        200: {
            "content": {"text/turtle": {}}
        }
    },
    status_code=200,
    summary="Inferencia SWRL sobre ontología base",
    description="Recibe datos y reglas SWRL (ambos RDF/TTL), ejecuta inferencia y devuelve el grafo inferido en formato Turtle."
)
async def reason(
    data: UploadFile = File(..., description="Datos RDF/TTL para instanciar en la ontología base"),
    swrl_rules: UploadFile = File(..., description="Archivo RDF/TTL con reglas SWRL")
):
    """
    Recibe datos y un archivo de reglas SWRL (TTL/RDF), ejecuta inferencia sobre la ontología base y devuelve los triples inferidos.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Guardar los datos recibidos
        data_file = os.path.join(tmpdir, data.filename)
        with open(data_file, "wb") as f:
            shutil.copyfileobj(data.file, f)
        # Guardar el archivo de reglas SWRL
        rules_file = os.path.join(tmpdir, swrl_rules.filename)
        with open(rules_file, "wb") as f:
            shutil.copyfileobj(swrl_rules.file, f)

        # Crear un nuevo World y clonar la ontología base
        world = World()
        onto = world.get_ontology(f"file://{ONTOLOGY_PATH}").load(format="turtle")
        # Importar los datos recibidos
        world.get_ontology(f"file://{data_file}").load(format="turtle")
        # Importar las reglas SWRL desde el archivo
        world.get_ontology(f"file://{rules_file}").load(format="turtle")

        # Ejecutar la inferencia
        with world.get_ontology(onto.base_iri):
            world.save()
            sync_reasoner_pellet(world)

        # Serializar el grafo inferido a Turtle
        ttl_output = world.as_rdflib_graph().serialize(format="turtle")

    return Response(content=ttl_output, media_type="text/turtle")

@app.get("/")
def root():
    return {"message": "SWRL Reasoner Service. Use /reason endpoint."}
