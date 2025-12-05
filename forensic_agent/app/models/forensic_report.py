"""Forensic analysis report data models"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class EUAIActRequirement(BaseModel):
    """EU AI Act requirement"""
    uri: str
    label: str
    criterion: str


class EUAIActAnalysis(BaseModel):
    """EU AI Act compliance analysis"""
    risk_level: str = Field(..., description="HighRisk|LimitedRisk|MinimalRisk")
    criteria: List[str] = Field(default_factory=list, description="Activated criteria URIs")
    requirements: List[EUAIActRequirement] = Field(default_factory=list)
    total_requirements: int


class ISOMapping(BaseModel):
    """ISO 42001 mapping"""
    iso_control: str
    iso_section: str
    description: str
    confidence: str


class ISO42001Analysis(BaseModel):
    """ISO 42001 cross-framework analysis"""
    mappings: Dict[str, ISOMapping] = Field(default_factory=dict)
    total_mapped: int
    certification_gap_detected: bool = Field(False)


class NISTMapping(BaseModel):
    """NIST AI RMF mapping"""
    nist_function: str
    nist_category: str
    description: str
    confidence: str
    applicability: str


class NISTAIRMFAnalysis(BaseModel):
    """NIST AI RMF cross-framework analysis"""
    mappings: Dict[str, NISTMapping] = Field(default_factory=dict)
    total_mapped: int
    jurisdiction_applicable: bool
    voluntary_guidance_ignored: bool = Field(False)


class CriticalGap(BaseModel):
    """Critical compliance gap"""
    requirement: str
    reason: str


class ComplianceGaps(BaseModel):
    """Compliance gap analysis"""
    total_required: int
    implemented: int
    missing: int
    compliance_ratio: float = Field(..., ge=0.0, le=1.0)
    missing_requirements: List[str] = Field(default_factory=list)
    critical_gaps: List[CriticalGap] = Field(default_factory=list)
    severity: str = Field(..., description="CRITICAL|HIGH|MEDIUM|LOW")


class ForensicAnalysisResult(BaseModel):
    """Complete forensic analysis result"""
    status: str = Field(..., description="COMPLETED|LOW_CONFIDENCE|ERROR")
    analysis_timestamp: str
    extraction: Dict  # ExtractedIncident as dict
    eu_ai_act: EUAIActAnalysis
    iso_42001: ISO42001Analysis
    nist_ai_rmf: NISTAIRMFAnalysis
    compliance_gaps: ComplianceGaps
    report: str = Field(..., description="Generated forensic report text")
    requires_expert_review: bool = Field(True)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "COMPLETED",
                "analysis_timestamp": "2025-12-05T15:30:00Z",
                "extraction": {},
                "eu_ai_act": {
                    "risk_level": "HighRisk",
                    "criteria": ["BiometricIdentificationCriterion"],
                    "requirements": [],
                    "total_requirements": 7
                },
                "iso_42001": {
                    "mappings": {},
                    "total_mapped": 5,
                    "certification_gap_detected": True
                },
                "nist_ai_rmf": {
                    "mappings": {},
                    "total_mapped": 6,
                    "jurisdiction_applicable": True,
                    "voluntary_guidance_ignored": True
                },
                "compliance_gaps": {
                    "total_required": 7,
                    "implemented": 2,
                    "missing": 5,
                    "compliance_ratio": 0.29,
                    "missing_requirements": [],
                    "critical_gaps": [],
                    "severity": "CRITICAL"
                },
                "report": "# FORENSIC COMPLIANCE AUDIT REPORT\n...",
                "requires_expert_review": True
            }
        }
