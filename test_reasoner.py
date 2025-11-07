"""
Test directo del reasoner service
"""

import requests
import tempfile
import os

def test_basic_ttl():
    # TTL básico sin reglas SWRL
    basic_ttl = """
@prefix ai: <http://ai-act.eu/ai#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<urn:uuid:test-system> a ai:IntelligentSystem ;
    ai:hasName "Test System" ;
    ai:hasPurpose ai:EducationAccess ;
    ai:hasDeploymentContext ai:Education .
"""

    # Reglas SWRL simples
    simple_rules = """
@prefix ai: <http://ai-act.eu/ai#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

# Sin reglas por ahora, solo datos
"""

    # Probar el reasoner
    files = {
        'data': ('test.ttl', basic_ttl.encode(), 'text/turtle'),
        'swrl_rules': ('rules.ttl', simple_rules.encode(), 'text/turtle')
    }

    response = requests.post('http://localhost:8001/reason', files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")

if __name__ == "__main__":
    test_basic_ttl()