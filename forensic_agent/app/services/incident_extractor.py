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
    "primary_purpose": "Main purpose of the system (use EU AI Act ontology terms when possible: BiometricIdentification, EmotionRecognition, etc.)",
    "processes_data_types": ["BiometricData", "PersonalData", "HealthData", "LocationData", "FinancialData", etc.],
    "deployment_context": ["PublicSpaces", "HighVolume", "RealTime", "CriticalInfrastructure", "EducationContext", "EmploymentContext", "LawEnforcementContext", "HealthcareContext", "MigrationContext", etc.],
    "is_automated_decision": true/false,
    "has_human_oversight": true/false/null,
    "model_scale": "FoundationModel|Large|Medium|Small",
    "parameter_count": "if mentioned, otherwise null",
    "training_data_description": "if mentioned, otherwise null",
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
- Extract ONLY information explicitly stated in the narrative
- Use null for unknown information - DO NOT guess or infer
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
- For primary_purpose, prefer EU AI Act ontology terms:
  * BiometricIdentification, EmotionRecognition, SocialScoring,
    PredictivePolicing, CreditScoring, etc.
- For incident_type:
  * discrimination: unfair treatment of protected groups
  * bias: algorithmic bias leading to unfair outcomes
  * safety_failure: system caused physical harm or danger
  * privacy_violation: unauthorized data collection/use
  * transparency_failure: lack of disclosure about AI use
  * data_leakage: sensitive data exposed
- For severity:
  * critical: widespread harm, fundamental rights violated
  * high: significant harm to many people
  * medium: moderate harm or limited scope
  * low: minimal harm or quickly resolved

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

    def _compute_confidence(self,
                          narrative: str,
                          extracted: ExtractedIncident) -> ExtractionConfidence:
        """
        Compute confidence scores for extraction based on heuristics

        This is a simple heuristic-based confidence scoring.
        Can be enhanced with LLM self-assessment in future iterations.
        """

        # System type confidence
        system_type_conf = 1.0 if extracted.system.system_type != "other" else 0.5

        # Purpose confidence (higher if matches known ontology terms)
        purpose_terms = [
            "Biometric", "Emotion", "Social", "Predictive", "Credit",
            "Recognition", "Classification", "Identification"
        ]
        purpose_conf = 0.9 if any(term in extracted.system.primary_purpose for term in purpose_terms) else 0.6
        if not extracted.system.primary_purpose or len(extracted.system.primary_purpose) < 5:
            purpose_conf = 0.3

        # Data types confidence
        data_types_conf = 0.9 if len(extracted.system.processes_data_types) > 0 else 0.4

        # Incident classification confidence
        known_types = [
            "discrimination", "bias", "safety_failure", "privacy_violation",
            "transparency_failure", "data_leakage", "adversarial_attack"
        ]
        incident_conf = 0.9 if extracted.incident.incident_type in known_types else 0.6

        # Affected populations confidence
        affected_conf = 0.8 if len(extracted.incident.affected_populations) > 0 else 0.5

        # Timeline confidence (higher if date is specific)
        timeline_conf = 0.9 if extracted.timeline.discovery_date and len(extracted.timeline.discovery_date) >= 7 else 0.5
        if not extracted.timeline.discovery_date:
            timeline_conf = 0.3

        # Compute overall as weighted average (timeline less important)
        scores = [
            system_type_conf * 1.2,  # More important
            purpose_conf * 1.2,      # More important
            data_types_conf * 1.0,
            incident_conf * 1.2,     # More important
            affected_conf * 0.8,
            timeline_conf * 0.6      # Less important
        ]
        overall = sum(scores) / sum([1.2, 1.2, 1.0, 1.2, 0.8, 0.6])

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
