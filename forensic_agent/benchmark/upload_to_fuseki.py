#!/usr/bin/env python3
"""
Upload inferred AI systems from benchmark to Fuseki
Creates RDF triples from forensic analysis results
"""

import json
import requests
import sys
from typing import Dict, List
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from datetime import datetime


# Define namespaces
AI = Namespace("http://ai-act.eu/ai#")
FORENSIC = Namespace("http://ai-act.eu/forensic#")


class FusekiUploader:
    """Upload forensic analysis results to Fuseki"""

    def __init__(self, fuseki_url: str = "http://localhost:3030"):
        self.fuseki_url = fuseki_url
        self.dataset = "aiact"
        self.upload_url = f"{fuseki_url}/{self.dataset}/data"

    def check_fuseki(self) -> bool:
        """Check if Fuseki is available"""
        try:
            response = requests.get(f"{self.fuseki_url}/{self.dataset}/query", timeout=5)
            return response.status_code in [200, 400]  # 400 is ok (no query provided)
        except Exception as e:
            print(f"✗ Fuseki not available: {e}")
            return False

    def create_system_graph(self, result: Dict) -> Graph:
        """Create RDF graph for an AI system from forensic analysis"""

        g = Graph()
        g.bind("ai", AI)
        g.bind("forensic", FORENSIC)

        # Extract data
        incident_id = result.get("incident_id", "unknown")
        extraction = result.get("extraction", {})
        system_data = extraction.get("system", {})
        incident_data = extraction.get("incident", {})
        timeline = extraction.get("timeline", {})
        response_data = extraction.get("response", {})
        eu_ai_act = result.get("eu_ai_act", {})
        confidence = extraction.get("confidence", {})

        # Create system URI
        system_uri = FORENSIC[f"System_{incident_id}"]

        # System type
        g.add((system_uri, RDF.type, AI.AISystem))

        # Basic properties
        if system_data.get("system_name"):
            g.add((system_uri, RDFS.label, Literal(system_data["system_name"])))

        if system_data.get("organization"):
            g.add((system_uri, AI.provider, Literal(system_data["organization"])))

        if system_data.get("primary_purpose"):
            g.add((system_uri, AI.purpose, Literal(system_data["primary_purpose"])))

        # Risk level (from EU AI Act analysis)
        risk_level = eu_ai_act.get("risk_level")
        if risk_level:
            g.add((system_uri, AI.hasRiskLevel, Literal(risk_level)))

        # Data types processed
        for data_type in system_data.get("processes_data_types", []):
            g.add((system_uri, AI.processesDataType, Literal(data_type)))

        # Deployment context
        for context in system_data.get("deployment_context", []):
            g.add((system_uri, AI.deploymentContext, Literal(context)))

        # Automated decision
        is_automated = system_data.get("is_automated_decision")
        if is_automated is not None:
            g.add((system_uri, AI.automatedDecisionMaking, Literal(is_automated, datatype=XSD.boolean)))

        # Human oversight
        has_oversight = system_data.get("has_human_oversight")
        if has_oversight is not None:
            g.add((system_uri, AI.humanOversight, Literal(has_oversight, datatype=XSD.boolean)))

        # Jurisdiction
        if system_data.get("jurisdiction"):
            g.add((system_uri, AI.jurisdiction, Literal(system_data["jurisdiction"])))

        # Create incident URI
        incident_uri = FORENSIC[f"Incident_{incident_id}"]
        g.add((incident_uri, RDF.type, FORENSIC.Incident))
        g.add((system_uri, FORENSIC.hasIncident, incident_uri))

        # Incident properties
        if incident_data.get("incident_type"):
            g.add((incident_uri, FORENSIC.incidentType, Literal(incident_data["incident_type"])))

        if incident_data.get("severity"):
            g.add((incident_uri, FORENSIC.severity, Literal(incident_data["severity"])))

        if timeline.get("discovery_date"):
            g.add((incident_uri, FORENSIC.discoveryDate, Literal(timeline["discovery_date"])))

        # Affected populations
        for population in incident_data.get("affected_populations", []):
            g.add((incident_uri, FORENSIC.affectedPopulation, Literal(population)))

        # EU AI Act requirements
        for requirement in eu_ai_act.get("requirements", []):
            req_uri = URIRef(requirement["uri"])
            g.add((system_uri, AI.subjectToRequirement, req_uri))

        # Compliance gaps
        compliance_gaps = result.get("compliance_gaps", {})
        for missing_req in compliance_gaps.get("missing_requirements", []):
            req_uri = URIRef(missing_req)
            g.add((system_uri, FORENSIC.missingRequirement, req_uri))

        # Confidence score
        overall_confidence = confidence.get("overall")
        if overall_confidence is not None:
            g.add((system_uri, FORENSIC.extractionConfidence,
                   Literal(overall_confidence, datatype=XSD.float)))

        # Analysis timestamp
        timestamp = result.get("analysis_timestamp")
        if timestamp:
            g.add((system_uri, FORENSIC.analysisTimestamp,
                   Literal(timestamp, datatype=XSD.dateTime)))

        # Original narrative
        narrative = extraction.get("raw_narrative")
        if narrative:
            g.add((incident_uri, FORENSIC.narrative, Literal(narrative)))

        return g

    def upload_graph(self, graph: Graph, system_id: str) -> bool:
        """Upload graph to Fuseki"""

        try:
            # Serialize to Turtle
            ttl_data = graph.serialize(format='turtle')

            # Upload to Fuseki
            response = requests.post(
                self.upload_url,
                data=ttl_data,
                headers={'Content-Type': 'text/turtle'},
                params={'graph': f'http://ai-act.eu/forensic/systems/{system_id}'},
                timeout=30
            )

            if response.status_code in [200, 201, 204]:
                return True
            else:
                print(f"  ✗ Upload failed: HTTP {response.status_code}")
                print(f"    {response.text[:200]}")
                return False

        except Exception as e:
            print(f"  ✗ Upload error: {e}")
            return False

    def upload_results(self, results: List[Dict]) -> Dict:
        """Upload all successful results to Fuseki"""

        stats = {
            "total": len(results),
            "uploaded": 0,
            "skipped": 0,
            "failed": 0
        }

        print(f"\n{'='*70}")
        print(f"UPLOADING TO FUSEKI")
        print(f"{'='*70}")
        print(f"Target: {self.fuseki_url}/{self.dataset}")
        print(f"Total results: {len(results)}")
        print(f"{'='*70}\n")

        for idx, result in enumerate(results, 1):
            incident_id = result.get("incident_id", f"unknown_{idx}")
            status = result.get("status", "UNKNOWN")

            print(f"[{idx}/{len(results)}] {incident_id}...", end=" ", flush=True)

            if status != "COMPLETED":
                print(f"⊝ Skipped (status: {status})")
                stats["skipped"] += 1
                continue

            # Create RDF graph
            graph = self.create_system_graph(result)

            # Upload to Fuseki
            if self.upload_graph(graph, incident_id):
                print(f"✓ Uploaded ({len(graph)} triples)")
                stats["uploaded"] += 1
            else:
                stats["failed"] += 1

        print(f"\n{'='*70}")
        print(f"UPLOAD SUMMARY")
        print(f"{'='*70}")
        print(f"Total: {stats['total']}")
        print(f"Uploaded: {stats['uploaded']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Failed: {stats['failed']}")
        print(f"{'='*70}\n")

        return stats

    def verify_upload(self, limit: int = 5) -> bool:
        """Verify that systems were uploaded"""

        query = """
        PREFIX forensic: <http://ai-act.eu/forensic#>
        PREFIX ai: <http://ai-act.eu/ai#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?system ?label ?riskLevel ?incidentType
        WHERE {
            ?system a ai:AISystem .
            OPTIONAL { ?system rdfs:label ?label }
            OPTIONAL { ?system ai:hasRiskLevel ?riskLevel }
            OPTIONAL {
                ?system forensic:hasIncident ?incident .
                ?incident forensic:incidentType ?incidentType
            }
        }
        LIMIT %d
        """ % limit

        try:
            response = requests.post(
                f"{self.fuseki_url}/{self.dataset}/query",
                data={'query': query},
                headers={'Accept': 'application/sparql-results+json'},
                timeout=30
            )

            if response.status_code == 200:
                results = response.json()
                bindings = results.get("results", {}).get("bindings", [])

                if bindings:
                    print(f"\n✓ Verification successful - Found {len(bindings)} systems:")
                    for binding in bindings:
                        label = binding.get("label", {}).get("value", "Unknown")
                        risk = binding.get("riskLevel", {}).get("value", "Unknown")
                        inc_type = binding.get("incidentType", {}).get("value", "Unknown")
                        print(f"  - {label} (Risk: {risk}, Type: {inc_type})")
                    return True
                else:
                    print("✗ No systems found in Fuseki")
                    return False
            else:
                print(f"✗ Query failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Verification error: {e}")
            return False


def main():
    # Find most recent results file
    results_dir = Path(__file__).parent / "results"

    if not results_dir.exists():
        print(f"✗ Results directory not found: {results_dir}")
        print("Run run_benchmark.py first")
        sys.exit(1)

    # Get most recent results file
    results_files = sorted(results_dir.glob("benchmark_results_*.json"), reverse=True)

    if not results_files:
        print(f"✗ No results files found in {results_dir}")
        print("Run run_benchmark.py first")
        sys.exit(1)

    results_file = results_files[0]
    print(f"✓ Loading results from: {results_file}")

    with open(results_file) as f:
        results = json.load(f)

    print(f"✓ Loaded {len(results)} results")

    # Create uploader
    uploader = FusekiUploader()

    # Check Fuseki
    print("Checking Fuseki availability...", end=" ")
    if not uploader.check_fuseki():
        sys.exit(1)
    print("✓")

    # Upload results
    stats = uploader.upload_results(results)

    # Verify upload
    if stats["uploaded"] > 0:
        uploader.verify_upload(limit=5)

    return stats


if __name__ == "__main__":
    main()
