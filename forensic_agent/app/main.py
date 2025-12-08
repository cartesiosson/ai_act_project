"""Forensic Compliance Agent - FastAPI Application"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict

from .services import (
    IncidentExtractorService,
    ForensicSPARQLService,
    ForensicAnalysisEngine,
    PersistenceService
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
persistence_service: Optional[PersistenceService] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global extractor_service, sparql_service, analysis_engine, persistence_service

    print("=" * 80)
    print("FORENSIC COMPLIANCE AGENT - STARTING UP")
    print("=" * 80)

    # Get configuration from environment
    llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp_sparql:8080")

    print(f"\nConfiguration:")
    print(f"  LLM Provider: {llm_provider}")
    print(f"  MCP Server URL: {mcp_server_url}")
    print()

    # Initialize services
    try:
        print("Initializing Incident Extractor...")
        extractor_service = IncidentExtractorService(
            llm_provider=llm_provider,
            api_key=anthropic_api_key
        )
        print("✓ Incident Extractor initialized")

        print("\nInitializing SPARQL Query Service (via MCP)...")
        sparql_service = ForensicSPARQLService(mcp_url=mcp_server_url)
        await sparql_service.ensure_connected()
        print("✓ SPARQL Query Service initialized (MCP client)")

        # Get stats via MCP
        stats = await sparql_service.get_stats()
        print(f"\nOntology Stats (via MCP):")
        print(f"  MCP Connected: {sparql_service._connected}")
        if stats:
            for key, value in stats.items():
                print(f"  {key}: {value}")

        print("\nInitializing Analysis Engine...")
        analysis_engine = ForensicAnalysisEngine(
            extractor=extractor_service,
            sparql=sparql_service
        )
        print("✓ Analysis Engine initialized")

        print("\nInitializing Persistence Service...")
        persistence_service = PersistenceService()
        await persistence_service.ensure_connected()
        print("✓ Persistence Service initialized (MongoDB + Fuseki)")

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

    stats = await sparql_service.get_stats()

    return {
        "status": "healthy",
        "services": {
            "extractor": "operational",
            "sparql": "operational",
            "analysis_engine": "operational"
        },
        "mcp": {
            "connected": sparql_service._connected,
            "stats": stats
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

        # Persist to MongoDB and Fuseki if analysis was successful
        if result.get("status") == "COMPLETED" and persistence_service:
            print("\n[PERSISTENCE] Saving analyzed system to MongoDB and Fuseki...")
            persist_result = await persistence_service.persist_analyzed_system(
                analysis_result=result,
                source=request.source,
                metadata=request.metadata
            )

            if persist_result.get("success"):
                result["persisted"] = {
                    "success": True,
                    "urn": persist_result.get("urn"),
                    "message": "System saved to MongoDB and Fuseki"
                }
                print(f"   ✓ System persisted with URN: {persist_result.get('urn')}")
            else:
                result["persisted"] = {
                    "success": False,
                    "error": persist_result.get("error")
                }
                print(f"   ✗ Persistence failed: {persist_result.get('error')}")

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

    stats = await sparql_service.get_stats()

    return {
        "mcp": {
            "connected": sparql_service._connected,
            "ontology_stats": stats
        },
        "services": {
            "extractor_ready": extractor_service is not None,
            "sparql_ready": sparql_service is not None,
            "analysis_engine_ready": analysis_engine is not None
        }
    }


@app.get("/forensic/systems")
async def list_analyzed_systems(
    limit: int = 20,
    offset: int = 0,
    source: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """List all analyzed AI systems stored in MongoDB."""
    if not persistence_service:
        raise HTTPException(status_code=503, detail="Persistence service not initialized")

    return await persistence_service.get_analyzed_systems(
        limit=limit,
        offset=offset,
        source=source,
        risk_level=risk_level
    )


@app.get("/forensic/systems/{urn:path}")
async def get_analyzed_system(urn: str):
    """Get a specific analyzed system by URN."""
    if not persistence_service:
        raise HTTPException(status_code=503, detail="Persistence service not initialized")

    system = await persistence_service.get_system_by_urn(urn)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    return system


@app.delete("/forensic/systems/{urn:path}")
async def delete_analyzed_system(urn: str):
    """Delete an analyzed system from MongoDB and Fuseki."""
    if not persistence_service:
        raise HTTPException(status_code=503, detail="Persistence service not initialized")

    deleted = await persistence_service.delete_system(urn)
    if not deleted:
        raise HTTPException(status_code=404, detail="System not found")

    return {"status": "deleted", "urn": urn}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
