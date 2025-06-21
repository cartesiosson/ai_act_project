import os
from requests.auth import HTTPBasicAuth
import time
import requests

FUSEKI_ENDPOINT = os.getenv("FUSEKI_ENDPOINT", "http://fuseki:3030")
DATASET = "ds"
GRAPH_URI = "http://ai-act.eu/ontoglogy"
ONTOLOGY_PATH = "/app/ontologias"

# Esperar a que Fuseki esté disponible
def wait_for_fuseki():
    for _ in range(30):
        try:
            r = requests.get(f"{FUSEKI_ENDPOINT}")
            if r.status_code == 200:
                return True
        except Exception:
            pass
        print("Esperando a que Fuseki esté listo...")
        time.sleep(2)
    raise RuntimeError("Fuseki no responde.")

wait_for_fuseki()

# Verificar si el grafo ya contiene datos
def graph_has_data():
    ask_query = f"""
    ASK WHERE {{ GRAPH <{GRAPH_URI}> {{ ?s ?p ?o }} }}
    """
    headers = {'Accept': 'application/sparql-results+json'}
    auth = HTTPBasicAuth(os.getenv("FUSEKI_USER", "admin"), os.getenv("FUSEKI_PASSWORD", "admin"))
    r = requests.post(f"{FUSEKI_ENDPOINT}/{DATASET}/query", data={'query': ask_query}, headers=headers, auth=auth)
    r.raise_for_status()
    return r.json().get("boolean", False)

# Verificar si el dataset existe
def dataset_exists():
    admin_url = f"{FUSEKI_ENDPOINT}/$/datasets"
    auth = HTTPBasicAuth(os.getenv("FUSEKI_USER", "admin"), os.getenv("FUSEKI_PASSWORD", "admin"))
    try:
        r = requests.get(admin_url, headers={"Accept": "application/json"}, auth=auth)
        r.raise_for_status()
        datasets = r.json().get("datasets", [])
        return any(ds.get("ds.name") == f"/{DATASET}" for ds in datasets)
    except Exception as e:
        print(f"Error al verificar existencia del dataset: {e}")
        return False

if not dataset_exists():
    print(f"⚠️ El dataset '{DATASET}' no existe. Creándolo...")
    admin_url = f"{FUSEKI_ENDPOINT}/$/datasets"
    auth = HTTPBasicAuth(os.getenv("FUSEKI_USER", "admin"), os.getenv("FUSEKI_PASSWORD", "admin"))
    payload = {"dbName": DATASET, "dbType": "tdb"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(admin_url, data=payload, headers=headers, auth=auth)
    if r.status_code not in (200, 201):
        raise Exception(f"❌ No se pudo crear el dataset {DATASET}: {r.status_code} {r.text}")
    print(f"✅ Dataset {DATASET} creado exitosamente.")

# Subir archivos TTL como grafo
def upload_turtle(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    headers = {"Content-Type": "text/turtle"}
    graph_url = f"{FUSEKI_ENDPOINT}/{DATASET}/data?graph={GRAPH_URI}"
    auth = HTTPBasicAuth(os.getenv("FUSEKI_USER", "admin"), os.getenv("FUSEKI_PASSWORD", "admin"))
    response = requests.post(graph_url, data=data, headers=headers, auth=auth)
    if response.status_code not in (200, 201, 204):
        raise Exception(f"Error cargando {file_path.name}: {response.status_code} {response.text}")
    print(f"✔️ {file_path.name} cargado en el grafo {GRAPH_URI}")

# Procesar todos los archivos en /app/ontologias
from pathlib import Path
ontologies_path = Path(ONTOLOGY_PATH)
ttl_files = list(ontologies_path.glob("*.ttl"))

if not ttl_files:
    print("No se encontraron archivos TTL en /app/ontologias.")
else:
    print("Archivos TTL encontrados:")
    for ttl_file in ttl_files:
        print(f" - {ttl_file.name}")
    if graph_has_data():
                print("ℹ️ El grafo ya contiene datos. No se realizará la carga.")
    else:
        for ttl_file in ttl_files:
            upload_turtle(ttl_file)