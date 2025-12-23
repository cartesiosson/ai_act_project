"""Forensic Compliance Agent - FastAPI Application"""

import os
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, AsyncGenerator

from .services import (
    IncidentExtractorService,
    ForensicSPARQLService,
    ForensicAnalysisEngine,
    PersistenceService,
    EvidencePlannerService,
    ForensicReActAgent
)
from .models.forensic_report import StreamEvent, StreamEventType

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
evidence_planner: Optional[EvidencePlannerService] = None
react_agent: Optional[ForensicReActAgent] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global extractor_service, sparql_service, analysis_engine, persistence_service, evidence_planner, react_agent

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

        print("\nInitializing Evidence Planner Service...")
        evidence_planner = EvidencePlannerService()
        print("✓ Evidence Planner Service initialized (DPV mappings)")

        # Initialize ReAct Agent (optional - only if Ollama is available)
        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        react_enabled = os.getenv("REACT_AGENT_ENABLED", "false").lower() == "true"

        if react_enabled:
            print(f"\nInitializing ReAct Agent (LangGraph + Ollama)...")
            print(f"  Ollama Endpoint: {ollama_endpoint}")
            print(f"  Model: {ollama_model}")
            try:
                react_agent = ForensicReActAgent(
                    sparql_service=sparql_service,
                    extractor_service=extractor_service,
                    ollama_base_url=ollama_endpoint,
                    model_name=ollama_model
                )
                print("✓ ReAct Agent initialized")
            except Exception as e:
                print(f"⚠ ReAct Agent initialization failed (optional): {e}")
                react_agent = None
        else:
            print("\nReAct Agent: Disabled (set REACT_AGENT_ENABLED=true to enable)")

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
        "version": "1.1.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "analyze": "POST /forensic/analyze",
            "evidence_plan": "POST /forensic/evidence-plan",
            "stats": "/forensic/stats"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not all([extractor_service, sparql_service, analysis_engine]):
        raise HTTPException(status_code=503, detail="Services not initialized")

    stats = await sparql_service.get_stats()

    # Get LLM info
    llm_info = {
        "provider": extractor_service.llm_provider if extractor_service else "unknown",
        "model": extractor_service.model if extractor_service else "unknown"
    }

    # ReAct agent info
    react_info = None
    if react_agent:
        react_info = {
            "enabled": True,
            "model": react_agent.model_name,
            "ollama_url": react_agent.ollama_base_url
        }

    return {
        "status": "healthy",
        "services": {
            "extractor": "operational",
            "sparql": "operational",
            "analysis_engine": "operational",
            "react_agent": "operational" if react_agent else "disabled"
        },
        "llm": llm_info,
        "react_agent": react_info,
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
            "analysis_engine_ready": analysis_engine is not None,
            "evidence_planner_ready": evidence_planner is not None
        }
    }


@app.post("/forensic/analyze-stream")
async def analyze_incident_stream(request: IncidentAnalysisRequest):
    """
    Analyze an AI incident narrative with Server-Sent Events streaming.

    Returns real-time updates of the analysis process including:
    - LLM prompts and responses
    - SPARQL queries and results
    - Step-by-step progress
    - Final analysis result
    """
    if not analysis_engine:
        raise HTTPException(status_code=503, detail="Analysis engine not initialized")

    if not request.narrative or len(request.narrative.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Narrative too short. Provide at least 50 characters of incident description."
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events during analysis"""
        try:
            # Run analysis with streaming
            async for event in analysis_engine.analyze_incident_streaming(request.narrative):
                # Format as SSE
                event_data = event.model_dump() if hasattr(event, 'model_dump') else event.dict()
                yield f"data: {json.dumps(event_data)}\n\n"

            # After analysis, handle persistence
            result = analysis_engine.last_result
            if result and result.get("status") == "COMPLETED":
                # Add metadata
                if request.metadata:
                    result["metadata"] = request.metadata
                result["source"] = request.source

                # Persist
                if persistence_service:
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

                # Send final result
                final_event = StreamEvent(
                    event_type=StreamEventType.ANALYSIS_COMPLETE,
                    step_name="Complete",
                    data=result,
                    progress_percent=100.0
                )
                yield f"data: {json.dumps(final_event.model_dump())}\n\n"

        except Exception as e:
            error_event = StreamEvent(
                event_type=StreamEventType.ERROR,
                step_name="Error",
                data={"error": str(e)}
            )
            yield f"data: {json.dumps(error_event.model_dump())}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/forensic/analyze-stream-with-evidence-plan")
async def analyze_stream_with_evidence_plan(request: IncidentAnalysisRequest):
    """
    Analyze an incident with streaming AND generate an evidence plan.

    Combines forensic analysis streaming with evidence planning.
    """
    if not analysis_engine or not evidence_planner:
        raise HTTPException(status_code=503, detail="Services not initialized")

    if not request.narrative or len(request.narrative.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Narrative too short. Provide at least 50 characters."
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events during analysis with evidence plan"""
        try:
            # Run analysis with streaming
            async for event in analysis_engine.analyze_incident_streaming(request.narrative):
                event_data = event.model_dump() if hasattr(event, 'model_dump') else event.dict()
                yield f"data: {json.dumps(event_data)}\n\n"

            # Get final result
            result = analysis_engine.last_result
            if result and result.get("status") == "COMPLETED":
                # Add metadata
                if request.metadata:
                    result["metadata"] = request.metadata
                result["source"] = request.source

                # Generate evidence plan
                compliance_gaps = result.get("compliance_gaps", {})
                missing_reqs = compliance_gaps.get("missing_requirements", [])
                critical_gaps = compliance_gaps.get("critical_gaps", [])

                if missing_reqs:
                    system_name = result.get("extraction", {}).get("system", {}).get("system_name", "Unknown System")
                    risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")

                    plan = evidence_planner.generate_plan(
                        system_name=system_name,
                        risk_level=risk_level,
                        missing_requirements=missing_reqs,
                        critical_gaps=critical_gaps
                    )
                    result["evidence_plan"] = evidence_planner.to_dict(plan)

                # Persist
                if persistence_service:
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

                # Send final result
                final_event = StreamEvent(
                    event_type=StreamEventType.ANALYSIS_COMPLETE,
                    step_name="Complete",
                    data=result,
                    progress_percent=100.0
                )
                yield f"data: {json.dumps(final_event.model_dump())}\n\n"

        except Exception as e:
            error_event = StreamEvent(
                event_type=StreamEventType.ERROR,
                step_name="Error",
                data={"error": str(e)}
            )
            yield f"data: {json.dumps(error_event.model_dump())}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/forensic/analyze-react")
async def analyze_incident_react(request: IncidentAnalysisRequest):
    """
    Analyze an AI incident using the ReAct (Reasoning + Acting) agent.

    This endpoint uses LangGraph with Ollama (Llama 3.2) to dynamically
    decide which regulatory frameworks to query based on the incident.

    The agent uses a Thought -> Action -> Observation loop to:
    - Extract incident properties
    - Decide which frameworks apply (EU AI Act, NIST, ISO)
    - Query only relevant regulations
    - Generate a forensic report

    Requires: REACT_AGENT_ENABLED=true and Ollama running with llama3.2
    """
    if not react_agent:
        raise HTTPException(
            status_code=503,
            detail="ReAct agent not initialized. Set REACT_AGENT_ENABLED=true and ensure Ollama is running."
        )

    if not request.narrative or len(request.narrative.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Narrative too short. Provide at least 50 characters."
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events during ReAct agent analysis"""
        try:
            async for event in react_agent.analyze_incident_streaming(request.narrative):
                event_data = event.model_dump() if hasattr(event, 'model_dump') else event.dict()
                yield f"data: {json.dumps(event_data)}\n\n"

            # Send final completion event
            final_event = StreamEvent(
                event_type=StreamEventType.ANALYSIS_COMPLETE,
                step_name="ReAct Analysis Complete",
                data={
                    "status": "COMPLETED",
                    "agent_type": "react",
                    "model": react_agent.model_name
                },
                progress_percent=100.0
            )
            yield f"data: {json.dumps(final_event.model_dump())}\n\n"

        except Exception as e:
            error_event = StreamEvent(
                event_type=StreamEventType.ERROR,
                step_name="ReAct Agent Error",
                data={"error": str(e)}
            )
            yield f"data: {json.dumps(error_event.model_dump())}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Evidence Plan Request Model
class EvidencePlanRequest(BaseModel):
    """Request model for evidence plan generation"""
    system_name: str
    risk_level: str
    missing_requirements: list
    critical_gaps: list = []
    jurisdiction: str = "EU"
    format: str = "json"  # "json" or "markdown"

    class Config:
        json_schema_extra = {
            "example": {
                "system_name": "Facial Recognition System",
                "risk_level": "HighRisk",
                "missing_requirements": [
                    "http://ai-act.eu/ai#HumanOversightRequirement",
                    "http://ai-act.eu/ai#FundamentalRightsAssessmentRequirement"
                ],
                "critical_gaps": [
                    {"requirement": "http://ai-act.eu/ai#HumanOversightRequirement", "reason": "Critical: Human oversight requirement"}
                ],
                "format": "json"
            }
        }


@app.post("/forensic/evidence-plan")
async def generate_evidence_plan(request: EvidencePlanRequest):
    """
    Generate an evidence plan based on compliance gaps.

    Takes the compliance gaps from a forensic analysis and generates
    a structured plan for evidence generation using DPV (Data Privacy Vocabulary)
    mappings.

    Returns:
        Evidence plan with required documentation, assessments, and policies
    """
    if not evidence_planner:
        raise HTTPException(status_code=503, detail="Evidence planner not initialized")

    if not request.missing_requirements:
        raise HTTPException(
            status_code=400,
            detail="No missing requirements provided. Run forensic analysis first."
        )

    try:
        # Generate evidence plan
        plan = evidence_planner.generate_plan(
            system_name=request.system_name,
            risk_level=request.risk_level,
            missing_requirements=request.missing_requirements,
            critical_gaps=request.critical_gaps,
            jurisdiction=request.jurisdiction
        )

        if request.format == "markdown":
            return {
                "plan_id": plan.plan_id,
                "format": "markdown",
                "content": evidence_planner.generate_markdown_report(plan)
            }
        else:
            return evidence_planner.to_dict(plan)

    except Exception as e:
        print(f"Evidence plan generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Evidence plan generation failed: {str(e)}"
        )


@app.post("/forensic/analyze-with-evidence-plan")
async def analyze_with_evidence_plan(request: IncidentAnalysisRequest):
    """
    Analyze an incident AND generate an evidence plan in one call.

    Combines forensic analysis with evidence planning to provide
    a complete compliance remediation package.
    """
    if not analysis_engine or not evidence_planner:
        raise HTTPException(status_code=503, detail="Services not initialized")

    if not request.narrative or len(request.narrative.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Narrative too short. Provide at least 50 characters."
        )

    try:
        # Run forensic analysis
        result = await analysis_engine.analyze_incident(request.narrative)

        # Add metadata
        if request.metadata:
            result["metadata"] = request.metadata
        result["source"] = request.source

        # If analysis completed, generate evidence plan
        if result.get("status") == "COMPLETED":
            compliance_gaps = result.get("compliance_gaps", {})
            missing_reqs = compliance_gaps.get("missing_requirements", [])
            critical_gaps = compliance_gaps.get("critical_gaps", [])

            if missing_reqs:
                system_name = result.get("extraction", {}).get("system", {}).get("system_name", "Unknown System")
                risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")

                plan = evidence_planner.generate_plan(
                    system_name=system_name,
                    risk_level=risk_level,
                    missing_requirements=missing_reqs,
                    critical_gaps=critical_gaps
                )

                result["evidence_plan"] = evidence_planner.to_dict(plan)

        # Persist if successful
        if result.get("status") == "COMPLETED" and persistence_service:
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

        return result

    except Exception as e:
        print(f"Analysis with evidence plan error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


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
