"""Incident extraction data models"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class SystemProperties(BaseModel):
    """Extracted system properties"""
    system_name: str = Field(..., description="Name of the AI system")
    system_type: str = Field(..., description="vision|nlp|tabular|multimodal|other")
    primary_purpose: str = Field(..., description="Main purpose of the system")
    processes_data_types: List[str] = Field(default_factory=list, description="BiometricData, PersonalData, etc.")
    deployment_context: List[str] = Field(default_factory=list, description="PublicSpaces, HighVolume, etc.")
    is_automated_decision: bool = Field(..., description="Whether system makes automated decisions")
    has_human_oversight: Optional[bool] = Field(None, description="Whether human oversight is present")
    model_scale: str = Field(..., description="FoundationModel|Large|Medium|Small")
    parameter_count: Optional[str] = Field(None, description="Model parameter count if known")
    training_data_description: Optional[str] = Field(None, description="Training data description if available")
    organization: Optional[str] = Field(None, description="Company/Organization name (legacy - use deployer/developer)")
    jurisdiction: str = Field(..., description="EU|US|Global|Other")
    # AIRO-aligned stakeholder fields (Art. 3.3-3.4 EU AI Act)
    deployer: Optional[str] = Field(None, description="Entity deploying the AI system (Art. 3.4 EU AI Act)")
    developer: Optional[str] = Field(None, description="Entity that developed the AI system")
    # ARTICLE 5: PROHIBITED PRACTICES (v0.37.4)
    prohibited_practices: Optional[List[str]] = Field(default_factory=list, description="Prohibited practices under Article 5 (SubliminalManipulation, VulnerabilityExploitation, SocialScoring, PredictivePolicing, RealTimeBiometricIdentification)")
    legal_exceptions: Optional[List[str]] = Field(default_factory=list, description="Legal exceptions claimed under Article 5.2 (only applicable to real-time biometric identification)")
    has_judicial_authorization: Optional[bool] = Field(None, description="Whether the system has prior judicial authorization (required for Article 5.2 exceptions)")
    # ARTICLE 6.3: PROFILING ESCALATION (v0.38.0)
    performs_profiling: Optional[bool] = Field(False, description="Whether the system performs profiling of natural persons (Art. 6.3 EU AI Act - always HighRisk if true)")
    # ARTICLE 2: SCOPE OVERRIDE DETECTION (v0.39.0)
    # These fields detect contexts that bring potentially excluded systems INTO EU AI Act scope
    scope_override_contexts: Optional[List[str]] = Field(default_factory=list, description="Scope override contexts detected: CausesRealWorldHarmContext, VictimImpactContext, AffectsFundamentalRightsContext, LegalConsequencesContext, MinorsAffectedContext")
    causes_death_or_injury: Optional[bool] = Field(False, description="Whether the incident caused death or physical injury")
    affects_minors: Optional[bool] = Field(False, description="Whether minors (under 18) were affected")
    affects_vulnerable_groups: Optional[bool] = Field(False, description="Whether vulnerable groups were affected (elderly, disabled, economically disadvantaged)")

    # Validators to handle None values from LLM extraction
    @field_validator('prohibited_practices', 'legal_exceptions', 'scope_override_contexts', mode='before')
    @classmethod
    def coerce_none_to_list(cls, v):
        """Convert None to empty list for list fields"""
        return v if v is not None else []

    @field_validator('performs_profiling', 'causes_death_or_injury', 'affects_minors', 'affects_vulnerable_groups', mode='before')
    @classmethod
    def coerce_none_to_false(cls, v):
        """Convert None to False for boolean fields"""
        return v if v is not None else False


class IncidentClassification(BaseModel):
    """Incident type and severity"""
    incident_type: str = Field(..., description="discrimination|bias|safety_failure|privacy_violation|etc.")
    severity: str = Field(..., description="critical|high|medium|low")
    affected_populations: List[str] = Field(default_factory=list, description="List of affected groups")
    affected_count: Optional[int] = Field(None, description="Number of people affected if known")
    public_disclosure: bool = Field(..., description="Whether incident was publicly disclosed")


class Timeline(BaseModel):
    """Incident timeline"""
    discovery_date: str = Field(..., description="YYYY-MM-DD or YYYY-MM or YYYY")
    impact_start_date: Optional[str] = Field(None, description="When impact began if known")
    impact_duration: Optional[str] = Field(None, description="Duration of impact if known")
    public_disclosure_date: Optional[str] = Field(None, description="When publicly disclosed")
    resolution_date: Optional[str] = Field(None, description="When resolved if applicable")


class OrganizationResponse(BaseModel):
    """How organization responded to incident"""
    acknowledged: bool = Field(..., description="Whether organization acknowledged incident")
    actions_taken: List[str] = Field(default_factory=list, description="List of actions taken")
    systemic_improvements: Optional[List[str]] = Field(None, description="Systemic improvements made")
    public_apology: bool = Field(False, description="Whether public apology was issued")
    compensation_provided: bool = Field(False, description="Whether compensation was provided")
    regulatory_action: Optional[str] = Field(None, description="Regulatory action taken if any")


class ExtractionConfidence(BaseModel):
    """Confidence scores for validation"""
    system_type: float = Field(..., ge=0.0, le=1.0, description="Confidence in system type identification")
    purpose: float = Field(..., ge=0.0, le=1.0, description="Confidence in purpose identification")
    data_types: float = Field(..., ge=0.0, le=1.0, description="Confidence in data types identification")
    incident_classification: float = Field(..., ge=0.0, le=1.0, description="Confidence in incident classification")
    affected_populations: float = Field(..., ge=0.0, le=1.0, description="Confidence in affected populations")
    timeline: float = Field(..., ge=0.0, le=1.0, description="Confidence in timeline accuracy")
    overall: float = Field(..., ge=0.0, le=1.0, description="Overall extraction confidence")


class ExtractedIncident(BaseModel):
    """Complete extracted incident data"""
    system: SystemProperties
    incident: IncidentClassification
    timeline: Timeline
    response: OrganizationResponse
    confidence: ExtractionConfidence
    raw_narrative: str = Field(..., description="Original incident narrative")
    extraction_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "system": {
                    "system_name": "Facebook DeepFace",
                    "system_type": "vision",
                    "primary_purpose": "BiometricIdentification",
                    "processes_data_types": ["BiometricData", "PersonalData"],
                    "deployment_context": ["PublicSpaces", "HighVolume"],
                    "is_automated_decision": True,
                    "has_human_oversight": False,
                    "model_scale": "Large",
                    "organization": "Facebook (Meta)",
                    "jurisdiction": "Global",
                    "deployer": "Facebook (Meta)",
                    "developer": "Facebook AI Research",
                    "prohibited_practices": [],
                    "legal_exceptions": [],
                    "has_judicial_authorization": None,
                    "performs_profiling": True
                },
                "incident": {
                    "incident_type": "discrimination",
                    "severity": "critical",
                    "affected_populations": ["Black users", "Minorities"],
                    "public_disclosure": True
                },
                "timeline": {
                    "discovery_date": "2015",
                    "resolution_date": "2015-2016"
                },
                "response": {
                    "acknowledged": True,
                    "actions_taken": ["Removed alt text generation feature"],
                    "public_apology": True,
                    "compensation_provided": False
                },
                "confidence": {
                    "system_type": 0.95,
                    "purpose": 0.92,
                    "data_types": 0.88,
                    "incident_classification": 0.96,
                    "affected_populations": 0.94,
                    "timeline": 0.80,
                    "overall": 0.91
                },
                "raw_narrative": "Facebook's DeepFace system...",
                "extraction_timestamp": "2025-12-05T15:30:00Z"
            }
        }
