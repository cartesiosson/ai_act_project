"""Forensic Compliance Agent - FastAPI Application"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict

from .services import (
    IncidentExtractorService,
    ForensicSPARQLService,
    ForensicAnalysisEngine
)

# Initialize FastAPI app
app = FastAPI(
    title="Forensic Compliance Agent",
    description="Multi-framework AI incident forensic analysis system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services (initialized on startup)
extractor_service: Optional[IncidentExtractorService] = None
sparql_service: Optional[ForensicSPARQLService] = None
analysis_engine: Optional[ForensicAnalysisEngine] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global extractor_service, sparql_service, analysis_engine

    print("=" * 80)
    print("FORENSIC COMPLIANCE AGENT - STARTING UP")
    print("=" * 80)

    # Get configuration from environment
    llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    ontology_path = os.getenv("ONTOLOGY_PATH", "/ontologias/ontologia-v0.37.2.ttl")
    mappings_path = os.getenv("MAPPINGS_PATH", "/ontologias/mappings")

    print(f"\nConfiguration:")
    print(f"  LLM Provider: {llm_provider}")
    print(f"  Ontology Path: {ontology_path}")
    print(f"  Mappings Path: {mappings_path}")
    print()

    # Initialize services
    try:
        print("Initializing Incident Extractor...")
        extractor_service = IncidentExtractorService(
            llm_provider=llm_provider,
            api_key=anthropic_api_key
        )
        print("✓ Incident Extractor initialized")

        print("\nInitializing SPARQL Query Service...")
        sparql_service = ForensicSPARQLService(
            ontology_path=ontology_path,
            mappings_path=mappings_path
        )
        print("✓ SPARQL Query Service initialized")

        # Get stats
        stats = sparql_service.get_stats()
        print(f"\nOntology Stats:")
        print(f"  Total triples: {stats['total_triples']}")
        print(f"  Ontology loaded: {stats['ontology_loaded']}")
        print(f"  ISO mappings loaded: {stats['iso_mappings_loaded']}")
        print(f"  NIST mappings loaded: {stats['nist_mappings_loaded']}")

        print("\nInitializing Analysis Engine...")
        analysis_engine = ForensicAnalysisEngine(
            extractor=extractor_service,
            sparql=sparql_service
        )
        print("✓ Analysis Engine initialized")

        print("\n" + "=" * 80)
        print("FORENSIC COMPLIANCE AGENT - READY")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ STARTUP FAILED: {e}")
        raise


# Request/Response Models
class IncidentAnalysisRequest(BaseModel):
    """Request model for incident analysis"""
    narrative: str
    source: Optional[str] = "manual"
    metadata: Optional[Dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "narrative": "Facebook's DeepFace facial recognition system generated racially biased alt text, identifying Black individuals as 'primates' in 2015...",
                "source": "AIAAIC",
                "metadata": {
                    "incident_id": "AIAAIC-2015-FB-001",
                    "reporter": "researcher@example.com"
                }
            }
        }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Forensic Compliance Agent",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "analyze": "POST /forensic/analyze",
            "stats": "/forensic/stats"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not all([extractor_service, sparql_service, analysis_engine]):
        raise HTTPException(status_code=503, detail="Services not initialized")

    stats = sparql_service.get_stats()

    return {
        "status": "healthy",
        "services": {
            "extractor": "operational",
            "sparql": "operational",
            "analysis_engine": "operational"
        },
        "ontology": {
            "loaded": stats["ontology_loaded"],
            "triples": stats["total_triples"],
            "iso_mappings": stats["iso_mappings_loaded"],
            "nist_mappings": stats["nist_mappings_loaded"]
        }
    }


@app.post("/forensic/analyze")
async def analyze_incident(request: IncidentAnalysisRequest):
    """
    Analyze an AI incident narrative

    Performs multi-framework forensic analysis including:
    - EU AI Act compliance analysis
    - ISO 42001 certification gap detection
    - NIST AI RMF voluntary guidance assessment

    Returns:
        Comprehensive forensic analysis report
    """
    if not analysis_engine:
        raise HTTPException(status_code=503, detail="Analysis engine not initialized")

    if not request.narrative or len(request.narrative.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Narrative too short. Provide at least 50 characters of incident description."
        )

    try:
        # Run analysis
        result = await analysis_engine.analyze_incident(request.narrative)

        # Add metadata if provided
        if request.metadata:
            result["metadata"] = request.metadata

        result["source"] = request.source

        return result

    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/forensic/stats")
async def get_stats():
    """Get forensic service statistics"""
    if not sparql_service:
        raise HTTPException(status_code=503, detail="SPARQL service not initialized")

    stats = sparql_service.get_stats()

    return {
        "ontology": {
            "total_triples": stats["total_triples"],
            "ontology_loaded": stats["ontology_loaded"],
            "iso_42001_mappings_loaded": stats["iso_mappings_loaded"],
            "nist_ai_rmf_mappings_loaded": stats["nist_mappings_loaded"]
        },
        "services": {
            "extractor_ready": extractor_service is not None,
            "sparql_ready": sparql_service is not None,
            "analysis_engine_ready": analysis_engine is not None
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
