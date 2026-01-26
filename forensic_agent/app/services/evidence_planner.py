"""
Evidence Planner Service

Generates structured evidence plans based on compliance gaps identified by the Forensic Agent.
Uses DPV (Data Privacy Vocabulary) mappings to determine appropriate technical and
organizational measures for each requirement.

Based on:
- W3C Data Privacy Vocabulary (DPV) 2.2
- EU AI Act requirements (Regulation 2024/1689)
- European Legislation Identifier (ELI) for EUR-Lex interoperability
- SERAMIS ontology mappings
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class EvidencePriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EvidenceFrequency(str, Enum):
    ONCE = "ONCE"
    CONTINUOUS = "CONTINUOUS"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"


class EvidenceType(str, Enum):
    POLICY = "PolicyEvidence"
    TECHNICAL = "TechnicalEvidence"
    AUDIT = "AuditEvidence"
    TRAINING = "TrainingEvidence"
    ASSESSMENT = "AssessmentEvidence"
    CONTRACTUAL = "ContractualEvidence"


class ResponsibleRole(str, Enum):
    DEPLOYER = "DEPLOYER"
    PROVIDER = "PROVIDER"
    DPO = "DPO"
    LEGAL = "LEGAL"
    TECHNICAL = "TECHNICAL"
    COMPLIANCE = "COMPLIANCE"


@dataclass
class EvidenceItem:
    """Single piece of evidence required for compliance"""
    id: str
    name: str
    description: str
    evidence_type: EvidenceType
    priority: EvidencePriority
    frequency: EvidenceFrequency
    responsible_role: ResponsibleRole
    dpv_measure: Optional[str] = None
    templates: List[str] = field(default_factory=list)
    guidance: Optional[str] = None


@dataclass
class RequirementEvidencePlan:
    """Evidence plan for a single requirement gap"""
    requirement_uri: str
    requirement_label: str
    priority: EvidencePriority
    dpv_measures: List[str]
    evidence_items: List[EvidenceItem]
    deadline_recommendation: str
    responsible_roles: List[ResponsibleRole]
    article_reference: Optional[str] = None
    eli_uri: Optional[str] = None  # European Legislation Identifier URI for EUR-Lex
    estimated_effort: Optional[str] = None


@dataclass
class EvidencePlan:
    """Complete evidence generation plan for all gaps"""
    plan_id: str
    generated_at: str
    system_name: str
    risk_level: str
    total_gaps: int
    requirement_plans: List[RequirementEvidencePlan]
    summary: Dict
    recommendations: List[str]


# ELI Base URI for EU AI Act (Regulation 2024/1689)
ELI_BASE = "http://data.europa.eu/eli/reg/2024/1689"

# Evidence catalog mapping requirements to evidence items
EVIDENCE_CATALOG = {
    "HumanOversightRequirement": {
        "article": "Article 14",
        "eli_uri": f"{ELI_BASE}/art_14/oj",
        "dpv_measures": ["dpv:HumanInvolvement", "dpv:HumanInvolvementForOversight"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.DEPLOYER, ResponsibleRole.COMPLIANCE],
        "evidence": [
            EvidenceItem(
                id="HO-POL-001",
                name="Human Oversight Policy",
                description="Documented policy defining human oversight mechanisms, escalation procedures, and operator responsibilities for AI system decisions",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE,
                dpv_measure="dpv:HumanInvolvement",
                templates=["human_oversight_policy_template.docx"],
                guidance="Must include: oversight triggers, escalation matrix, operator authority levels, documentation requirements"
            ),
            EvidenceItem(
                id="HO-LOG-001",
                name="Override Decision Logs",
                description="Logs of human override decisions including timestamps, operator ID, decision context, and justification",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.CONTINUOUS,
                responsible_role=ResponsibleRole.TECHNICAL,
                dpv_measure="dpv:RecordsOfActivities",
                guidance="Logs must be tamper-proof and retained per Art. 12 requirements"
            ),
            EvidenceItem(
                id="HO-TRN-001",
                name="Operator Training Records",
                description="Training records for AI system operators including competency assessments and certification",
                evidence_type=EvidenceType.TRAINING,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DEPLOYER,
                templates=["operator_training_log.xlsx", "competency_assessment.docx"],
                guidance="Include: training dates, topics covered, assessment results, refresher schedule"
            ),
        ]
    },

    "FundamentalRightsAssessmentRequirement": {
        "article": "Article 27",
        "eli_uri": f"{ELI_BASE}/art_27/oj",
        "dpv_measures": ["dpv:ImpactAssessment", "dpv:FRIA"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.DEPLOYER, ResponsibleRole.DPO, ResponsibleRole.LEGAL],
        "evidence": [
            EvidenceItem(
                id="FRIA-ASS-001",
                name="FRIA Report",
                description="Fundamental Rights Impact Assessment documenting potential impacts on affected persons' rights",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                dpv_measure="dpv:FRIA",
                templates=["fria_template.docx"],
                guidance="Must cover: affected categories, specific risks per category, period/frequency of use, human oversight measures, mitigation measures"
            ),
            EvidenceItem(
                id="FRIA-ASS-002",
                name="Affected Persons Analysis",
                description="Detailed analysis of categories of persons affected and specific risks to each group",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                guidance="Include vulnerable groups analysis per Art. 27(1)(c)"
            ),
            EvidenceItem(
                id="FRIA-POL-001",
                name="Mitigation Plan",
                description="Documented measures to mitigate identified fundamental rights risks",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE,
                templates=["risk_mitigation_plan.docx"]
            ),
        ]
    },

    "TransparencyRequirement": {
        "article": "Article 13",
        "eli_uri": f"{ELI_BASE}/art_13/oj",
        "dpv_measures": ["dpv:Transparency", "dpv:PrivacyNotice"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.DEPLOYER],
        "evidence": [
            EvidenceItem(
                id="TR-TEC-001",
                name="User Notification Implementation",
                description="Evidence that users are clearly informed they are interacting with an AI system",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.TECHNICAL,
                dpv_measure="dpv:Transparency",
                guidance="Screenshots, UI mockups, or code showing AI disclosure"
            ),
            EvidenceItem(
                id="TR-TEC-002",
                name="System Description Document",
                description="Plain-language description of system capabilities, limitations, and intended use",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.PROVIDER,
                templates=["system_description_template.docx"]
            ),
            EvidenceItem(
                id="TR-POL-001",
                name="AI Disclosure Policy",
                description="Policy and procedures for disclosing AI system use to affected persons",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.COMPLIANCE
            ),
        ]
    },

    "DocumentationRequirement": {
        "article": "Article 11 + Annex IV",
        "eli_uri": f"{ELI_BASE}/art_11/oj",
        "dpv_measures": ["dpv:RecordsOfActivities", "dpv:Documentation"],
        "deadline": "Before CE marking",
        "responsible": [ResponsibleRole.PROVIDER],
        "evidence": [
            EvidenceItem(
                id="DOC-TEC-001",
                name="Technical Documentation (Annex IV)",
                description="Complete technical documentation per Annex IV including system design, algorithms, data, and validation",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.PROVIDER,
                templates=["annex_iv_technical_documentation.docx"],
                guidance="Must include all 8 sections of Annex IV"
            ),
            EvidenceItem(
                id="DOC-TEC-002",
                name="Model Card",
                description="Model card documenting capabilities, limitations, intended use, and performance metrics",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.PROVIDER,
                templates=["model_card_template.md"]
            ),
            EvidenceItem(
                id="DOC-TEC-003",
                name="Version Control Records",
                description="Version control showing changes to AI system over time with change justifications",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.MEDIUM,
                frequency=EvidenceFrequency.CONTINUOUS,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
        ]
    },

    "DataGovernanceRequirement": {
        "article": "Article 10",
        "eli_uri": f"{ELI_BASE}/art_10/oj",
        "dpv_measures": ["dpv:DataGovernancePolicies", "dpv:DataQualityAssessment"],
        "deadline": "Before training/deployment",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.DPO],
        "evidence": [
            EvidenceItem(
                id="DG-POL-001",
                name="Data Quality Policy",
                description="Policy defining data quality standards, validation procedures, and bias monitoring",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                templates=["data_quality_policy.docx"]
            ),
            EvidenceItem(
                id="DG-TEC-001",
                name="Training Data Documentation",
                description="Documentation of training data sources, characteristics, preprocessing, and known limitations",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.PROVIDER,
                templates=["dataset_documentation.md"]
            ),
            EvidenceItem(
                id="DG-TEC-002",
                name="Data Provenance Records",
                description="Records of data origin, transformations, and chain of custody",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.MEDIUM,
                frequency=EvidenceFrequency.CONTINUOUS,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
        ]
    },

    "RiskManagementRequirement": {
        "article": "Article 9",
        "eli_uri": f"{ELI_BASE}/art_9/oj",
        "dpv_measures": ["dpv:RiskManagementPlan", "dpv:RiskAssessment"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.COMPLIANCE],
        "evidence": [
            EvidenceItem(
                id="RM-POL-001",
                name="Risk Management System Documentation",
                description="Documented risk management system per Art. 9 including methodology, governance, and lifecycle coverage",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE,
                templates=["risk_management_system.docx"],
                guidance="Must be iterative and cover entire AI system lifecycle"
            ),
            EvidenceItem(
                id="RM-ASS-001",
                name="Risk Register",
                description="Register of identified risks, their assessment scores, and treatment decisions",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.QUARTERLY,
                responsible_role=ResponsibleRole.COMPLIANCE,
                templates=["risk_register.xlsx"]
            ),
            EvidenceItem(
                id="RM-AUD-001",
                name="Risk Monitoring Records",
                description="Records of ongoing risk monitoring activities and periodic reassessments",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.CONTINUOUS,
                responsible_role=ResponsibleRole.COMPLIANCE
            ),
        ]
    },

    "NonDiscriminationRequirement": {
        "article": "Article 10(2)(f)",
        "eli_uri": f"{ELI_BASE}/art_10/par_2/pnt_f/oj",
        "dpv_measures": ["dpv:BiasAssessment", "dpv:FairnessAssessment"],
        "deadline": "Before deployment + ongoing",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.DPO],
        "evidence": [
            EvidenceItem(
                id="ND-AUD-001",
                name="Bias Audit Report",
                description="Independent bias audit analyzing system outputs across protected characteristics",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                dpv_measure="dpv:BiasAssessment",
                templates=["bias_audit_report.docx"],
                guidance="Must cover: gender, ethnicity, age, disability, and other protected characteristics"
            ),
            EvidenceItem(
                id="ND-TEC-001",
                name="Fairness Metrics Report",
                description="Quantitative fairness metrics with defined thresholds and monitoring procedures",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.QUARTERLY,
                responsible_role=ResponsibleRole.TECHNICAL,
                guidance="Include: demographic parity, equalized odds, calibration metrics"
            ),
            EvidenceItem(
                id="ND-ASS-001",
                name="Protected Group Analysis",
                description="Analysis of system performance disaggregated by protected characteristics",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO
            ),
        ]
    },

    "TraceabilityRequirement": {
        "article": "Article 12",
        "eli_uri": f"{ELI_BASE}/art_12/oj",
        "dpv_measures": ["dpv:RecordsOfActivities", "dpv:AuditLogging"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.TECHNICAL],
        "evidence": [
            EvidenceItem(
                id="TC-TEC-001",
                name="Audit Log System",
                description="Automatic logging of system events, inputs, outputs, and decisions",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.CONTINUOUS,
                responsible_role=ResponsibleRole.TECHNICAL,
                dpv_measure="dpv:AuditLogging",
                guidance="Logs must enable monitoring per Art. 72(1)"
            ),
            EvidenceItem(
                id="TC-TEC-002",
                name="Decision Trace Capability",
                description="Technical capability to trace individual decisions back to inputs and model state",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.CONTINUOUS,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
            EvidenceItem(
                id="TC-POL-001",
                name="Log Retention Policy",
                description="Policy defining log retention periods, secure storage, and access controls",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.MEDIUM,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.COMPLIANCE
            ),
        ]
    },

    "AccuracyEvaluationRequirement": {
        "article": "Article 15",
        "eli_uri": f"{ELI_BASE}/art_15/oj",
        "dpv_measures": ["dpv:ReviewProcedure", "dpv:PerformanceAssessment"],
        "deadline": "Before deployment + ongoing",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.TECHNICAL],
        "evidence": [
            EvidenceItem(
                id="AC-AUD-001",
                name="Accuracy Test Report",
                description="Test reports showing accuracy metrics on representative validation datasets",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.QUARTERLY,
                responsible_role=ResponsibleRole.TECHNICAL,
                templates=["accuracy_test_report.docx"]
            ),
            EvidenceItem(
                id="AC-TEC-001",
                name="Validation Dataset Documentation",
                description="Documentation of validation datasets including representativeness analysis",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.MEDIUM,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.PROVIDER
            ),
            EvidenceItem(
                id="AC-TEC-002",
                name="Performance Baseline",
                description="Established performance baseline with acceptable deviation thresholds",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.PROVIDER
            ),
        ]
    },

    "AccuracyRequirement": {
        "article": "Article 15",
        "eli_uri": f"{ELI_BASE}/art_15/oj",
        "dpv_measures": ["dpv:AccuracyAssessment", "dpv:QualityAssurance"],
        "deadline": "Before deployment + ongoing",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.TECHNICAL],
        "evidence": [
            EvidenceItem(
                id="ACR-TEC-001",
                name="Accuracy Specification Document",
                description="Document specifying accuracy requirements, metrics, and acceptable thresholds for the AI system",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.PROVIDER,
                guidance="Must define precision, recall, F1, or domain-specific accuracy metrics"
            ),
            EvidenceItem(
                id="ACR-AUD-001",
                name="Accuracy Monitoring Reports",
                description="Periodic reports demonstrating ongoing accuracy performance in production",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.QUARTERLY,
                responsible_role=ResponsibleRole.TECHNICAL,
                templates=["accuracy_monitoring_report.docx"]
            ),
            EvidenceItem(
                id="ACR-POL-001",
                name="Accuracy Degradation Response Plan",
                description="Procedures for detecting and responding to accuracy degradation over time",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.MEDIUM,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE
            ),
        ]
    },

    "BiasDetectionRequirement": {
        "article": "Article 10(2)(f)",
        "eli_uri": f"{ELI_BASE}/art_10/par_2/pnt_f/oj",
        "dpv_measures": ["dpv:BiasAssessment", "dpv:BiasMonitoring"],
        "deadline": "Before deployment + ongoing",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.DPO],
        "evidence": [
            EvidenceItem(
                id="BD-TEC-001",
                name="Bias Detection Methodology",
                description="Documented methodology for detecting bias in training data and model outputs",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.PROVIDER,
                dpv_measure="dpv:BiasAssessment",
                guidance="Must cover statistical methods, protected attributes, and detection thresholds"
            ),
            EvidenceItem(
                id="BD-AUD-001",
                name="Bias Detection Reports",
                description="Regular reports from bias detection systems showing analysis results",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.QUARTERLY,
                responsible_role=ResponsibleRole.DPO,
                templates=["bias_detection_report.docx"]
            ),
            EvidenceItem(
                id="BD-TEC-002",
                name="Bias Monitoring Dashboard",
                description="Evidence of continuous bias monitoring implementation with alerting",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.CONTINUOUS,
                responsible_role=ResponsibleRole.TECHNICAL,
                dpv_measure="dpv:BiasMonitoring"
            ),
        ]
    },

    "FairnessRequirement": {
        "article": "Article 10(2)(f) + Recital 47",
        "eli_uri": f"{ELI_BASE}/art_10/par_2/pnt_f/oj",
        "dpv_measures": ["dpv:FairnessAssessment", "dpv:EqualTreatment"],
        "deadline": "Before deployment + ongoing",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.DPO, ResponsibleRole.LEGAL],
        "evidence": [
            EvidenceItem(
                id="FR-ASS-001",
                name="Fairness Assessment Report",
                description="Comprehensive assessment of fairness across different demographic groups and use cases",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                dpv_measure="dpv:FairnessAssessment",
                guidance="Must include group fairness metrics: demographic parity, equalized odds, predictive parity"
            ),
            EvidenceItem(
                id="FR-POL-001",
                name="Fairness Policy",
                description="Policy defining fairness principles, criteria, and remediation procedures",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE,
                templates=["fairness_policy.docx"]
            ),
            EvidenceItem(
                id="FR-TEC-001",
                name="Fairness Metrics Implementation",
                description="Technical documentation of fairness metrics implemented in the system",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.TECHNICAL,
                guidance="Include: chosen metrics, thresholds, trade-off decisions between different fairness criteria"
            ),
        ]
    },

    "RobustnessRequirement": {
        "article": "Article 15",
        "dpv_measures": ["dpv:SecurityAssessment", "dpv:RobustnessTesting"],
        "deadline": "Before deployment + ongoing",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.TECHNICAL],
        "evidence": [
            EvidenceItem(
                id="RB-AUD-001",
                name="Robustness Test Report",
                description="Test reports demonstrating system behavior under adverse conditions",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
            EvidenceItem(
                id="RB-AUD-002",
                name="Adversarial Testing Results",
                description="Results of adversarial testing and red-team exercises",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.TECHNICAL,
                guidance="Include: evasion attacks, poisoning attempts, model extraction tests"
            ),
            EvidenceItem(
                id="RB-TEC-001",
                name="Failsafe Mechanism Documentation",
                description="Documentation of failsafe mechanisms and graceful degradation capabilities",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.MEDIUM,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
        ]
    },

    "SecurityRequirement": {
        "article": "Article 15",
        "dpv_measures": ["dpv:TechnicalSecurityMeasure", "dpv:SecurityAssessment"],
        "deadline": "Before deployment + ongoing",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.TECHNICAL],
        "evidence": [
            EvidenceItem(
                id="SC-AUD-001",
                name="Security Audit Report",
                description="Security audit covering infrastructure, APIs, data protection, and access controls",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
            EvidenceItem(
                id="SC-AUD-002",
                name="Penetration Test Report",
                description="Penetration testing results for AI system and supporting infrastructure",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
            EvidenceItem(
                id="SC-POL-001",
                name="Security Policy",
                description="Security policy covering access control, encryption, and incident response",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE
            ),
        ]
    },

    "GPAITransparencyRequirement": {
        "article": "Article 52",
        "dpv_measures": ["dpv:Transparency", "dpv:Documentation"],
        "deadline": "Before market placement",
        "responsible": [ResponsibleRole.PROVIDER],
        "evidence": [
            EvidenceItem(
                id="GPAI-TEC-001",
                name="GPAI Model Card",
                description="Model card for GPAI system per Art. 52 including capabilities, limitations, and risks",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.PROVIDER,
                templates=["gpai_model_card.md"]
            ),
            EvidenceItem(
                id="GPAI-TEC-002",
                name="Training Data Summary",
                description="Summary of training data sources, types of content, and general characteristics",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.PROVIDER
            ),
            EvidenceItem(
                id="GPAI-POL-001",
                name="Copyright Compliance Policy",
                description="Policy and procedures for copyright compliance in training data",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.LEGAL
            ),
        ]
    },

    "ProtectionOfMinorsRequirement": {
        "article": "Recital 28 + Art. 27",
        "dpv_measures": ["dpv:ChildrenDataProtection", "dpv:AgeVerification"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.DEPLOYER, ResponsibleRole.DPO],
        "evidence": [
            EvidenceItem(
                id="PM-TEC-001",
                name="Age Verification Mechanism",
                description="Implementation of age verification where system may affect minors",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.TECHNICAL,
                dpv_measure="dpv:AgeVerification"
            ),
            EvidenceItem(
                id="PM-ASS-001",
                name="Minors Impact Assessment",
                description="Specific assessment of impacts on children and minors",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO
            ),
            EvidenceItem(
                id="PM-CON-001",
                name="Parental Consent Records",
                description="Parental consent mechanisms and records where applicable",
                evidence_type=EvidenceType.CONTRACTUAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.CONTINUOUS,
                responsible_role=ResponsibleRole.LEGAL
            ),
        ]
    },

    "SystemSafetyRequirement": {
        "article": "Article 15",
        "dpv_measures": ["dpv:SafetyAssessment", "dpv:RiskMitigation"],
        "deadline": "Before deployment + ongoing",
        "responsible": [ResponsibleRole.PROVIDER, ResponsibleRole.TECHNICAL],
        "evidence": [
            EvidenceItem(
                id="SS-ASS-001",
                name="Safety Assessment Report",
                description="Comprehensive safety assessment covering foreseeable risks and mitigation",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
            EvidenceItem(
                id="SS-TEC-001",
                name="Safety Mechanisms Documentation",
                description="Documentation of safety mechanisms, kill switches, and emergency procedures",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.TECHNICAL
            ),
            EvidenceItem(
                id="SS-POL-001",
                name="Incident Response Plan",
                description="Plan for responding to safety incidents including notification procedures",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE
            ),
        ]
    },

    # ============================================================================
    # SCOPE OVERRIDE ASSESSMENT (v0.39.0) - Article 2 Applicability
    # ============================================================================
    "ScopeOverrideAssessment": {
        "article": "Article 2",
        "eli_uri": f"{ELI_BASE}/art_2/oj",
        "dpv_measures": ["dpv:ImpactAssessment", "dpv:RightsImpactAssessment"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.LEGAL, ResponsibleRole.COMPLIANCE, ResponsibleRole.DPO],
        "evidence": [
            EvidenceItem(
                id="SO-ASS-001",
                name="Scope Applicability Assessment",
                description="Assessment documenting why a system with potentially excluded purpose falls within EU AI Act scope due to override contexts (fundamental rights impact, legal consequences, victim harm, etc.)",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.LEGAL,
                dpv_measure="dpv:ImpactAssessment",
                templates=["scope_override_assessment.docx"],
                guidance="Must document: (1) The excluded purpose category (Art. 2 exclusion), (2) The override context triggering applicability, (3) Specific impacts on natural persons, (4) Legal basis for scope inclusion"
            ),
            EvidenceItem(
                id="SO-ASS-002",
                name="Fundamental Rights Impact Documentation",
                description="Documentation of how the system affects fundamental rights of natural persons, triggering AI Act applicability despite potentially excluded purpose",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                dpv_measure="dpv:RightsImpactAssessment",
                guidance="Required when system purpose falls under Art. 2 exclusion but deployment context affects fundamental rights"
            ),
            EvidenceItem(
                id="SO-POL-001",
                name="Scope Determination Policy",
                description="Policy for determining EU AI Act applicability for systems with mixed-use purposes or edge-case deployment contexts",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE,
                templates=["scope_determination_policy.docx"]
            ),
        ]
    },

    # ============================================================================
    # FRIA REQUIREMENT (v0.39.0) - Article 27 Fundamental Rights Impact Assessment
    # ============================================================================
    "FRIARequirement": {
        "article": "Article 27",
        "eli_uri": f"{ELI_BASE}/art_27/oj",
        "dpv_measures": ["dpv:FRIA", "dpv:ImpactAssessment", "dpv:RightsImpactAssessment"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.DEPLOYER, ResponsibleRole.DPO, ResponsibleRole.LEGAL],
        "evidence": [
            EvidenceItem(
                id="FRIA-REQ-001",
                name="FRIA Trigger Assessment",
                description="Assessment documenting the trigger conditions that require a Fundamental Rights Impact Assessment per Article 27",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.LEGAL,
                dpv_measure="dpv:ImpactAssessment",
                templates=["fria_trigger_assessment.docx"],
                guidance="Document which override context triggered FRIA requirement: LegalConsequencesContext, VictimImpactContext, AffectsFundamentalRightsContext, BiometricProcessingContext"
            ),
            EvidenceItem(
                id="FRIA-REQ-002",
                name="Complete FRIA Report per Art. 27",
                description="Full Fundamental Rights Impact Assessment following Art. 27 structure: affected persons, specific risks, frequency of use, human oversight, mitigation measures",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                dpv_measure="dpv:FRIA",
                templates=["fria_full_report.docx", "fria_annex_template.xlsx"],
                guidance="Art. 27(1) requires: (a) deployer's processes, (b) period/frequency of use, (c) categories of affected persons, (d) specific risks per category, (e) human oversight measures, (f) measures for identified risks. Per Art. 27(2), consult workers' representatives where applicable."
            ),
            EvidenceItem(
                id="FRIA-REQ-003",
                name="FRIA Notification to Authority",
                description="Evidence of notification to relevant market surveillance authority per Art. 27(4) requirements",
                evidence_type=EvidenceType.AUDIT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.COMPLIANCE,
                guidance="Art. 27(4): Deployers must notify market surveillance authority of FRIA results. Retain notification acknowledgment."
            ),
            EvidenceItem(
                id="FRIA-REQ-004",
                name="FRIA Mitigation Plan",
                description="Documented measures to mitigate identified fundamental rights risks from the FRIA",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE,
                templates=["fria_mitigation_plan.docx"],
                guidance="Link each identified risk to specific mitigation measure with timeline and responsible party"
            ),
        ]
    },

    # ============================================================================
    # VICTIM IMPACT ASSESSMENT (v0.39.0) - For systems affecting victims
    # ============================================================================
    "VictimImpactAssessment": {
        "article": "Article 2 + Article 27",
        "eli_uri": f"{ELI_BASE}/art_27/oj",
        "dpv_measures": ["dpv:ImpactAssessment", "dpv:VulnerableDataSubject"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.DPO, ResponsibleRole.LEGAL],
        "evidence": [
            EvidenceItem(
                id="VI-ASS-001",
                name="Victim Category Identification",
                description="Documentation identifying categories of victims potentially affected by the AI system and specific vulnerabilities",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                dpv_measure="dpv:VulnerableDataSubject",
                templates=["victim_category_assessment.docx"],
                guidance="Cover: crime victims, accident victims, disaster victims, domestic violence survivors, trafficking victims. Reference DPV VulnerableDataSubject taxonomy."
            ),
            EvidenceItem(
                id="VI-ASS-002",
                name="Secondary Harm Prevention Assessment",
                description="Assessment of potential secondary harms to victims from AI system use and prevention measures",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.DPO,
                guidance="Assess: re-traumatization, privacy violations, dignity impacts, access barriers for vulnerable persons"
            ),
            EvidenceItem(
                id="VI-POL-001",
                name="Victim Protection Policy",
                description="Policy ensuring protection of victim rights and dignity in AI system deployment",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.COMPLIANCE,
                templates=["victim_protection_policy.docx"]
            ),
        ]
    },

    # ============================================================================
    # LEGAL CONSEQUENCES ASSESSMENT (v0.39.0) - For systems producing legal effects
    # ============================================================================
    "LegalConsequencesAssessment": {
        "article": "Article 2 + Article 6 Annex III",
        "eli_uri": f"{ELI_BASE}/art_6/oj",
        "dpv_measures": ["dpv:LegalEffect", "dpv:AutomatedDecisionMaking"],
        "deadline": "Before deployment",
        "responsible": [ResponsibleRole.LEGAL, ResponsibleRole.COMPLIANCE],
        "evidence": [
            EvidenceItem(
                id="LC-ASS-001",
                name="Legal Effects Mapping",
                description="Comprehensive mapping of legal effects produced by the AI system on natural persons",
                evidence_type=EvidenceType.ASSESSMENT,
                priority=EvidencePriority.CRITICAL,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.LEGAL,
                dpv_measure="dpv:LegalEffect",
                templates=["legal_effects_mapping.docx"],
                guidance="Document all legal consequences: arrest decisions, court proceedings, benefit denials, contract terminations, rights restrictions"
            ),
            EvidenceItem(
                id="LC-TEC-001",
                name="Automated Decision Documentation",
                description="Technical documentation of automated decision-making processes with legal consequences",
                evidence_type=EvidenceType.TECHNICAL,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ANNUALLY,
                responsible_role=ResponsibleRole.TECHNICAL,
                dpv_measure="dpv:AutomatedDecisionMaking",
                guidance="Include decision logic, thresholds, factors considered, and explainability mechanisms"
            ),
            EvidenceItem(
                id="LC-POL-001",
                name="Legal Challenge Process",
                description="Documented process for affected persons to challenge AI-assisted legal decisions",
                evidence_type=EvidenceType.POLICY,
                priority=EvidencePriority.HIGH,
                frequency=EvidenceFrequency.ONCE,
                responsible_role=ResponsibleRole.LEGAL,
                templates=["legal_challenge_process.docx"],
                guidance="Must include: appeal mechanisms, human review rights, timeline for decisions"
            ),
        ]
    },
}


class EvidencePlannerService:
    """
    Generates evidence plans based on compliance gaps.

    Takes the output from the Forensic Agent (compliance gaps) and generates
    a structured plan for evidence generation using DPV mappings.
    """

    def __init__(self):
        self.evidence_catalog = EVIDENCE_CATALOG

    def generate_plan(
        self,
        system_name: str,
        risk_level: str,
        missing_requirements: List[str],
        critical_gaps: List[Dict],
        jurisdiction: str = "EU"
    ) -> EvidencePlan:
        """
        Generate a complete evidence plan for identified gaps.

        Args:
            system_name: Name of the AI system
            risk_level: EU AI Act risk level (HighRisk, LimitedRisk, etc.)
            missing_requirements: List of missing requirement URIs
            critical_gaps: List of critical gap details
            jurisdiction: Jurisdiction context (EU, US, Global)

        Returns:
            Complete evidence plan with all requirement plans
        """
        plan_id = f"EVP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        requirement_plans = []

        # Extract requirement names from URIs
        critical_req_names = {
            gap.get("requirement", "").split("#")[-1]
            for gap in critical_gaps
        }

        for req_uri in missing_requirements:
            # Handle multiple formats:
            # - Full URI: http://ai-act.eu/ai#DataGovernanceRequirement
            # - Prefixed: ai:DataGovernanceRequirement
            # - Plain name: DataGovernanceRequirement
            if "#" in req_uri:
                req_name = req_uri.split("#")[-1]
            elif ":" in req_uri:
                req_name = req_uri.split(":")[-1]
            else:
                req_name = req_uri

            # Check if we have evidence mapping for this requirement
            if req_name in self.evidence_catalog:
                catalog_entry = self.evidence_catalog[req_name]

                # Determine priority based on whether it's a critical gap
                priority = (
                    EvidencePriority.CRITICAL
                    if req_name in critical_req_names
                    else EvidencePriority.HIGH
                )

                req_plan = RequirementEvidencePlan(
                    requirement_uri=req_uri,
                    requirement_label=self._format_label(req_name),
                    priority=priority,
                    dpv_measures=catalog_entry["dpv_measures"],
                    evidence_items=catalog_entry["evidence"],
                    deadline_recommendation=catalog_entry["deadline"],
                    responsible_roles=catalog_entry["responsible"],
                    article_reference=catalog_entry.get("article"),
                    eli_uri=catalog_entry.get("eli_uri"),
                    estimated_effort=self._estimate_effort(catalog_entry["evidence"])
                )
                requirement_plans.append(req_plan)

        # Sort by priority
        priority_order = {
            EvidencePriority.CRITICAL: 0,
            EvidencePriority.HIGH: 1,
            EvidencePriority.MEDIUM: 2,
            EvidencePriority.LOW: 3
        }
        requirement_plans.sort(key=lambda x: priority_order[x.priority])

        # Generate summary
        summary = self._generate_summary(requirement_plans)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, requirement_plans, critical_gaps
        )

        return EvidencePlan(
            plan_id=plan_id,
            generated_at=datetime.utcnow().isoformat(),
            system_name=system_name,
            risk_level=risk_level,
            total_gaps=len(missing_requirements),
            requirement_plans=requirement_plans,
            summary=summary,
            recommendations=recommendations
        )

    def _format_label(self, req_name: str) -> str:
        """Convert CamelCase to readable label"""
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', req_name)
        return " ".join(words)

    def _estimate_effort(self, evidence_items: List[EvidenceItem]) -> str:
        """Estimate effort based on evidence items"""
        critical_count = sum(
            1 for e in evidence_items if e.priority == EvidencePriority.CRITICAL
        )
        total_count = len(evidence_items)

        if critical_count >= 2 or total_count >= 4:
            return "HIGH (2-4 weeks)"
        elif critical_count >= 1 or total_count >= 2:
            return "MEDIUM (1-2 weeks)"
        else:
            return "LOW (< 1 week)"

    def _generate_summary(self, requirement_plans: List[RequirementEvidencePlan]) -> Dict:
        """Generate plan summary statistics"""
        total_evidence_items = sum(
            len(rp.evidence_items) for rp in requirement_plans
        )

        by_priority = {}
        for rp in requirement_plans:
            priority = rp.priority.value
            by_priority[priority] = by_priority.get(priority, 0) + 1

        by_type = {}
        for rp in requirement_plans:
            for ei in rp.evidence_items:
                etype = ei.evidence_type.value
                by_type[etype] = by_type.get(etype, 0) + 1

        by_role = {}
        for rp in requirement_plans:
            for role in rp.responsible_roles:
                role_name = role.value
                by_role[role_name] = by_role.get(role_name, 0) + 1

        return {
            "total_requirements": len(requirement_plans),
            "total_evidence_items": total_evidence_items,
            "by_priority": by_priority,
            "by_evidence_type": by_type,
            "by_responsible_role": by_role
        }

    def _generate_recommendations(
        self,
        risk_level: str,
        requirement_plans: List[RequirementEvidencePlan],
        critical_gaps: List[Dict],
        scope_override_detected: bool = False,
        override_context: Optional[str] = None
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Scope override warning (v0.39.0)
        if scope_override_detected:
            context_label = override_context or "deployment context"
            recommendations.append(
                f"SCOPE ALERT: System with potentially excluded purpose is IN SCOPE due to {context_label}. "
                "Complete Scope Override Assessment per Art. 2."
            )

        # Critical gaps first
        critical_count = sum(
            1 for rp in requirement_plans if rp.priority == EvidencePriority.CRITICAL
        )
        if critical_count > 0:
            recommendations.append(
                f"URGENT: Address {critical_count} critical requirement gaps before deployment"
            )

        # FRIA recommendation for high-risk OR scope override contexts (v0.39.0)
        has_fria_trigger = any(
            "FundamentalRights" in rp.requirement_uri or
            "FRIA" in rp.requirement_uri or
            "VictimImpact" in rp.requirement_uri or
            "LegalConsequences" in rp.requirement_uri
            for rp in requirement_plans
        )
        if risk_level == "HighRisk" or has_fria_trigger or scope_override_detected:
            recommendations.append(
                "Conduct Fundamental Rights Impact Assessment (FRIA) per Art. 27 - "
                "mandatory for high-risk deployers and systems affecting fundamental rights"
            )

        # Human oversight for automated decisions
        has_oversight_gap = any(
            "HumanOversight" in rp.requirement_uri
            for rp in requirement_plans
        )
        if has_oversight_gap:
            recommendations.append(
                "Establish human oversight mechanisms per Art. 14 - ensure operators can intervene"
            )

        # Documentation for conformity
        has_doc_gap = any(
            "Documentation" in rp.requirement_uri
            for rp in requirement_plans
        )
        if has_doc_gap:
            recommendations.append(
                "Complete Annex IV technical documentation - required for conformity assessment"
            )

        # Bias/fairness for discrimination risk
        has_bias_gap = any(
            "NonDiscrimination" in rp.requirement_uri or "Bias" in rp.requirement_uri
            for rp in requirement_plans
        )
        if has_bias_gap:
            recommendations.append(
                "Conduct independent bias audit across protected characteristics per Art. 10(2)(f)"
            )

        # Scope-specific recommendations (v0.39.0)
        has_scope_assessment = any(
            "ScopeOverride" in rp.requirement_uri
            for rp in requirement_plans
        )
        if has_scope_assessment:
            recommendations.append(
                "Document scope applicability rationale with legal basis per Art. 2 exemptions and overrides"
            )

        has_victim_impact = any(
            "VictimImpact" in rp.requirement_uri
            for rp in requirement_plans
        )
        if has_victim_impact:
            recommendations.append(
                "Conduct specialized victim impact assessment - heightened duty of care for vulnerable persons"
            )

        has_legal_consequences = any(
            "LegalConsequences" in rp.requirement_uri
            for rp in requirement_plans
        )
        if has_legal_consequences:
            recommendations.append(
                "Document all legal effects on natural persons and establish appeal/challenge mechanisms"
            )

        # General recommendation
        recommendations.append(
            "Establish ongoing monitoring and periodic evidence review schedule"
        )

        return recommendations

    def to_dict(self, plan: EvidencePlan) -> Dict:
        """Convert evidence plan to dictionary for JSON serialization"""
        return {
            "plan_id": plan.plan_id,
            "generated_at": plan.generated_at,
            "system_name": plan.system_name,
            "risk_level": plan.risk_level,
            "total_gaps": plan.total_gaps,
            "summary": plan.summary,
            "recommendations": plan.recommendations,
            "requirement_plans": [
                {
                    "requirement_uri": rp.requirement_uri,
                    "requirement_label": rp.requirement_label,
                    "priority": rp.priority.value,
                    "article_reference": rp.article_reference,
                    "eli_uri": rp.eli_uri,
                    "dpv_measures": rp.dpv_measures,
                    "deadline_recommendation": rp.deadline_recommendation,
                    "responsible_roles": [r.value for r in rp.responsible_roles],
                    "estimated_effort": rp.estimated_effort,
                    "evidence_items": [
                        {
                            "id": ei.id,
                            "name": ei.name,
                            "description": ei.description,
                            "evidence_type": ei.evidence_type.value,
                            "priority": ei.priority.value,
                            "frequency": ei.frequency.value,
                            "responsible_role": ei.responsible_role.value,
                            "dpv_measure": ei.dpv_measure,
                            "templates": ei.templates,
                            "guidance": ei.guidance
                        }
                        for ei in rp.evidence_items
                    ]
                }
                for rp in plan.requirement_plans
            ]
        }

    def generate_markdown_report(self, plan: EvidencePlan) -> str:
        """Generate a markdown report of the evidence plan"""
        lines = [
            "# Evidence Generation Plan",
            "",
            f"**Plan ID:** {plan.plan_id}",
            f"**Generated:** {plan.generated_at}",
            f"**System:** {plan.system_name}",
            f"**Risk Level:** {plan.risk_level}",
            f"**Total Gaps:** {plan.total_gaps}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"- **Requirements to Address:** {plan.summary['total_requirements']}",
            f"- **Evidence Items Required:** {plan.summary['total_evidence_items']}",
            "",
            "### By Priority",
        ]

        for priority, count in plan.summary['by_priority'].items():
            lines.append(f"- {priority}: {count}")

        lines.extend([
            "",
            "### By Evidence Type",
        ])

        for etype, count in plan.summary['by_evidence_type'].items():
            lines.append(f"- {etype}: {count}")

        lines.extend([
            "",
            "---",
            "",
            "## Recommendations",
            "",
        ])

        for i, rec in enumerate(plan.recommendations, 1):
            lines.append(f"{i}. {rec}")

        lines.extend([
            "",
            "---",
            "",
            "## Detailed Evidence Requirements",
            "",
        ])

        for rp in plan.requirement_plans:
            lines.extend([
                f"### {rp.requirement_label}",
                "",
                f"**Priority:** {rp.priority.value}",
                f"**Article:** {rp.article_reference or 'N/A'}" + (f" ([EUR-Lex]({rp.eli_uri}))" if rp.eli_uri else ""),
                f"**Deadline:** {rp.deadline_recommendation}",
                f"**Responsible:** {', '.join(r.value for r in rp.responsible_roles)}",
                f"**Estimated Effort:** {rp.estimated_effort}",
                "",
                "**DPV Measures:**",
            ])

            for measure in rp.dpv_measures:
                lines.append(f"- `{measure}`")

            lines.extend([
                "",
                "**Required Evidence:**",
                "",
            ])

            for ei in rp.evidence_items:
                lines.extend([
                    f"#### {ei.id}: {ei.name}",
                    "",
                    f"- **Type:** {ei.evidence_type.value}",
                    f"- **Priority:** {ei.priority.value}",
                    f"- **Frequency:** {ei.frequency.value}",
                    f"- **Responsible:** {ei.responsible_role.value}",
                    f"- **Description:** {ei.description}",
                ])

                if ei.guidance:
                    lines.append(f"- **Guidance:** {ei.guidance}")

                if ei.templates:
                    lines.append(f"- **Templates:** {', '.join(ei.templates)}")

                lines.append("")

            lines.append("---")
            lines.append("")

        lines.extend([
            "",
            "---",
            "",
            f"*Generated by SERAMIS Evidence Planner | {plan.generated_at}*",
        ])

        return "\n".join(lines)
