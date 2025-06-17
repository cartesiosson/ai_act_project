import os
import time
import json
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from pymongo import MongoClient

FUSEKI_BASE = os.getenv("FUSEKI_BASE", "http://fuseki:3030")
FUSEKI_DATASET = os.getenv("FUSEKI_DATASET", "ds")
FUSEKI_GRAPH = os.getenv("FUSEKI_GRAPH", "http://ai-act.eu/data/ai-data")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "ai_act"

# Esperar a que Fuseki esté disponible
def wait_for_fuseki(url):
    for _ in range(30):
        try:
            if requests.get(url).status_code == 200:
                print("✔️  Fuseki está disponible.")
                return
        except Exception:
            pass
        print("⏳ Esperando a Fuseki...")
        time.sleep(2)
    raise Exception("❌ Timeout esperando a Fuseki.")

# Consulta SPARQL para obtener etiquetas y comentarios multilingües
def fetch_entities(class_key):
    """
    Consulta entidades de una clase en Fuseki, soportando subclases si class_key comienza con 'subclass:'.
    """
    use_subclass = class_key.startswith("subclass:")
    class_uri = class_key[len("subclass:"):] if use_subclass else class_key

    sparql = SPARQLWrapper(f"{FUSEKI_BASE}/{FUSEKI_DATASET}/query")
    sparql.setReturnFormat(JSON)

    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?entity ?label ?labelLang ?comment ?commentLang WHERE {{
        GRAPH <{FUSEKI_GRAPH}> {{
            ?entity a {'?class .' if use_subclass else f'<{class_uri}> .'}
            {'?class rdfs:subClassOf* <' + class_uri + '> .' if use_subclass else ''}
            OPTIONAL {{
                ?entity rdfs:label ?label .
                BIND(LANG(?label) AS ?labelLang)
            }}
            OPTIONAL {{
                ?entity rdfs:comment ?comment .
                BIND(LANG(?comment) AS ?commentLang)
            }}
        }}
    }}
    """

    sparql.setQuery(query)

    try:
        results = sparql.query().convert()
        entities = {}

        for result in results["results"]["bindings"]:
            uri = result["entity"]["value"]
            label_lang = result.get("labelLang", {}).get("value")
            label_val = result.get("label", {}).get("value")
            comment_lang = result.get("commentLang", {}).get("value")
            comment_val = result.get("comment", {}).get("value")

            if uri not in entities:
                entities[uri] = {"_id": uri, "label": {}, "comment": {}}

            if label_lang and label_val:
                entities[uri]["label"][label_lang] = label_val

            if comment_lang and comment_val:
                entities[uri]["comment"][comment_lang] = comment_val

        return list(entities.values())

    except Exception as e:
        print(f"❌ Error al consultar Fuseki para la clase {class_uri}: {e}")
        return []

# Conectar a MongoDB
def connect_mongo():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

if __name__ == "__main__":
    wait_for_fuseki(FUSEKI_BASE)
    db = connect_mongo()

    classes = {
    "http://ai-act.eu/vocab#Purpose": "purposes",
    "http://ai-act.eu/vocab#RiskLevel": "risklevels",
    "subclass:http://ai-act.eu/vocab#RiskCriterion": "criteria",
    "http://ai-act.eu/ontology/compliance#ComplianceRequirement": "compliance"
    }

    for cls_uri, collection in classes.items():
        print(f"Importando {collection} desde Fuseki...")
        entities = fetch_entities(cls_uri)
        if entities:
            db[collection].delete_many({})
            db[collection].insert_many(entities)
            print(f" → {len(entities)} elementos cargados.")
        else:
            print(f" ⚠️  No se encontraron entidades para {cls_uri}.")
