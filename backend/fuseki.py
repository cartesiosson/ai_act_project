import os
import requests
from requests.auth import HTTPBasicAuth

FUSEKI_ENDPOINT = os.getenv("FUSEKI_ENDPOINT", "http://fuseki:3030")
FUSEKI_DATASET = os.getenv("FUSEKI_DATASET", "ds")
FUSEKI_GRAPH = os.getenv("FUSEKI_GRAPH_URI", "http://ai-act.eu/data")

def insert_data_turtle(turtle_data: str):
    url = f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/data?graph={FUSEKI_GRAPH}"
    headers = {"Content-Type": "text/turtle"}
    auth = HTTPBasicAuth(os.getenv("FUSEKI_USER", "admin"), os.getenv("FUSEKI_PASSWORD", "admin"))

    response = requests.post(url, data=turtle_data.encode("utf-8"), headers=headers, auth=auth)
    if response.status_code not in (200, 201, 204):
        raise Exception(f"❌ Error al insertar en Fuseki: {response.status_code} - {response.text}")
