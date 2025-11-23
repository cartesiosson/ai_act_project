# Forensic Compliance Agent Architecture

## System Design: Llama 3.2 + EU AI Act Ontology + MCP SPARQL

```
┌─────────────────────────────────────────────────────────────────┐
│                   FORENSIC COMPLIANCE AGENT                     │
│              (Llama 3.2 + Ontology + MCP SPARQL)                │
└─────────────────────────────────────────────────────────────────┘

                          ▲
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        │                 │                 │
    ┌───┴───┐         ┌──┴───┐         ┌──┴────┐
    │ Llama │         │ MCP  │         │Ontology
    │ 3.2   │◄────────┤SPARQL├────────►│ Store
    └───┬───┘         └──┬───┘         └──┬────┘
        │                │                │
        │                │                │
        ▼                ▼                ▼
    ┌─────────────────────────────────────────┐
    │         INCIDENT ANALYSIS ENGINE        │
    │                                         │
    │  1. Parse narrative                    │
    │  2. Extract system properties          │
    │  3. Query for requirements             │
    │  4. Identify gaps                      │
    │  5. Generate report                    │
    └─────────────────────────────────────────┘
                        ▼
    ┌─────────────────────────────────────────┐
    │      FORENSIC ANALYSIS REPORT          │
    │                                         │
    │  • System classification                │
    │  • Required requirements                │
    │  • Compliance gaps                      │
    │  • Severity assessment                  │
    │  • Similar incidents                    │
    │  • Enforcement recommendation           │
    └─────────────────────────────────────────┘
                        ▼
    ┌─────────────────────────────────────────┐
    │      EXPERT REVIEW & VALIDATION        │
    │                                         │
    │  • Verify extraction accuracy          │
    │  • Assess Article 6(3) judgment        │
    │  • Determine final enforcement         │
    └─────────────────────────────────────────┘
```

---

## Component 1: Incident Extraction Engine (Llama 3.2)

### Input
Raw incident narrative from AIAAIC database

### Example Input
```
"Facebook's DeepFace facial recognition system generated racially
 biased alt text, identifying Black individuals as 'primates' in
 2015. Incident discovered through user reports. Facebook response:
 apology + removed alt text generation feature. No systemic changes
 to training data or bias detection."
```

### Processing Pipeline

```python
class IncidentExtractor:
    """
    Extracts structured incident information from narratives
    using Llama 3.2 with few-shot prompting
    """

    def extract_incident(self, narrative: str) -> Dict:
        """
        Main extraction pipeline
        """

        # Step 1: System properties
        system_info = self.extract_system_properties(narrative)
        # Returns: type, purpose, capabilities, deployment

        # Step 2: Incident classification
        incident_type = self.classify_incident(narrative)
        # Returns: discrimination, safety, privacy, transparency, etc.

        # Step 3: Affected populations
        affected = self.extract_affected_populations(narrative)
        # Returns: list of affected groups

        # Step 4: Timeline
        timeline = self.extract_timeline(narrative)
        # Returns: discovery date, impact duration, resolution

        # Step 5: Response
        response = self.extract_system_response(narrative)
        # Returns: what organization did about it

        return {
            "system": system_info,
            "incident": incident_type,
            "affected_populations": affected,
            "timeline": timeline,
            "response": response,
            "confidence_scores": self.compute_confidence(narrative)
        }

    def extract_system_properties(self, narrative: str) -> Dict:
        """
        Extract: type, purpose, data types, deployment context
        """
        prompt = f"""
        Analyze this AI incident narrative and extract system properties:

        NARRATIVE:
        {narrative}

        Extract in JSON:
        {{
            "system_name": "...",
            "system_type": "vision|nlp|tabular|multimodal|other",
            "primary_purpose": "...",
            "processes_data_types": ["BiometricData", "PersonalData", ...],
            "deployment_context": ["PublicSpaces", "HighVolume", ...],
            "is_automated_decision": true/false,
            "has_human_oversight": true/false/unknown,
            "model_scale": "FoundationModel|Large|Medium|Small",
            "parameter_count": "...",
            "training_data": "..."
        }}
        """

        response = self.llama.generate(prompt)
        return self.parse_json(response)

    def classify_incident(self, narrative: str) -> str:
        """
        Classify incident type for requirement matching
        """
        incident_types = [
            "discrimination",
            "bias",
            "safety_failure",
            "privacy_violation",
            "transparency_failure",
            "data_leakage",
            "adversarial_attack",
            "model_poisoning",
            "unauthorized_access"
        ]

        prompt = f"""
        Classify this incident into ONE category:
        {', '.join(incident_types)}

        NARRATIVE:
        {narrative}

        Respond with ONLY the category name.
        """

        response = self.llama.generate(prompt)
        return response.strip().lower()

    def extract_affected_populations(self, narrative: str) -> List[str]:
        """
        Identify affected populations (for rights assessment)
        """
        prompt = f"""
        List all affected populations mentioned in this incident:

        NARRATIVE:
        {narrative}

        Respond as JSON array:
        ["population1", "population2", ...]
        """

        response = self.llama.generate(prompt)
        return self.parse_json_array(response)

    def compute_confidence(self, narrative: str) -> Dict:
        """
        Self-assess confidence in extractions
        """
        confidence_prompt = f"""
        For this incident narrative, assess your confidence (0-1) in:
        - System type identification
        - Purpose identification
        - Data types identified
        - Incident classification
        - Affected populations
        - Timeline accuracy

        NARRATIVE:
        {narrative}

        Respond as JSON with confidence scores.
        """

        return self.llama.generate(confidence_prompt)
```

### Output Example

```json
{
  "system": {
    "system_name": "Facebook DeepFace",
    "system_type": "vision",
    "primary_purpose": "Image Recognition / Alt Text Generation",
    "processes_data_types": ["BiometricData", "ImageData", "PersonalData"],
    "deployment_context": ["PublicSpaces", "HighVolume"],
    "is_automated_decision": true,
    "has_human_oversight": false,
    "model_scale": "Large",
    "parameter_count": "Unknown",
    "training_data": "Possibly Facebook user images"
  },
  "incident": "discrimination",
  "affected_populations": ["Black users", "Minorities", "All users"],
  "timeline": {
    "discovery_date": "2015",
    "impact_duration": "Unknown (feature existed from launch)",
    "public_disclosure": "2015",
    "resolution_date": "2015-2016"
  },
  "response": {
    "acknowledged": true,
    "actions_taken": ["Removed alt text generation feature"],
    "systemic_improvements": "None documented",
    "public_apology": true
  },
  "confidence_scores": {
    "system_type": 0.95,
    "purpose": 0.92,
    "data_types": 0.88,
    "incident_classification": 0.96,
    "affected_populations": 0.94,
    "timeline": 0.80
  }
}
```

---

## Component 2: MCP SPARQL Interface

### Role
Bridge between Llama's extracted properties and the EU AI Act ontology

### Interface Definition

```python
class ForensicSPARQLMCP:
    """
    MCP server providing forensic analysis queries
    """

    async def query_mandatory_requirements(self,
                                          purpose: str,
                                          context: str,
                                          data_types: List[str]) -> Dict:
        """
        Given system properties, return ALL mandatory requirements

        Example:
        query_mandatory_requirements(
            purpose="BiometricIdentification",
            context="PublicSpaces",
            data_types=["BiometricData", "PersonalData"]
        )

        Returns:
        {
          "criteria": ["BiometricIdentificationCriterion", ...],
          "requirements": ["BiometricSecurityRequirement", ...],
          "risk_level": "HighRisk"
        }
        """

        sparql = f"""
        PREFIX ai: <http://ai-act.eu/ai#>

        SELECT ?requirement ?label ?type
        WHERE {{
          # Purpose-based criteria
          ai:{purpose} ai:activatesCriterion ?criterion .

          # Context-based criteria
          ai:{context} ai:triggersCriterion ?criterion .

          # Data governance from data types
          {self._data_type_clause(data_types)}

          # Get requirements from criteria
          ?criterion ai:activatesRequirement ?requirement .
          ?requirement rdfs:label ?label ;
                       rdf:type ?type .
        }}
        """

        results = await self.execute_sparql(sparql)
        return self.format_results(results)

    async def query_incident_specific_requirements(self,
                                                   incident_type: str) -> List[str]:
        """
        Given incident type, get related requirements

        incident_type: "discrimination", "safety", "privacy", etc.
        """

        sparql = f"""
        PREFIX ai: <http://ai-act.eu/ai#>

        SELECT ?requirement ?label
        WHERE {{
          # Find criteria related to incident type
          ?criterion rdfs:label ?criterionLabel .
          FILTER(CONTAINS(?criterionLabel, "{incident_type}"))

          # Get their requirements
          ?criterion ai:activatesRequirement ?requirement .
          ?requirement rdfs:label ?label .
        }}
        ORDER BY ?label
        """

        return await self.execute_sparql(sparql)

    async def query_compliance_gaps(self,
                                    mandatory: List[str],
                                    implemented: List[str]) -> Dict:
        """
        Compare what's required vs. what was implemented
        """

        missing = set(mandatory) - set(implemented)

        gap_analysis = {
            "total_required": len(mandatory),
            "implemented": len(implemented),
            "missing": len(missing),
            "compliance_ratio": len(implemented) / len(mandatory),
            "missing_requirements": list(missing),
            "severity": self._assess_severity(missing)
        }

        return gap_analysis

    async def query_similar_systems_at_risk(self,
                                           incident_type: str,
                                           missing_requirement: str) -> List[str]:
        """
        Find other systems with same compliance gap
        """

        sparql = f"""
        PREFIX ai: <http://ai-act.eu/ai#>

        SELECT ?system ?systemName
        WHERE {{
          # Systems with same incident type risk
          ?system a ai:IntelligentSystem ;
                  rdfs:label ?systemName .

          # Check if they have the missing requirement
          MINUS {{
            ?system ai:hasComplianceRequirement ai:{missing_requirement} .
          }}

          # Same purpose/context risks
          ?system ai:hasPurpose ?purpose ;
                  ai:hasDeploymentContext ?context .

          ?purpose rdfs:label ?purposeLabel .
          FILTER(CONTAINS(?purposeLabel, "{incident_type}"))
        }}
        """

        return await self.execute_sparql(sparql)

    async def query_article_6_3_risks(self,
                                      system_properties: Dict) -> List[str]:
        """
        Identify Article 6(3) residual risks

        Article 6(3): "Unforeseen risks not covered by Annex III"
        """

        # Get all requirements that SHOULD apply
        mandatory = await self.query_mandatory_requirements(
            system_properties["purpose"],
            system_properties["context"],
            system_properties["data_types"]
        )

        # Get requirements related to unforeseen risks
        sparql = """
        PREFIX ai: <http://ai-act.eu/ai#>

        SELECT ?criterion ?label
        WHERE {
          ?criterion a ai:Criterion ;
                     rdfs:label ?label ;
                     rdfs:comment ?comment .

          # Find criteria marked as "residual" or "unforeseen"
          FILTER(CONTAINS(?comment, "residual") ||
                 CONTAINS(?comment, "unforeseen"))
        }
        """

        residual_risks = await self.execute_sparql(sparql)
        return residual_risks
```

### Usage in Agent

```python
# Llama extracts incident properties
incident = extractor.extract_incident(narrative)

# Agent queries MCP for requirements
requirements = await mcp.query_mandatory_requirements(
    purpose=incident["system"]["primary_purpose"],
    context=incident["system"]["deployment_context"],
    data_types=incident["system"]["processes_data_types"]
)

# Agent identifies gaps
gaps = await mcp.query_compliance_gaps(
    mandatory=requirements["requirements"],
    implemented=incident["response"]["actions_taken"]
)

# Agent finds similar at-risk systems
similar = await mcp.query_similar_systems_at_risk(
    incident_type=incident["incident"],
    missing_requirement=gaps["missing_requirements"][0]
)
```

---

## Component 3: Analysis Engine

### Process

```python
class ForensicAnalysisEngine:
    """
    Orchestrates extraction, querying, and analysis
    """

    async def analyze_incident(self, narrative: str) -> Dict:
        """
        Complete forensic analysis of an incident
        """

        # Step 1: Extract properties
        print("Extracting incident properties...")
        incident = self.extractor.extract_incident(narrative)

        if incident["confidence_scores"].get("system_type", 0) < 0.7:
            return {
                "status": "LOW_CONFIDENCE",
                "message": "Insufficient detail in narrative for reliable analysis",
                "requires_human_review": True
            }

        # Step 2: Query ontology for proper classification
        print("Querying ontology for mandatory requirements...")
        requirements = await self.mcp.query_mandatory_requirements(
            purpose=incident["system"]["primary_purpose"],
            context=incident["system"]["deployment_context"][0],
            data_types=incident["system"]["processes_data_types"]
        )

        # Step 3: Identify compliance gaps
        print("Analyzing compliance gaps...")
        gaps = await self.mcp.query_compliance_gaps(
            mandatory=requirements["requirements"],
            implemented=self._extract_claimed_requirements(incident)
        )

        # Step 4: Article 6(3) assessment
        print("Checking for Article 6(3) residual risks...")
        article_6_3 = await self.mcp.query_article_6_3_risks(
            incident["system"]
        )

        # Step 5: Find similar at-risk systems
        print("Finding similar systems at risk...")
        similar = await self.mcp.query_similar_systems_at_risk(
            incident_type=incident["incident"],
            missing_requirement=gaps["missing_requirements"][0]
        )

        # Step 6: Generate report (LLM)
        print("Generating compliance report...")
        report = await self._generate_report(
            incident=incident,
            requirements=requirements,
            gaps=gaps,
            article_6_3=article_6_3,
            similar=similar
        )

        return {
            "status": "COMPLETED",
            "extraction": incident,
            "classification": requirements,
            "gaps": gaps,
            "article_6_3": article_6_3,
            "similar_systems": similar,
            "report": report,
            "requires_expert_review": True  # Always flag for human review
        }

    async def _generate_report(self, **kwargs) -> str:
        """
        Use Llama to generate human-readable report
        """

        prompt = f"""
        Generate a forensic compliance audit report based on this analysis:

        System: {kwargs['incident']['system']['system_name']}
        Type: {kwargs['incident']['system']['system_type']}
        Incident: {kwargs['incident']['incident']}

        Mandatory Requirements (from ontology):
        {json.dumps(kwargs['requirements'], indent=2)}

        Compliance Gaps:
        {json.dumps(kwargs['gaps'], indent=2)}

        Article 6(3) Residual Risks:
        {json.dumps(kwargs['article_6_3'], indent=2)}

        Similar Systems at Risk: {len(kwargs['similar_systems'])} systems

        Generate a professional enforcement report including:
        1. Executive Summary
        2. System Classification (proper risk level)
        3. Mandatory Requirements
        4. Compliance Gap Analysis
        5. Root Cause Analysis
        6. Systemic Risk Assessment
        7. Enforcement Recommendation
        8. Remediation Requirements
        """

        report = await self.llama.generate(prompt)
        return report
```

---

## Component 4: Expert Review Interface

### Input to Expert

```json
{
  "status": "REQUIRES_EXPERT_REVIEW",
  "incident_name": "Facebook DeepFace Bias",
  "extraction_confidence": 0.92,

  "agent_analysis": {
    "system_classification": {
      "proper_risk_level": "HighRisk",
      "declared_risk_level": "Unknown (pre-regulation)",
      "basis": "Biometric ID + Public Spaces + Automated Decision"
    },

    "compliance_assessment": {
      "mandatory_requirements": 7,
      "implemented": 2,
      "missing": 5,
      "compliance_ratio": 0.29
    },

    "critical_gaps": [
      "BiasDetectionRequirement",
      "FairnessEvaluationRequirement",
      "BiasMonitoringRequirement",
      "DiversityInTrainingDataRequirement",
      "AlgorithmicAuditRequirement"
    ],

    "article_6_3_candidates": [
      "UnforeseenDiscriminationRisk",
      "UnintendedContextOfUse"
    ],

    "similar_systems_at_risk": 23,
    "enforcement_recommendation": "VIOLATION - Fine €10-15M if 2024"
  },

  "expert_tasks": [
    "Verify system classification accuracy",
    "Assess factual accuracy of extraction",
    "Judge Article 6(3) applicability",
    "Determine temporal applicability (pre/post EU AI Act)",
    "Assess severity and enforcement action",
    "Identify lessons for similar systems"
  ]
}
```

### Expert Verdict

```json
{
  "case_id": "AIAAIC-2015-FB-DEEPFACE",
  "expert_review": {
    "extraction_verified": true,
    "classification_correct": true,
    "article_6_3_assessment": "LIKELY APPLICABLE",
    "temporal_note": "2015 - pre-EU AI Act, but demonstrates regulatory need",
    "enforcement_decision": "Would be violation if 2024",
    "estimated_fine_if_2024": "€12,000,000",
    "systemic_impact": "Identified 23 other facial recognition systems with same gap"
  },

  "published_findings": {
    "summary": "...",
    "impact_assessment": "...",
    "remediation_required": "..."
  }
}
```

---

## Integration with AIAAIC Database

### Data Pipeline

```
AIAAIC Database
     │
     ▼
[INCIDENT NARRATIVES]
     │
     ├─► Agent extracts properties
     │
     ├─► MCP queries ontology
     │
     ├─► Agent analyzes gaps
     │
     └─► Report generated
            │
            ▼
     [EXPERT REVIEW QUEUE]
            │
            ├─► Expert verifies
            │
            ├─► Expert judges
            │
            └─► Final verdict
                  │
                  ▼
           [ENFORCEMENT ACTION]
           [SYSTEMIC PATTERNS]
           [REGULATORY RECOMMENDATIONS]
```

### Batch Processing

```python
async def process_incident_batch(incident_narratives: List[str]):
    """
    Process multiple incidents in parallel
    """

    tasks = [
        self.analyze_incident(narrative)
        for narrative in incident_narratives
    ]

    results = await asyncio.gather(*tasks)

    # Generate summary statistics
    summary = {
        "total_analyzed": len(results),
        "high_confidence": sum(1 for r in results if r.get("status") == "COMPLETED"),
        "violations_detected": sum(1 for r in results if r["gaps"]["missing"] > 0),
        "article_6_3_candidates": sum(1 for r in results if r.get("article_6_3")),
        "similar_systems_at_risk": sum(1 for r in results if len(r.get("similar_systems", [])) > 0)
    }

    return results, summary
```

---

## Why This Architecture Works

| Component | Why It Works |
|-----------|------------|
| **Llama 3.2** | Excellent at NLP extraction, can parse messy narratives |
| **MCP SPARQL** | Deterministic queries, authoritative ontology, full auditability |
| **Ontology** | Single source of truth for requirements, eliminates interpretation variance |
| **Human Review** | Keeps judgment calls (Article 6(3), enforcement) with humans |

This design ensures:
- ✅ Consistency across cases (same law applied the same way)
- ✅ Scalability (can process hundreds of incidents)
- ✅ Transparency (full chain of reasoning is auditable)
- ✅ Accountability (humans make final enforcement decisions)
- ✅ Compliance (aligns with EU regulatory approaches)

