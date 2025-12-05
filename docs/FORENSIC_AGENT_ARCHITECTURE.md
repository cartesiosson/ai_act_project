# Forensic Compliance Agent Architecture (v2.0)

> **Status:** Architecture Design Phase
> **Last Updated:** 2025-12-05
> **Frameworks:** EU AI Act + ISO 42001 + NIST AI RMF

---

## Executive Summary

The Forensic Compliance Agent is a **post-incident analysis system** that:
1. **Extracts** structured properties from incident narratives (LLM-based)
2. **Queries** the EU AI Act ontology to determine mandatory requirements (SPARQL)
3. **Identifies** compliance gaps using multi-framework mappings (EU/ISO/NIST)
4. **Generates** forensic reports with enforcement recommendations
5. **Flags** cases for expert human review and validation

**Key Innovation:** Combines the flexibility of LLMs for extraction with the determinism of semantic reasoning for compliance assessment, enhanced by ISO 42001 and NIST AI RMF cross-framework analysis.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    FORENSIC COMPLIANCE AGENT                         │
│         (LLM Extraction + Ontology Reasoning + Multi-Framework)      │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
        ┌─────────────────┬─────────────┬──────────────────┐
        │  LLM EXTRACTOR  │  ONTOLOGY   │  MULTI-FRAMEWORK │
        │   (Llama 3.2    │   STORE     │    MAPPINGS      │
        │    or Claude)   │  (Fuseki)   │ (ISO + NIST RMF) │
        └─────────────────┴─────────────┴──────────────────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  ▼
                    ┌──────────────────────────┐
                    │  FORENSIC ANALYSIS       │
                    │  ENGINE                  │
                    │                          │
                    │  1. Parse narrative      │
                    │  2. Extract properties   │
                    │  3. Query requirements   │
                    │  4. Multi-framework gaps │
                    │  5. Generate report      │
                    └──────────────────────────┘
                                  ▼
        ┌──────────────────────────────────────────────┐
        │       MULTI-FRAMEWORK FORENSIC REPORT        │
        │                                              │
        │  • EU AI Act Compliance Analysis             │
        │  • ISO 42001 Certification Gaps              │
        │  • NIST AI RMF Voluntary Guidance Check      │
        │  • Cross-Jurisdictional Assessment           │
        │  • Enforcement Recommendations               │
        └──────────────────────────────────────────────┘
                                  ▼
        ┌──────────────────────────────────────────────┐
        │      EXPERT REVIEW & VALIDATION              │
        │                                              │
        │  • Verify extraction accuracy                │
        │  • Assess Article 6(3) judgment              │
        │  • Determine final enforcement               │
        │  • Validate multi-framework analysis         │
        └──────────────────────────────────────────────┘
```

---

## Component 1: Incident Extraction Service

### Technology Choice

**Option A: Llama 3.2 (Local/Self-hosted)**
- ✅ Privacy (no data leaves infrastructure)
- ✅ Cost-effective at scale
- ⚠️ Requires GPU infrastructure
- ⚠️ Quality depends on prompt engineering

**Option B: Claude Sonnet 4.5 (API)**
- ✅ Higher quality extraction
- ✅ Better structured output
- ✅ No GPU infrastructure needed
- ⚠️ API costs (but acceptable for expert tool)
- ⚠️ Data leaves infrastructure (check compliance)

**Recommendation:** Start with **Claude Sonnet 4.5** for pilot, migrate to **Llama 3.2** if volume scales or privacy requirements dictate.

### Service Architecture

```python
# File: backend/app/services/forensic/incident_extractor.py

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import anthropic  # or ollama for Llama

class SystemProperties(BaseModel):
    """Extracted system properties"""
    system_name: str
    system_type: str  # vision, nlp, tabular, multimodal, other
    primary_purpose: str
    processes_data_types: List[str]  # BiometricData, PersonalData, etc.
    deployment_context: List[str]  # PublicSpaces, HighVolume, etc.
    is_automated_decision: bool
    has_human_oversight: Optional[bool]
    model_scale: str  # FoundationModel, Large, Medium, Small
    parameter_count: Optional[str]
    training_data_description: Optional[str]
    organization: str
    jurisdiction: str  # EU, US, Global, etc.

class IncidentClassification(BaseModel):
    """Incident type and severity"""
    incident_type: str  # discrimination, bias, safety_failure, privacy_violation, etc.
    severity: str  # critical, high, medium, low
    affected_populations: List[str]
    affected_count: Optional[int]
    public_disclosure: bool

class Timeline(BaseModel):
    """Incident timeline"""
    discovery_date: str
    impact_start_date: Optional[str]
    impact_duration: Optional[str]
    public_disclosure_date: Optional[str]
    resolution_date: Optional[str]

class OrganizationResponse(BaseModel):
    """How organization responded"""
    acknowledged: bool
    actions_taken: List[str]
    systemic_improvements: Optional[List[str]]
    public_apology: bool
    compensation_provided: bool
    regulatory_action: Optional[str]

class ExtractionConfidence(BaseModel):
    """Confidence scores for validation"""
    system_type: float  # 0.0-1.0
    purpose: float
    data_types: float
    incident_classification: float
    affected_populations: float
    timeline: float
    overall: float

class ExtractedIncident(BaseModel):
    """Complete extracted incident data"""
    system: SystemProperties
    incident: IncidentClassification
    timeline: Timeline
    response: OrganizationResponse
    confidence: ExtractionConfidence
    raw_narrative: str
    extraction_timestamp: str


class IncidentExtractorService:
    """
    Extracts structured incident information from narratives
    using LLM with structured output prompting
    """

    def __init__(self, llm_provider: str = "anthropic"):
        """
        Initialize with LLM provider

        Args:
            llm_provider: "anthropic" (Claude) or "ollama" (Llama)
        """
        self.llm_provider = llm_provider

        if llm_provider == "anthropic":
            self.client = anthropic.Anthropic()
            self.model = "claude-sonnet-4-5-20250929"
        elif llm_provider == "ollama":
            # TODO: Configure Ollama client for Llama 3.2
            self.model = "llama3.2"
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    async def extract_incident(self, narrative: str) -> ExtractedIncident:
        """
        Main extraction pipeline

        Args:
            narrative: Raw incident narrative text

        Returns:
            ExtractedIncident with structured data
        """

        # Build comprehensive extraction prompt
        prompt = self._build_extraction_prompt(narrative)

        # Call LLM with structured output
        response = await self._call_llm(prompt)

        # Parse and validate response
        extracted = self._parse_llm_response(response)

        # Compute confidence scores
        confidence = await self._compute_confidence(narrative, extracted)
        extracted.confidence = confidence

        # Store raw narrative
        extracted.raw_narrative = narrative

        return extracted

    def _build_extraction_prompt(self, narrative: str) -> str:
        """
        Build structured extraction prompt
        """
        return f"""
You are a forensic AI compliance analyst. Extract structured information from this AI incident narrative.

INCIDENT NARRATIVE:
{narrative}

Extract the following information in JSON format:

{{
  "system": {{
    "system_name": "Name of the AI system",
    "system_type": "vision|nlp|tabular|multimodal|other",
    "primary_purpose": "Main purpose of the system",
    "processes_data_types": ["BiometricData", "PersonalData", "HealthData", etc.],
    "deployment_context": ["PublicSpaces", "HighVolume", "RealTime", "CriticalInfrastructure", etc.],
    "is_automated_decision": true/false,
    "has_human_oversight": true/false/null,
    "model_scale": "FoundationModel|Large|Medium|Small",
    "parameter_count": "if mentioned",
    "training_data_description": "if mentioned",
    "organization": "Company/Organization name",
    "jurisdiction": "EU|US|Global|Other"
  }},
  "incident": {{
    "incident_type": "discrimination|bias|safety_failure|privacy_violation|transparency_failure|data_leakage|adversarial_attack|model_poisoning|unauthorized_access|other",
    "severity": "critical|high|medium|low",
    "affected_populations": ["List of affected groups"],
    "affected_count": number or null,
    "public_disclosure": true/false
  }},
  "timeline": {{
    "discovery_date": "YYYY-MM-DD or YYYY-MM or YYYY",
    "impact_start_date": "if mentioned",
    "impact_duration": "if mentioned",
    "public_disclosure_date": "if mentioned",
    "resolution_date": "if mentioned"
  }},
  "response": {{
    "acknowledged": true/false,
    "actions_taken": ["List of actions"],
    "systemic_improvements": ["List of improvements"] or null,
    "public_apology": true/false,
    "compensation_provided": true/false,
    "regulatory_action": "description if any"
  }}
}}

IMPORTANT:
- Extract ONLY information explicitly stated in the narrative
- Use null for unknown information
- For data_types, map to EU AI Act ontology classes when possible:
  * Biometric data → BiometricData
  * Personal information → PersonalData
  * Health records → HealthData
  * Location data → LocationData
  * Financial data → FinancialData
- For deployment_context, identify:
  * PublicSpaces, HighVolume, RealTime, CriticalInfrastructure,
    EducationContext, EmploymentContext, LawEnforcementContext,
    HealthcareContext, MigrationContext

Respond with ONLY valid JSON, no additional text.
"""

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM API"""
        if self.llm_provider == "anthropic":
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.0,  # Deterministic for extraction
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        else:
            # TODO: Implement Ollama call
            raise NotImplementedError("Ollama support pending")

    def _parse_llm_response(self, response: str) -> ExtractedIncident:
        """Parse and validate LLM JSON response"""
        import json
        from datetime import datetime

        # Parse JSON
        data = json.loads(response)

        # Build ExtractedIncident
        return ExtractedIncident(
            system=SystemProperties(**data["system"]),
            incident=IncidentClassification(**data["incident"]),
            timeline=Timeline(**data["timeline"]),
            response=OrganizationResponse(**data["response"]),
            confidence=ExtractionConfidence(
                system_type=0.0,  # Will be computed
                purpose=0.0,
                data_types=0.0,
                incident_classification=0.0,
                affected_populations=0.0,
                timeline=0.0,
                overall=0.0
            ),
            raw_narrative="",  # Will be set by caller
            extraction_timestamp=datetime.utcnow().isoformat()
        )

    async def _compute_confidence(self,
                                  narrative: str,
                                  extracted: ExtractedIncident) -> ExtractionConfidence:
        """
        Compute confidence scores for extraction
        """

        # Simple heuristic-based confidence (can be enhanced with LLM self-assessment)
        confidence = ExtractionConfidence(
            system_type=1.0 if extracted.system.system_type != "other" else 0.5,
            purpose=1.0 if extracted.system.primary_purpose else 0.3,
            data_types=0.9 if len(extracted.system.processes_data_types) > 0 else 0.4,
            incident_classification=0.9,
            affected_populations=0.8 if len(extracted.incident.affected_populations) > 0 else 0.5,
            timeline=0.8 if extracted.timeline.discovery_date else 0.4,
            overall=0.0  # Will compute average
        )

        # Compute overall as average
        scores = [
            confidence.system_type,
            confidence.purpose,
            confidence.data_types,
            confidence.incident_classification,
            confidence.affected_populations,
            confidence.timeline
        ]
        confidence.overall = sum(scores) / len(scores)

        return confidence
```

---

## Component 2: Forensic SPARQL Query Service

### Service Architecture

```python
# File: backend/app/services/forensic/sparql_queries.py

from typing import Dict, List, Optional, Set
from rdflib import Graph, Namespace, URIRef
from rdflib.plugins.sparql import prepareQuery

AI = Namespace("http://ai-act.eu/ai#")
ISO = Namespace("http://iso.org/42001#")
NIST = Namespace("http://nist.gov/ai-rmf#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")


class ForensicSPARQLService:
    """
    SPARQL query service for forensic compliance analysis
    with multi-framework support (EU AI Act + ISO 42001 + NIST AI RMF)
    """

    def __init__(self, fuseki_endpoint: str):
        """
        Initialize with Fuseki endpoint

        Args:
            fuseki_endpoint: URL of Fuseki SPARQL endpoint
        """
        self.endpoint = fuseki_endpoint
        self.graph = Graph()

        # Bind namespaces
        self.graph.bind("ai", AI)
        self.graph.bind("iso", ISO)
        self.graph.bind("nist", NIST)
        self.graph.bind("rdfs", RDFS)

        # Load ontology + mappings
        self._load_ontology()

    def _load_ontology(self):
        """Load ontology and mappings from files"""
        self.graph.parse("ontologias/versions/0.37.2/ontologia-v0.37.2.ttl", format="turtle")
        self.graph.parse("ontologias/mappings/iso-42001-mappings.ttl", format="turtle")
        self.graph.parse("ontologias/mappings/nist-ai-rmf-mappings.ttl", format="turtle")

    async def query_mandatory_requirements(self,
                                          purpose: str,
                                          contexts: List[str],
                                          data_types: List[str]) -> Dict:
        """
        Query ontology for mandatory EU AI Act requirements

        Args:
            purpose: Primary purpose (e.g., "BiometricIdentification")
            contexts: Deployment contexts (e.g., ["PublicSpaces", "HighVolume"])
            data_types: Data types processed (e.g., ["BiometricData"])

        Returns:
            Dict with criteria, requirements, and risk level
        """

        # Build SPARQL query
        query = f"""
        PREFIX ai: <http://ai-act.eu/ai#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?requirement ?requirementLabel ?criterion
        WHERE {{
          # Purpose-based criteria
          {{
            ai:{purpose} ai:activatesCriterion ?criterion .
          }}
          UNION
          {{
            # Context-based criteria
            VALUES ?context {{ {" ".join([f"ai:{c}" for c in contexts])} }}
            ?context ai:triggersCriterion ?criterion .
          }}

          # Get requirements from criteria
          ?criterion ai:activatesRequirement ?requirement .
          ?requirement rdfs:label ?requirementLabel .
        }}
        ORDER BY ?requirementLabel
        """

        results = self.graph.query(query)

        # Parse results
        requirements = []
        criteria = set()

        for row in results:
            requirements.append({
                "uri": str(row.requirement),
                "label": str(row.requirementLabel),
                "criterion": str(row.criterion)
            })
            criteria.add(str(row.criterion))

        # Determine risk level
        risk_level = self._determine_risk_level(list(criteria))

        return {
            "criteria": list(criteria),
            "requirements": requirements,
            "risk_level": risk_level,
            "total_requirements": len(requirements)
        }

    async def query_iso_42001_mappings(self,
                                      eu_requirements: List[str]) -> Dict:
        """
        Query ISO 42001 mappings for EU AI Act requirements

        Args:
            eu_requirements: List of EU AI Act requirement URIs

        Returns:
            Dict with ISO controls mapped to each requirement
        """

        query = """
        PREFIX ai: <http://ai-act.eu/ai#>
        PREFIX iso: <http://iso.org/42001#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?requirement ?isoControl ?isoSection ?isoDescription ?confidence
        WHERE {
          ?requirement ai:equivalentToISOControl ?isoControl ;
                       ai:isoSection ?isoSection ;
                       ai:isoControlDescription ?isoDescription ;
                       ai:mappingConfidence ?confidence .
        }
        """

        results = self.graph.query(query)

        iso_mappings = {}
        for row in results:
            req_uri = str(row.requirement)
            if req_uri in eu_requirements or any(req in req_uri for req in eu_requirements):
                iso_mappings[req_uri] = {
                    "iso_control": str(row.isoControl),
                    "iso_section": str(row.isoSection),
                    "description": str(row.isoDescription),
                    "confidence": str(row.confidence)
                }

        return iso_mappings

    async def query_nist_ai_rmf_mappings(self,
                                        eu_requirements: List[str],
                                        jurisdiction: str = "GLOBAL") -> Dict:
        """
        Query NIST AI RMF mappings for EU AI Act requirements

        Args:
            eu_requirements: List of EU AI Act requirement URIs
            jurisdiction: "US", "GLOBAL", or "EU" (for applicability filtering)

        Returns:
            Dict with NIST functions mapped to each requirement
        """

        query = """
        PREFIX ai: <http://ai-act.eu/ai#>
        PREFIX nist: <http://nist.gov/ai-rmf#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?requirement ?nistFunction ?nistCategory ?nistDescription
               ?confidence ?applicability
        WHERE {
          ?requirement ai:equivalentToNISTFunction ?nistFunction ;
                       ai:nistCategory ?nistCategory ;
                       ai:nistCategoryDescription ?nistDescription ;
                       ai:nistMappingConfidence ?confidence ;
                       ai:nistApplicabilityContext ?applicability .
        }
        """

        results = self.graph.query(query)

        nist_mappings = {}
        for row in results:
            req_uri = str(row.requirement)
            applicability = str(row.applicability)

            # Filter by jurisdiction
            if jurisdiction == "US" and "US_INCIDENTS" not in applicability:
                continue
            if jurisdiction == "GLOBAL" and "GLOBAL_INCIDENTS" not in applicability:
                continue

            if req_uri in eu_requirements or any(req in req_uri for req in eu_requirements):
                nist_mappings[req_uri] = {
                    "nist_function": str(row.nistFunction),
                    "nist_category": str(row.nistCategory),
                    "description": str(row.nistDescription),
                    "confidence": str(row.confidence),
                    "applicability": applicability
                }

        return nist_mappings

    async def analyze_compliance_gaps(self,
                                     mandatory_requirements: List[str],
                                     incident_properties: Dict) -> Dict:
        """
        Analyze compliance gaps based on incident properties

        Args:
            mandatory_requirements: List of required requirement URIs
            incident_properties: Incident details (to infer what was implemented)

        Returns:
            Gap analysis with missing requirements
        """

        # Infer implemented requirements from incident response
        implemented = self._infer_implemented_requirements(incident_properties)

        # Compute gaps
        mandatory_set = set(mandatory_requirements)
        implemented_set = set(implemented)
        missing = mandatory_set - implemented_set

        # Categorize by severity
        critical_gaps = self._categorize_critical_gaps(list(missing))

        return {
            "total_required": len(mandatory_requirements),
            "implemented": len(implemented),
            "missing": len(missing),
            "compliance_ratio": len(implemented) / len(mandatory_requirements) if mandatory_requirements else 0,
            "missing_requirements": list(missing),
            "critical_gaps": critical_gaps,
            "severity": self._assess_gap_severity(len(missing), len(mandatory_requirements))
        }

    def _determine_risk_level(self, criteria: List[str]) -> str:
        """Determine risk level from activated criteria"""
        criteria_str = " ".join(criteria)

        # Check for high-risk indicators
        high_risk_keywords = [
            "Biometric", "LawEnforcement", "Migration", "Employment",
            "Education", "CriticalInfrastructure", "EmotionRecognition"
        ]

        for keyword in high_risk_keywords:
            if keyword in criteria_str:
                return "HighRisk"

        return "LimitedRisk"

    def _infer_implemented_requirements(self, incident_properties: Dict) -> List[str]:
        """
        Infer which requirements were implemented based on incident description

        This is heuristic-based - can be enhanced with LLM reasoning
        """
        implemented = []

        response = incident_properties.get("response", {})
        actions = response.get("actions_taken", [])

        # Simple keyword matching (can be improved)
        action_str = " ".join(actions).lower()

        if "documentation" in action_str or "record" in action_str:
            implemented.append("DocumentationRequirement")

        if "transparency" in action_str or "disclosure" in action_str:
            implemented.append("TransparencyRequirement")

        if "monitoring" in action_str or "audit" in action_str:
            implemented.append("MonitoringRequirement")

        # Most incidents show lack of implementation, so default to minimal
        return implemented

    def _categorize_critical_gaps(self, missing: List[str]) -> List[Dict]:
        """Categorize missing requirements by criticality"""
        critical_keywords = [
            "Biometric", "Security", "Safety", "HumanOversight",
            "FundamentalRights", "NonDiscrimination"
        ]

        critical = []
        for req in missing:
            for keyword in critical_keywords:
                if keyword in req:
                    critical.append({
                        "requirement": req,
                        "reason": f"Critical due to {keyword}"
                    })
                    break

        return critical

    def _assess_gap_severity(self, missing_count: int, total_count: int) -> str:
        """Assess severity of compliance gaps"""
        ratio = missing_count / total_count if total_count > 0 else 0

        if ratio > 0.7:
            return "CRITICAL"
        elif ratio > 0.4:
            return "HIGH"
        elif ratio > 0.2:
            return "MEDIUM"
        else:
            return "LOW"
```

---

## Component 3: Multi-Framework Forensic Analysis Engine

```python
# File: backend/app/services/forensic/analysis_engine.py

from typing import Dict, Optional
from datetime import datetime
from .incident_extractor import IncidentExtractorService, ExtractedIncident
from .sparql_queries import ForensicSPARQLService

class ForensicAnalysisEngine:
    """
    Orchestrates multi-framework forensic analysis of AI incidents
    """

    def __init__(self,
                 extractor: IncidentExtractorService,
                 sparql: ForensicSPARQLService):
        """
        Initialize with extractor and SPARQL services
        """
        self.extractor = extractor
        self.sparql = sparql

    async def analyze_incident(self, narrative: str) -> Dict:
        """
        Complete multi-framework forensic analysis

        Args:
            narrative: Raw incident narrative text

        Returns:
            Comprehensive forensic analysis report
        """

        print("=" * 80)
        print("FORENSIC COMPLIANCE ANALYSIS")
        print("=" * 80)

        # Step 1: Extract incident properties
        print("\n[1/6] Extracting incident properties from narrative...")
        incident = await self.extractor.extract_incident(narrative)

        # Check confidence threshold
        if incident.confidence.overall < 0.6:
            return {
                "status": "LOW_CONFIDENCE",
                "message": "Insufficient detail in narrative for reliable analysis",
                "confidence": incident.confidence.overall,
                "extraction": incident.dict(),
                "requires_human_review": True
            }

        print(f"   ✓ Extraction confidence: {incident.confidence.overall:.2f}")
        print(f"   ✓ System: {incident.system.system_name}")
        print(f"   ✓ Incident type: {incident.incident.incident_type}")
        print(f"   ✓ Jurisdiction: {incident.system.jurisdiction}")

        # Step 2: Query EU AI Act mandatory requirements
        print("\n[2/6] Querying EU AI Act ontology for mandatory requirements...")
        eu_requirements = await self.sparql.query_mandatory_requirements(
            purpose=incident.system.primary_purpose,
            contexts=incident.system.deployment_context,
            data_types=incident.system.processes_data_types
        )

        print(f"   ✓ Risk level: {eu_requirements['risk_level']}")
        print(f"   ✓ Mandatory requirements: {eu_requirements['total_requirements']}")

        # Step 3: Query ISO 42001 mappings
        print("\n[3/6] Querying ISO 42001 mappings...")
        eu_req_uris = [req["uri"] for req in eu_requirements["requirements"]]
        iso_mappings = await self.sparql.query_iso_42001_mappings(eu_req_uris)

        print(f"   ✓ ISO 42001 controls mapped: {len(iso_mappings)}")

        # Step 4: Query NIST AI RMF mappings (if applicable)
        print("\n[4/6] Querying NIST AI RMF mappings...")
        jurisdiction = incident.system.jurisdiction
        nist_mappings = await self.sparql.query_nist_ai_rmf_mappings(
            eu_req_uris,
            jurisdiction=jurisdiction if jurisdiction in ["US", "GLOBAL"] else "GLOBAL"
        )

        print(f"   ✓ NIST AI RMF functions mapped: {len(nist_mappings)}")

        # Step 5: Analyze compliance gaps
        print("\n[5/6] Analyzing compliance gaps...")
        gaps = await self.sparql.analyze_compliance_gaps(
            mandatory_requirements=eu_req_uris,
            incident_properties=incident.dict()
        )

        print(f"   ✓ Compliance ratio: {gaps['compliance_ratio']:.1%}")
        print(f"   ✓ Missing requirements: {gaps['missing']}")
        print(f"   ✓ Gap severity: {gaps['severity']}")

        # Step 6: Generate multi-framework report
        print("\n[6/6] Generating multi-framework forensic report...")
        report = await self._generate_report(
            incident=incident,
            eu_requirements=eu_requirements,
            iso_mappings=iso_mappings,
            nist_mappings=nist_mappings,
            gaps=gaps
        )

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

        return {
            "status": "COMPLETED",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "extraction": incident.dict(),
            "eu_ai_act": eu_requirements,
            "iso_42001": iso_mappings,
            "nist_ai_rmf": nist_mappings,
            "compliance_gaps": gaps,
            "report": report,
            "requires_expert_review": True  # Always flag for human validation
        }

    async def _generate_report(self, **kwargs) -> str:
        """
        Generate human-readable multi-framework forensic report

        Uses LLM to synthesize analysis into enforcement-ready document
        """

        incident = kwargs["incident"]
        eu = kwargs["eu_requirements"]
        iso = kwargs["iso_mappings"]
        nist = kwargs["nist_mappings"]
        gaps = kwargs["gaps"]

        # Build structured report
        report = f"""
# FORENSIC COMPLIANCE AUDIT REPORT

**Report ID:** FCA-{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}
**Analysis Date:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
**Status:** PRELIMINARY - REQUIRES EXPERT REVIEW

---

## 1. EXECUTIVE SUMMARY

**System:** {incident.system.system_name}
**Organization:** {incident.system.organization}
**Incident Type:** {incident.incident.incident_type.upper()}
**Incident Date:** {incident.timeline.discovery_date}
**Jurisdiction:** {incident.system.jurisdiction}

**Severity Assessment:** {gaps["severity"]}
**Compliance Ratio:** {gaps["compliance_ratio"]:.1%} ({gaps["implemented"]}/{gaps["total_required"]} requirements)

---

## 2. SYSTEM CLASSIFICATION

### 2.1 System Properties
- **Type:** {incident.system.system_type}
- **Purpose:** {incident.system.primary_purpose}
- **Processes Data:** {", ".join(incident.system.processes_data_types)}
- **Deployment Context:** {", ".join(incident.system.deployment_context)}
- **Automated Decision:** {"Yes" if incident.system.is_automated_decision else "No"}
- **Human Oversight:** {incident.system.has_human_oversight or "Unknown"}

### 2.2 EU AI Act Risk Classification
**Proper Risk Level:** {eu["risk_level"]}

**Basis:**
- Activated Criteria: {len(eu["criteria"])}
- Mandatory Requirements: {eu["total_requirements"]}

---

## 3. EU AI ACT COMPLIANCE ANALYSIS

### 3.1 Mandatory Requirements
Total Requirements: {eu["total_requirements"]}

{self._format_requirements_list(eu["requirements"])}

### 3.2 Compliance Gaps
**Missing:** {gaps["missing"]} requirements ({gaps["severity"]} severity)

**Critical Gaps:**
{self._format_critical_gaps(gaps["critical_gaps"])}

---

## 4. ISO 42001 CROSS-FRAMEWORK ANALYSIS

### 4.1 Certification Status
**Note:** ISO 42001 certification status unknown from incident narrative.

### 4.2 Failed ISO Controls
The following ISO 42001 controls should have prevented this incident:

{self._format_iso_mappings(iso)}

**Forensic Conclusion:**
If the organization holds ISO 42001 certification, this incident suggests:
- Incomplete implementation of certified controls
- Insufficient audit scope during certification
- Certification obtained before proper control deployment
- **Recommendation:** Review and potentially suspend ISO 42001 certification

---

## 5. NIST AI RMF VOLUNTARY GUIDANCE ANALYSIS

### 5.1 Applicability
**Jurisdiction:** {incident.system.jurisdiction}
**NIST AI RMF Published:** January 2023 (pre-dates incident: {"Yes" if incident.timeline.discovery_date < "2023" else "No"})

### 5.2 NIST Functions Analysis
{self._format_nist_mappings(nist)}

**Forensic Conclusion:**
{"The incident occurred BEFORE NIST AI RMF publication. Voluntary guidance was not available." if incident.timeline.discovery_date < "2023" else "NIST AI RMF voluntary guidance WAS AVAILABLE but appears to have been IGNORED."}

---

## 6. ROOT CAUSE ANALYSIS

### 6.1 Primary Failure Points
{self._infer_root_causes(incident, gaps)}

### 6.2 Contributing Factors
- Lack of {gaps["critical_gaps"][0]["reason"] if gaps["critical_gaps"] else "key requirements"}
- Insufficient {incident.incident.incident_type} prevention measures
- {"No human oversight" if not incident.system.has_human_oversight else "Inadequate human oversight"}

---

## 7. ENFORCEMENT RECOMMENDATION

### 7.1 Temporal Applicability
**Incident Date:** {incident.timeline.discovery_date}
**EU AI Act Enforcement:** August 2, 2024

{"⚠️ **PRE-REGULATION INCIDENT** - EU AI Act was not in force at time of incident." if incident.timeline.discovery_date < "2024" else "✅ **POST-REGULATION INCIDENT** - EU AI Act applies."}

### 7.2 Violation Assessment
{self._assess_violations(incident, gaps)}

### 7.3 Recommended Actions
1. **Immediate:** System deactivation pending compliance audit
2. **Short-term:** Implement all missing requirements ({gaps["missing"]} requirements)
3. **Medium-term:** Full compliance audit with multi-framework validation
4. **Long-term:** Systematic review of similar systems in portfolio

---

## 8. SYSTEMIC RISK ASSESSMENT

### 8.1 Similar Systems at Risk
**Query:** Systems with same purpose + missing requirements
**Status:** Requires database of registered systems (not available in current analysis)

### 8.2 Industry Impact
**Incident Type:** {incident.incident.incident_type}
**Affected Populations:** {", ".join(incident.incident.affected_populations)}
**Public Disclosure:** {"Yes" if incident.incident.public_disclosure else "No"}

---

## 9. EXPERT REVIEW REQUIREMENTS

**This report requires expert validation for:**
- [ ] Verify extraction accuracy from narrative
- [ ] Assess temporal applicability of EU AI Act
- [ ] Evaluate Article 6(3) unforeseen risk assessment
- [ ] Determine appropriate enforcement action
- [ ] Validate multi-framework analysis (ISO/NIST)
- [ ] Calculate fine amount (if applicable)
- [ ] Identify additional systemic risks

---

**Report Generated:** {datetime.utcnow().isoformat()}
**Generated By:** Forensic Compliance Agent v2.0
**Extraction Confidence:** {incident.confidence.overall:.1%}
**Status:** PRELIMINARY - NOT FOR ENFORCEMENT USE WITHOUT EXPERT REVIEW

---
"""

        return report

    def _format_requirements_list(self, requirements: List[Dict]) -> str:
        """Format requirements list for report"""
        lines = []
        for i, req in enumerate(requirements, 1):
            lines.append(f"{i}. **{req['label']}**")
            lines.append(f"   - URI: `{req['uri']}`")
            lines.append(f"   - Activated by: {req['criterion']}")
        return "\n".join(lines)

    def _format_critical_gaps(self, critical_gaps: List[Dict]) -> str:
        """Format critical gaps for report"""
        if not critical_gaps:
            return "No critical gaps identified (all gaps are medium/low severity)"

        lines = []
        for gap in critical_gaps:
            lines.append(f"- **{gap['requirement']}**")
            lines.append(f"  - {gap['reason']}")
        return "\n".join(lines)

    def _format_iso_mappings(self, iso_mappings: Dict) -> str:
        """Format ISO 42001 mappings for report"""
        if not iso_mappings:
            return "No ISO 42001 mappings available for identified requirements."

        lines = []
        for req_uri, mapping in iso_mappings.items():
            req_name = req_uri.split("#")[-1]
            lines.append(f"**{req_name}** → ISO {mapping['iso_section']}")
            lines.append(f"  - Control: {mapping['description']}")
            lines.append(f"  - Confidence: {mapping['confidence']}")
            lines.append("")
        return "\n".join(lines)

    def _format_nist_mappings(self, nist_mappings: Dict) -> str:
        """Format NIST AI RMF mappings for report"""
        if not nist_mappings:
            return "No NIST AI RMF mappings available for identified requirements."

        lines = []
        for req_uri, mapping in nist_mappings.items():
            req_name = req_uri.split("#")[-1]
            lines.append(f"**{req_name}** → NIST {mapping['nist_category']}")
            lines.append(f"  - Function: {mapping['description']}")
            lines.append(f"  - Applicability: {mapping['applicability']}")
            lines.append("")
        return "\n".join(lines)

    def _infer_root_causes(self, incident: ExtractedIncident, gaps: Dict) -> str:
        """Infer root causes from incident and gaps"""
        causes = []

        # Primary cause from incident type
        causes.append(f"1. **Primary:** {incident.incident.incident_type.capitalize()} incident due to missing {gaps['missing']} requirements")

        # Secondary from critical gaps
        if gaps["critical_gaps"]:
            critical = gaps["critical_gaps"][0]
            causes.append(f"2. **Secondary:** {critical['reason']}")

        # Tertiary from system properties
        if not incident.system.has_human_oversight:
            causes.append("3. **Tertiary:** Lack of human oversight mechanisms")

        return "\n".join(causes)

    def _assess_violations(self, incident: ExtractedIncident, gaps: Dict) -> str:
        """Assess violations and recommend penalties"""
        if incident.timeline.discovery_date < "2024":
            return """
**Assessment:** Incident occurred BEFORE EU AI Act enforcement.

**Status:** Not subject to EU AI Act penalties (retroactive application prohibited).

**Note:** This analysis demonstrates what WOULD constitute a violation if incident occurred post-August 2024.

**Recommendation:** Use as case study for similar systems currently deployed.
"""
        else:
            severity = gaps["severity"]
            missing = gaps["missing"]

            if severity == "CRITICAL":
                fine = "€10-15 million or 2% of annual worldwide turnover (whichever is higher)"
                article = "Article 99 (Annex III + multiple requirement violations)"
            elif severity == "HIGH":
                fine = "€5-10 million or 1% of annual worldwide turnover"
                article = "Article 99 (High-risk requirement violations)"
            else:
                fine = "€2-5 million or administrative measures"
                article = "Article 99 (Limited requirement violations)"

            return f"""
**Assessment:** VIOLATION CONFIRMED

**Violated Requirements:** {missing} requirements not implemented
**Severity:** {severity}

**Applicable Penalties:**
- Legal Basis: {article}
- Financial Penalty: {fine}
- Administrative Measures: System deactivation, compliance audit

**Aggravating Factors:**
{"- High public visibility (public disclosure)" if incident.incident.public_disclosure else ""}
- Affected populations: {len(incident.incident.affected_populations)} groups
- Organization response: {"Inadequate" if len(incident.response.actions_taken) < 2 else "Partial"}
"""
```

---

## Component 4: Expert Review Interface

### Web Interface (Future)

```
┌────────────────────────────────────────────────────────────┐
│  FORENSIC ANALYSIS REVIEW QUEUE                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  [ ] Case #FCA-20241205-143022                            │
│      System: Facebook DeepFace                            │
│      Incident: Discrimination (2015)                      │
│      Confidence: 92%                                      │
│      Status: PENDING REVIEW                               │
│      → [Review] [Details] [Multi-Framework Report]       │
│                                                            │
│  [ ] Case #FCA-20241205-143145                            │
│      System: Amazon Rekognition                           │
│      Incident: Bias (2019)                                │
│      Confidence: 88%                                      │
│      Status: PENDING REVIEW                               │
│      → [Review] [Details] [Multi-Framework Report]       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Expert Validation Checklist

```python
class ExpertReviewValidation(BaseModel):
    """Expert review validation schema"""

    case_id: str
    reviewer_name: str
    review_date: str

    # Validation checks
    extraction_accurate: bool
    extraction_notes: Optional[str]

    classification_correct: bool
    classification_notes: Optional[str]

    article_6_3_applicable: bool
    article_6_3_rationale: Optional[str]

    iso_analysis_valid: bool
    nist_analysis_valid: bool

    temporal_applicability: str  # "PRE_REGULATION", "POST_REGULATION"
    enforcement_recommendation: str  # "VIOLATION", "NO_VIOLATION", "REQUIRES_FURTHER_INVESTIGATION"

    estimated_fine: Optional[str]
    remediation_required: List[str]

    systemic_impact_notes: Optional[str]
    similar_systems_identified: Optional[int]

    approved: bool
    final_report: Optional[str]
```

---

## Deployment Architecture

### Docker Services

```yaml
# File: docker-compose.yml (additions)

services:
  forensic_agent:
    build: ./forensic_agent
    depends_on:
      - fuseki
      - backend
    environment:
      - FUSEKI_ENDPOINT=${FUSEKI_ENDPOINT}
      - LLM_PROVIDER=${LLM_PROVIDER}  # anthropic or ollama
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OLLAMA_ENDPOINT=${OLLAMA_ENDPOINT}
    volumes:
      - ./forensic_agent:/app
      - ./ontologias/versions/${CURRENT_RELEASE}:/ontologias:ro
      - ./ontologias/mappings:/ontologias/mappings:ro
    ports:
      - "${FORENSIC_PORT}:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Directory Structure

```
forensic_agent/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── models/
│   │   ├── incident.py            # Pydantic models
│   │   └── forensic_report.py
│   ├── services/
│   │   ├── incident_extractor.py  # LLM extraction
│   │   ├── sparql_queries.py      # Ontology queries
│   │   └── analysis_engine.py     # Orchestration
│   ├── routers/
│   │   ├── forensic.py            # API endpoints
│   │   └── review.py              # Expert review endpoints
│   └── utils/
│       ├── confidence.py          # Confidence scoring
│       └── report_generator.py    # Report formatting
├── tests/
│   ├── test_extraction.py
│   ├── test_sparql.py
│   └── test_analysis.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## API Endpoints

```python
# File: forensic_agent/app/routers/forensic.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/forensic", tags=["forensic"])

class IncidentAnalysisRequest(BaseModel):
    narrative: str
    source: str  # "AIAAIC", "manual", etc.
    metadata: Optional[Dict]

@router.post("/analyze")
async def analyze_incident(request: IncidentAnalysisRequest):
    """
    Analyze an AI incident narrative

    Returns:
        Comprehensive multi-framework forensic analysis
    """
    try:
        analysis = await forensic_engine.analyze_incident(request.narrative)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{case_id}")
async def get_analysis(case_id: str):
    """Get forensic analysis by case ID"""
    # TODO: Retrieve from database
    pass

@router.post("/batch-analyze")
async def batch_analyze(narratives: List[str]):
    """Batch analyze multiple incidents"""
    # TODO: Implement batch processing
    pass

@router.get("/review-queue")
async def get_review_queue():
    """Get pending expert review cases"""
    # TODO: Query database for pending reviews
    pass
```

---

## Next Steps: Implementation Phases

### Phase 1: MVP (Weeks 1-2)
- [ ] Set up forensic_agent service structure
- [ ] Implement IncidentExtractorService with Claude API
- [ ] Implement ForensicSPARQLService
- [ ] Implement basic ForensicAnalysisEngine
- [ ] Create API endpoints
- [ ] Test with 5 sample AIAAIC incidents

### Phase 2: Multi-Framework Integration (Week 3)
- [ ] Integrate ISO 42001 mapping queries
- [ ] Integrate NIST AI RMF mapping queries
- [ ] Enhance report generation with multi-framework sections
- [ ] Add jurisdiction-aware analysis
- [ ] Test with US, EU, and Global incidents

### Phase 3: Expert Review System (Week 4)
- [ ] Design expert review database schema
- [ ] Implement review queue management
- [ ] Create expert validation API
- [ ] Add confidence thresholds and routing
- [ ] Build simple web UI for review queue

### Phase 4: Production Readiness (Week 5-6)
- [ ] Add comprehensive error handling
- [ ] Implement rate limiting and caching
- [ ] Add monitoring and logging
- [ ] Create deployment documentation
- [ ] Performance optimization
- [ ] Security audit

---

## Testing Strategy

### Unit Tests
- Extraction accuracy (precision/recall on labeled test set)
- SPARQL query correctness
- Confidence score calibration
- Report format validation

### Integration Tests
- End-to-end analysis pipeline
- Multi-framework mapping accuracy
- API endpoint reliability

### Validation Tests
- Expert review agreement rate (target: >85%)
- False positive/negative rates
- Temporal applicability accuracy

---

## Success Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Extraction Accuracy | >85% | Expert validation on 100 incidents |
| Requirement Identification | >90% | Compare with manual legal analysis |
| Analysis Time | <60 seconds | Performance benchmarking |
| Expert Agreement | >85% | Inter-rater reliability |
| Multi-Framework Accuracy | >90% | ISO/NIST expert validation |

---

**Architecture Version:** 2.0
**Last Updated:** 2025-12-05
**Status:** Design Complete - Ready for Implementation
**Next Action:** Begin Phase 1 implementation
