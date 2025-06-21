import os
import json
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, URIRef

# Rutas relativas desde donde se ejecuta este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TTL_PATH = os.path.join(BASE_DIR, "../ontologias/docs/ontology.jsonld")
CONTEXT_OUT = os.path.join(BASE_DIR, "../ontologias/docs/context.jsonld")

# Cargar el grafo
g = Graph()
g.parse(TTL_PATH, format="json-ld")

context = {
    "@context": {
        "ai": "http://ai-act.eu/ai#",
        "rdfs": str(RDFS),
        "rdf": str(RDF),
        "xsd": str(XSD),
        "owl": str(OWL)
    }
}

# Inferencia de propiedades
for s, p, o in g.triples((None, RDF.type, None)):
    if o in [OWL.ObjectProperty, OWL.DatatypeProperty, RDF.Property]:
        if isinstance(s, URIRef):
            prop = str(s)
            if "#" in prop:
                prefix, name = prop.rsplit("#", 1)
                if prefix == "http://ai-act.eu/ai":
                    term = f"ai:{name}"
                else:
                    continue
            else:
                continue

            # Heurística para tipo de dato
            if "has" in name.lower() or name.startswith("is"):
                term_def = {"@type": "xsd:string"}
                if "Uri" in name or "Urn" in name:
                    term_def = {"@type": "@id"}
            else:
                term_def = {"@type": "xsd:string"}

            context["@context"][term] = term_def

# Guardar el contexto
with open(CONTEXT_OUT, "w", encoding="utf-8") as f:
    json.dump(context, f, indent=2, ensure_ascii=False)

print(f"✅ context.jsonld generado en: {CONTEXT_OUT}")
