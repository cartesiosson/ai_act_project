"""Incident extraction service using LLM"""

import json
import os
from typing import Optional
from datetime import datetime
import anthropic
import httpx

from ..models.incident import (
    ExtractedIncident,
    SystemProperties,
    IncidentClassification,
    Timeline,
    OrganizationResponse,
    ExtractionConfidence
)


class IncidentExtractorService:
    """
    Extracts structured incident information from narratives
    using LLM with structured output prompting
    """

    def __init__(self, llm_provider: str = "anthropic", api_key: Optional[str] = None,
                 ollama_endpoint: Optional[str] = None, ollama_model: Optional[str] = None):
        """
        Initialize with LLM provider

        Args:
            llm_provider: "anthropic" (Claude) or "ollama" (Llama)
            api_key: API key for Anthropic (if None, reads from env)
            ollama_endpoint: Ollama endpoint URL (default: http://localhost:11434)
            ollama_model: Ollama model name (default: llama3.2)
        """
        self.llm_provider = llm_provider

        if llm_provider == "anthropic":
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")

            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-sonnet-4-5-20250929"
        elif llm_provider == "ollama":
            self.ollama_endpoint = ollama_endpoint or os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
            self.model = ollama_model or os.getenv("OLLAMA_MODEL", "llama3.2")
            self.client = httpx.AsyncClient(timeout=120.0)
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
        confidence = self._compute_confidence(narrative, extracted)
        extracted.confidence = confidence

        # Store raw narrative
        extracted.raw_narrative = narrative
        extracted.extraction_timestamp = datetime.utcnow().isoformat()

        return extracted

    def _build_extraction_prompt(self, narrative: str) -> str:
        """
        Build structured extraction prompt
        """
        return f"""You are a forensic AI compliance analyst. Extract structured information from this AI incident narrative.

INCIDENT NARRATIVE:
{narrative}

Extract the following information in JSON format:

{{
  "system": {{
    "system_name": "Name of the AI system",
    "system_type": "vision|nlp|tabular|multimodal|other",
    "primary_purpose": "REQUIRED - Main purpose. MUST be one of these EU AI Act ontology values: BiometricIdentification, LawEnforcementSupport, MigrationControl, EducationAccess, RecruitmentOrEmployment, WorkforceEvaluationPurpose, CriticalInfrastructureOperation, HealthCare, JudicialDecisionSupport, PublicServiceAllocation, GenerativeAIContentCreation, SurveillanceMonitoring. Choose the closest match. Use CriticalInfrastructureOperation for autonomous vehicles, robots, drones, weapons, Tesla, autopilot. Use SurveillanceMonitoring for smart home devices, cameras, doorbells, tracking. Use GenerativeAIContentCreation for AI art, chatbots, LLMs, deepfakes.",
    "processes_data_types": ["BiometricData", "PersonalData", "HealthData", "LocationData", "FinancialData", etc.],
    "deployment_context": ["PublicSpaces", "HighVolume", "RealTime", "CriticalInfrastructure", "EducationContext", "EmploymentContext", "LawEnforcementContext", "HealthcareContext", "MigrationContext", etc.],
    "is_automated_decision": true/false,
    "has_human_oversight": true/false/null,
    "model_scale": "FoundationModel|Large|Medium|Small",
    "parameter_count": "if mentioned, otherwise null",
    "training_data_description": "if mentioned, otherwise null",
    "organization": "Company/Organization name (legacy field - also fill deployer/developer if known)",
    "jurisdiction": "EU|US|Global|Other",
    "deployer": "Entity that deploys/operates the AI system (Art. 3.4 EU AI Act) - may differ from developer",
    "developer": "Entity that developed/created the AI system - may differ from deployer",
    "prohibited_practices": ["List of Article 5 prohibited practices if detected: SubliminalManipulation, VulnerabilityExploitation, SocialScoring, PredictivePolicing, RealTimeBiometricIdentification. Leave empty if none detected."],
    "legal_exceptions": ["If RealTimeBiometricIdentification is detected, check for legal exceptions: VictimSearchException, TerroristThreatException, SeriousCrimeException. Otherwise empty."],
    "has_judicial_authorization": true/false/null "Only relevant if real-time biometric ID with exceptions. Does the narrative mention judicial/court authorization?",
    "performs_profiling": true/false "Does the system perform profiling of natural persons? (Art. 6.3 EU AI Act - automatic risk escalation to HighRisk if true). Profiling = automated processing of personal data to evaluate, analyze or predict aspects concerning natural person's performance at work, economic situation, health, preferences, interests, reliability, behavior, location or movements."
  }},
  "incident": {{
    "incident_type": "discrimination|bias|safety_failure|privacy_violation|transparency_failure|data_leakage|adversarial_attack|model_poisoning|unauthorized_access|appropriation|copyright|other",
    "severity": "critical|high|medium|low",
    "affected_populations": ["List of affected groups"],
    "affected_count": number or null,
    "public_disclosure": true/false
  }},
  "timeline": {{
    "discovery_date": "YYYY-MM-DD or YYYY-MM or YYYY (as specific as possible)",
    "impact_start_date": "if mentioned, otherwise null",
    "impact_duration": "if mentioned, otherwise null",
    "public_disclosure_date": "if mentioned, otherwise null",
    "resolution_date": "if mentioned, otherwise null"
  }},
  "response": {{
    "acknowledged": true/false,
    "actions_taken": ["List of actions the organization took"],
    "systemic_improvements": ["List of systemic improvements"] or null,
    "public_apology": true/false,
    "compensation_provided": true/false,
    "regulatory_action": "description if any regulatory action was taken, otherwise null"
  }}
}}

IMPORTANT EXTRACTION RULES:
- Extract information from the narrative
- Use null for unknown information EXCEPT for primary_purpose (see below)
- For data_types, map to EU AI Act ontology classes when possible:
  * Biometric data (face, fingerprint, iris, etc.) → BiometricData
  * Personal information, names, emails → PersonalData
  * Health records, medical data → HealthData
  * GPS, location tracking → LocationData
  * Banking, credit data → FinancialData
- For deployment_context, identify contextual factors:
  * PublicSpaces: deployed in public areas
  * HighVolume: processes large amounts of data
  * RealTime: real-time decision making
  * CriticalInfrastructure: used in critical systems
  * EducationContext, EmploymentContext, LawEnforcementContext, etc.
- For primary_purpose (REQUIRED - NEVER return null):
  * MUST use EXACTLY one of these ontology IRIs:
    - BiometricIdentification: facial recognition, fingerprint, iris scan, voice ID
    - LawEnforcementSupport: police systems, criminal investigation, predictive policing
    - MigrationControl: border control, asylum processing, immigration
    - EducationAccess: student evaluation, exam grading, educational AI
    - RecruitmentOrEmployment: hiring, CV screening, job applications
    - WorkforceEvaluationPurpose: employee monitoring, performance evaluation
    - CriticalInfrastructureOperation: autonomous vehicles, robots (including delivery robots like Starship, sidewalk robots), drones, weapons, military, Tesla, autopilot, energy, transport - ANY robot interacting with public spaces
    - HealthCare: medical diagnosis, clinical decision support, patient care
    - JudicialDecisionSupport: court decisions, sentencing, recidivism prediction
    - PublicServiceAllocation: credit scoring, social benefits, insurance, welfare
    - GenerativeAIContentCreation: AI art, chatbots, LLMs, deepfakes, synthetic media, image/text generation
    - SurveillanceMonitoring: smart home devices, cameras, doorbells (Ring), CCTV, tracking, IoT security
  * Map the described purpose to the closest matching IRI above
- For incident_type:
  * discrimination: unfair treatment of protected groups
  * bias: algorithmic bias leading to unfair outcomes
  * safety_failure: system caused physical harm or danger
  * privacy_violation: unauthorized data collection/use
  * transparency_failure: lack of disclosure about AI use
  * data_leakage: sensitive data exposed
  * appropriation: using data/content without authorization for AI training
  * copyright: AI system infringes copyrights or produces infringing content
- For severity:
  * critical: widespread harm, fundamental rights violated
  * high: significant harm to many people
  * medium: moderate harm or limited scope
  * low: minimal harm or quickly resolved
- For deployer/developer (AIRO stakeholder alignment):
  * deployer: The entity that uses/operates the AI system under their authority (Art. 3.4 EU AI Act)
    - Example: A bank using a credit scoring AI → deployer is the bank
    - Example: A police department using facial recognition → deployer is the police department
  * developer: The entity that created/built the AI system
    - Example: OpenAI creates ChatGPT → developer is OpenAI
    - Example: A bank uses a vendor's AI → developer is the vendor
  * If the same entity both developed and deploys the system, set both to the same value
  * These map to AIRO ontology: airo:AIDeployer and airo:AIDeveloper
  * Use null only if truly unknown from the narrative
- For prohibited_practices (Article 5 - Unacceptable Risk):
  * SubliminalManipulation: AI uses subliminal techniques beyond conscious awareness to manipulate behavior
  * VulnerabilityExploitation: AI exploits vulnerabilities of age (minors), disability, or economic disadvantage to manipulate behavior
  * SocialScoring: AI performs social scoring by public authorities leading to detrimental treatment (China-style social credit systems)
  * PredictivePolicing: AI predicts crime risk based SOLELY on profiling without objective criminal behavior evidence
  * RealTimeBiometricIdentification: Real-time remote biometric identification (e.g., facial recognition) in publicly accessible spaces
  * Systems with these practices CANNOT be deployed in the EU (maximum penalties: €35M or 7% global revenue)
  * ONLY RealTimeBiometricIdentification has limited exceptions under Article 5.2
- For legal_exceptions (ONLY if RealTimeBiometricIdentification detected):
  * VictimSearchException: Searching for victims (kidnapping, missing children, human trafficking)
  * TerroristThreatException: Prevention of specific, substantial terrorist threat
  * SeriousCrimeException: Detection/prosecution of serious crimes (3+ years imprisonment)
  * ALL exceptions require prior judicial authorization
- For has_judicial_authorization:
  * true: Narrative explicitly mentions court/judicial/magistrate authorization
  * false: Narrative explicitly states NO authorization
  * null: Authorization status unknown from narrative

Respond with ONLY valid JSON, no additional text or markdown formatting.
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
        elif self.llm_provider == "ollama":
            # Call Ollama API
            url = f"{self.ollama_endpoint}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for deterministic extraction
                    "num_predict": 4096
                }
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")
        else:
            raise NotImplementedError(f"LLM provider {self.llm_provider} not supported")

    def _normalize_to_list(self, value, field_name: str) -> list:
        """Normalize a value to a list (handles LLM returning strings instead of lists)"""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            # If it's a comma-separated string, split it
            if "," in value:
                return [v.strip() for v in value.split(",") if v.strip()]
            # Single value - wrap in list
            return [value] if value.strip() else []
        return []

    def _parse_llm_response(self, response: str) -> ExtractedIncident:
        """Parse and validate LLM JSON response"""

        # Clean response (remove markdown if present)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {response[:500]}")

        # Normalize system data - ensure list fields are actually lists
        system_data = data.get("system", {})
        system_data["processes_data_types"] = self._normalize_to_list(
            system_data.get("processes_data_types"), "processes_data_types"
        )
        system_data["deployment_context"] = self._normalize_to_list(
            system_data.get("deployment_context"), "deployment_context"
        )

        # Normalize incident data
        incident_data = data.get("incident", {})
        incident_data["affected_populations"] = self._normalize_to_list(
            incident_data.get("affected_populations"), "affected_populations"
        )

        # Clean up response data - convert null to appropriate defaults for required boolean fields
        response_data = data.get("response", {})
        if response_data.get("compensation_provided") is None:
            response_data["compensation_provided"] = False
        if response_data.get("public_apology") is None:
            response_data["public_apology"] = False
        # Normalize list fields in response
        response_data["actions_taken"] = self._normalize_to_list(
            response_data.get("actions_taken"), "actions_taken"
        )
        response_data["systemic_improvements"] = self._normalize_to_list(
            response_data.get("systemic_improvements"), "systemic_improvements"
        ) or None  # Keep None if empty for optional field

        # Build ExtractedIncident
        return ExtractedIncident(
            system=SystemProperties(**system_data),
            incident=IncidentClassification(**incident_data),
            timeline=Timeline(**data.get("timeline", {})),
            response=OrganizationResponse(**response_data),
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

    def _compute_confidence(self,
                          narrative: str,
                          extracted: ExtractedIncident) -> ExtractionConfidence:
        """
        Compute confidence scores for extraction based on AI Act ontology alignment.

        Weights are derived from the EU AI Act ontology (ai-act.eu/ai-act#):
        - hasPurpose -> expectedRiskLevel: Purpose directly determines risk classification
        - hasDeploymentContext: Context affects regulatory requirements
        - Data types: Determines if special categories (biometric, health) apply
        - Incident type: Maps to specific AI Act violations
        - Affected populations: Relevant for fundamental rights impact
        - Timeline: Supporting evidence, less critical for classification

        Weight rationale (based on ontology relationships):
        - purpose_weight = 2.0: hasPurpose -> expectedRiskLevel is the primary classifier
        - deployment_weight = 1.5: hasDeploymentContext triggers specific criteria (Art. 6)
        - data_types_weight = 1.5: Special data categories trigger stricter requirements
        - incident_weight = 1.0: Type of incident (evidence of violation)
        - affected_weight = 1.0: Fundamental rights impact assessment
        - timeline_weight = 0.5: Contextual, not determinant for classification
        """

        # === AI Act Ontology-Aligned Weights ===
        # Derived from ontology property relationships:
        # - hasPurpose -> expectedRiskLevel (direct risk determination)
        # - hasDeploymentContext -> Criterion -> assignsRiskLevel (contextual risk)
        # - processesDataTypes -> triggers BiometricData/HealthData criteria
        PURPOSE_WEIGHT = 2.0      # Primary risk classifier per Art. 6
        DEPLOYMENT_WEIGHT = 1.5   # Context-based criteria per Annex III
        DATA_TYPES_WEIGHT = 1.5   # Special categories per Art. 10
        INCIDENT_WEIGHT = 1.0     # Evidence of violation
        AFFECTED_WEIGHT = 1.0     # Fundamental rights impact
        TIMELINE_WEIGHT = 0.5     # Supporting context

        # System type confidence (proxy for deployment context)
        system_type_conf = 1.0 if extracted.system.system_type != "other" else 0.5

        # Purpose confidence - AI Act ontology terms that map to hasPurpose -> expectedRiskLevel
        # These are the Purpose subclasses that directly determine risk level
        purpose_terms = [
            "Biometric", "Emotion", "Social", "Predictive", "Credit",
            "Recognition", "Classification", "Identification", "Scoring",
            "Autonomous", "Medical", "Recruitment", "Migration", "Policing"
        ]
        purpose_conf = 0.9 if any(term in extracted.system.primary_purpose for term in purpose_terms) else 0.6
        if not extracted.system.primary_purpose or len(extracted.system.primary_purpose) < 5:
            purpose_conf = 0.3

        # Data types confidence - maps to ontology special category data
        # Higher confidence if recognized AI Act data categories are present
        special_data_types = ["BiometricData", "HealthData", "LocationData", "FinancialData"]
        has_special_data = any(dt in extracted.system.processes_data_types for dt in special_data_types)
        data_types_conf = 0.95 if has_special_data else (0.8 if len(extracted.system.processes_data_types) > 0 else 0.4)

        # Incident classification confidence - maps to AI Act violation categories
        known_types = [
            "discrimination", "bias", "safety_failure", "privacy_violation",
            "transparency_failure", "data_leakage", "adversarial_attack",
            "appropriation", "copyright"
        ]
        incident_conf = 0.9 if extracted.incident.incident_type in known_types else 0.6

        # Affected populations confidence - fundamental rights impact
        affected_conf = 0.8 if len(extracted.incident.affected_populations) > 0 else 0.5

        # Timeline confidence (supporting evidence)
        timeline_conf = 0.9 if extracted.timeline.discovery_date and len(extracted.timeline.discovery_date) >= 7 else 0.5
        if not extracted.timeline.discovery_date:
            timeline_conf = 0.3

        # Compute overall as ontology-weighted average
        scores = [
            purpose_conf * PURPOSE_WEIGHT,
            system_type_conf * DEPLOYMENT_WEIGHT,  # system_type as proxy for deployment
            data_types_conf * DATA_TYPES_WEIGHT,
            incident_conf * INCIDENT_WEIGHT,
            affected_conf * AFFECTED_WEIGHT,
            timeline_conf * TIMELINE_WEIGHT
        ]
        weights_sum = PURPOSE_WEIGHT + DEPLOYMENT_WEIGHT + DATA_TYPES_WEIGHT + INCIDENT_WEIGHT + AFFECTED_WEIGHT + TIMELINE_WEIGHT
        overall = sum(scores) / weights_sum

        # Clamp to [0, 1]
        overall = max(0.0, min(1.0, overall))

        return ExtractionConfidence(
            system_type=system_type_conf,
            purpose=purpose_conf,
            data_types=data_types_conf,
            incident_classification=incident_conf,
            affected_populations=affected_conf,
            timeline=timeline_conf,
            overall=overall
        )
