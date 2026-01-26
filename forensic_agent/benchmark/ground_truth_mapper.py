"""
Ground Truth Mapper for AIAAIC to EU AI Act

Maps AIAAIC Repository taxonomy to EU AI Act ontology categories,
handling multi-label scenarios with priority-based primary type selection.

"""

from typing import Dict, List, Optional, Tuple


# =============================================================================
# ISSUE MAPPING: AIAAIC Issue(s) -> EU AI Act incident_type + Ontology IRIs
# =============================================================================

# Extended mapping with ontology IRIs for full traceability
# Structure: AIAAIC Issue -> (priority, incident_type, [ontology_iris])
# Priority: higher number = higher severity (safety/fundamental rights first)

ISSUE_PRIORITY_MAP_EXTENDED: Dict[str, Tuple[int, str, List[str]]] = {
    # Direct equivalences with ontology concepts
    "Safety": (10, "safety_failure", [
        "ai:SystemSafetyRequirement",
        "ai:RiskManagementRequirement",
        "ai:CausesRealWorldHarmContext",
        "ai:SafetyCriticalContext"
    ]),
    "Privacy/surveillance": (9, "privacy_violation", [
        "ai:PrivacyProtectionRequirement",
        "ai:DataPrivacyRequirement",
        "ai:BiometricDataSensitivityRiskCriterion",
        "ai:SurveillanceRiskCriterion",
        "ai:RealTimeBiometricIdentificationCriterion"
    ]),
    "Fairness": (8, "bias", [
        "ai:FairnessRequirement",
        "ai:BiasDetectionRequirement",
        "ai:HistoricalBiasReplicationRiskCriterion",
        "ai:ProtectedCharacteristicInferenceRiskCriterion"
    ]),
    "Accuracy/reliability": (7, "accuracy_failure", [
        "ai:AccuracyEvaluationRequirement",
        "ai:RobustnessRequirement",
        "ai:DistributionShiftRobustnessRequirement"
    ]),
    "Transparency": (6, "transparency_failure", [
        "ai:TransparencyRequirement",
        "ai:ExplainabilityRequirement",
        "ai:TraceabilityRequirement",
        "ai:BlackBoxDecisionRiskCriterion",
        "ai:LimitedTransparencyContext"
    ]),
    "Mis/disinformation": (5, "misinformation", [
        "ai:GPAITransparencyRequirement",
        "ai:MisinformationAmplificationRiskCriterion",
        "ai:UserNotificationRequirement"
    ]),
    "Copyright": (4, "copyright", [
        "ai:GPAIProviderObligations",
        "ai:DataProvenanceRequirement",
        "ai:DatasetDocumentationRequirement"
    ]),
    "Security": (3, "adversarial_attack", [
        "ai:SecurityRequirement",
        "ai:AdversarialRobustnessRequirement",
        "ai:VulnerabilityManagementRequirement",
        "ai:AccessControlRequirement",
        "ai:EncryptionRequirement"
    ]),

    # Mapped by semantic proximity
    "Accountability": (2, "transparency_failure", [
        "ai:AuditTrailRequirement",
        "ai:DocumentationRequirement",
        "ai:HumanOversightRequirement",
        "ai:PostMarketMonitoringRequirement"
    ]),
    "Authenticity/integrity": (1, "misinformation", [
        "ai:GPAITransparencyRequirement",
        "ai:UserNotificationRequirement"
    ]),

    # Additional AIAAIC issues with lower priority
    "Cheating/plagiarism": (1, "copyright", [
        "ai:DataProvenanceRequirement"
    ]),
    "Employment": (1, "bias", [
        "ai:FairnessRequirement",
        "ai:WorkforceEvaluationCriterion",
        "ai:RecruitmentEmploymentCriterion"
    ]),
}

# Simplified map for backward compatibility (without IRIs)
ISSUE_PRIORITY_MAP: Dict[str, Tuple[int, str]] = {
    k: (v[0], v[1]) for k, v in ISSUE_PRIORITY_MAP_EXTENDED.items()
}


# =============================================================================
# SECTOR MAPPING: AIAAIC Sector(s) -> EU AI Act DeploymentContext
# =============================================================================

# Maps AIAAIC sectors to EU AI Act deployment contexts and risk indicators
SECTOR_CONTEXT_MAP: Dict[str, Tuple[str, str]] = {
    # High-risk contexts (Annex III)
    "Govt - police": ("LawEnforcementContext", "HighRisk"),
    "Govt - security": ("LawEnforcementContext", "HighRisk"),
    "Govt - immigration": ("MigrationContext", "HighRisk"),
    "Govt - justice": ("JudicialContext", "HighRisk"),
    "Health": ("HealthcareContext", "HighRisk"),
    "Education": ("EducationContext", "HighRisk"),
    "Banking/finance": ("FinancialContext", "HighRisk"),
    "Insurance": ("FinancialContext", "HighRisk"),
    "Automotive": ("CriticalInfrastructure", "HighRisk"),
    "Transport/logistics": ("CriticalInfrastructure", "HighRisk"),
    "Energy/utilities": ("CriticalInfrastructure", "HighRisk"),

    # Lower risk contexts
    "Media/entertainment/sports/arts": ("EntertainmentContext", "MinimalRisk"),
    "Retail": ("CommercialContext", "LimitedRisk"),
    "Technology": ("TechnologyContext", "LimitedRisk"),
    "Business/professional services": ("BusinessContext", "LimitedRisk"),
    "Politics": ("PoliticalContext", "HighRisk"),  # Due to manipulation risks
}


# =============================================================================
# TECHNOLOGY MAPPING: AIAAIC Technology(ies) -> EU AI Act SystemType
# =============================================================================

TECHNOLOGY_TYPE_MAP: Dict[str, Tuple[str, Optional[str]]] = {
    # Vision systems
    "Facial recognition": ("vision", "BiometricIdentification"),
    "Computer vision": ("vision", None),
    "Object detection": ("vision", None),
    "Image recognition": ("vision", None),

    # NLP systems
    "NLP/text analysis": ("nlp", None),
    "Speech recognition": ("nlp", None),
    "Speech-to-text": ("nlp", None),
    "Chatbot": ("nlp", None),

    # Generative AI
    "Generative AI": ("multimodal", "GenerativeAI"),
    "Deepfake": ("multimodal", "GenerativeAI"),
    "Large language model (LLM)": ("nlp", "GenerativeAI"),

    # Autonomous systems
    "Self-driving system": ("vision", "AutonomousVehicle"),
    "Robotics": ("multimodal", "IndustrialAutomation"),
    "Drone": ("vision", "AutonomousVehicle"),

    # Tabular/ML
    "Machine learning": ("tabular", None),
    "Deep learning": ("tabular", None),
    "Neural network": ("tabular", None),
    "Predictive analytics": ("tabular", None),
}


# =============================================================================
# HARM MAPPING: AIAAIC External harms -> Risk indicators
# =============================================================================

HARM_RISK_INDICATORS: Dict[str, str] = {
    # Death/injury -> Always in scope, highest risk
    "Loss of life": "CausesDeathOrInjury",
    "Bodily injury": "CausesDeathOrInjury",
    "Physical harm": "CausesDeathOrInjury",

    # Fundamental rights impacts
    "Discrimination": "AffectsFundamentalRights",
    "Loss of rights/freedoms": "AffectsFundamentalRights",
    "Privacy loss": "AffectsFundamentalRights",

    # Vulnerable groups
    "Child safety": "MinorsAffected",

    # Legal consequences
    "Wrongful arrest": "LegalConsequences",
    "Wrongful detention": "LegalConsequences",
}


# =============================================================================
# SERIOUS INCIDENT MAPPING: AIAAIC -> EU AI Act Article 3(49)
# =============================================================================
# Maps AIAAIC issues and harms to EU AI Act serious incident types
# Reference: Article 3(49) - Definition of "serious incident"

# Maps AIAAIC "External harms" to Article 3(49) serious incident types
HARM_TO_SERIOUS_INCIDENT: Dict[str, List[str]] = {
    # Art. 3(49)(a) - Death or serious damage to health
    "Loss of life": ["DeathOrHealthHarm"],
    "Bodily injury": ["DeathOrHealthHarm"],
    "Physical harm": ["DeathOrHealthHarm"],
    "Psychological/mental health harm": ["DeathOrHealthHarm"],
    "Mental harm": ["DeathOrHealthHarm"],
    "Suicide/self-harm": ["DeathOrHealthHarm"],

    # Art. 3(49)(c) - Breach of fundamental rights
    "Discrimination": ["FundamentalRightsInfringement"],
    "Loss of rights/freedoms": ["FundamentalRightsInfringement"],
    "Privacy loss": ["FundamentalRightsInfringement"],
    "Wrongful arrest": ["FundamentalRightsInfringement"],
    "Wrongful detention": ["FundamentalRightsInfringement"],
    "Loss of livelihood": ["FundamentalRightsInfringement"],
    "Loss of liberty": ["FundamentalRightsInfringement"],
    "Harassment/abuse": ["FundamentalRightsInfringement"],

    # Art. 3(49)(d) - Serious harm to property or environment
    "Financial harm": ["PropertyOrEnvironmentHarm"],
    "Property damage": ["PropertyOrEnvironmentHarm"],
    "Environmental damage": ["PropertyOrEnvironmentHarm"],
    "Infrastructure damage": ["PropertyOrEnvironmentHarm", "CriticalInfrastructureDisruption"],
}

# Maps AIAAIC "Issues" to Article 3(49) serious incident types
# Note: Issues are causes, not outcomes - mapping is less direct
ISSUE_TO_SERIOUS_INCIDENT: Dict[str, List[str]] = {
    # Safety issues typically result in health/death harm
    "Safety": ["DeathOrHealthHarm"],

    # Privacy/surveillance typically affects fundamental rights
    "Privacy/surveillance": ["FundamentalRightsInfringement"],

    # Fairness issues affect fundamental rights (discrimination)
    "Fairness": ["FundamentalRightsInfringement"],

    # These may or may not result in serious incidents - context dependent
    "Accuracy/reliability": [],  # Could lead to any type depending on context
    "Transparency": [],  # Not directly a serious incident
    "Accountability": [],  # Not directly a serious incident
    "Mis/disinformation": [],  # Could lead to FundamentalRightsInfringement
    "Copyright": [],  # Not typically a serious incident
    "Security": [],  # Could lead to any type depending on attack outcome
}

# Maps AIAAIC "Sector" to potential serious incident types
# Critical infrastructure sectors map to CriticalInfrastructureDisruption
SECTOR_TO_SERIOUS_INCIDENT: Dict[str, List[str]] = {
    # Critical infrastructure sectors (Art. 3(49)(b))
    "Energy/utilities": ["CriticalInfrastructureDisruption"],
    "Transport/logistics": ["CriticalInfrastructureDisruption"],
    "Health": ["CriticalInfrastructureDisruption", "DeathOrHealthHarm"],
    "Govt - security": ["CriticalInfrastructureDisruption"],

    # High fundamental rights impact sectors
    "Govt - police": ["FundamentalRightsInfringement"],
    "Govt - justice": ["FundamentalRightsInfringement"],
    "Govt - immigration": ["FundamentalRightsInfringement"],
    "Banking/finance": ["PropertyOrEnvironmentHarm", "FundamentalRightsInfringement"],
}


# =============================================================================
# MAIN MAPPING FUNCTIONS
# =============================================================================

def map_issues_to_ground_truth(issues_str: str, include_iris: bool = False) -> Dict:
    """
    Maps AIAAIC Issue(s) to ground truth multi-label structure.

    Generates a structure that allows both strict evaluation
    (primary_type) and flexible evaluation (incident_types).

    Args:
        issues_str: Semicolon-separated AIAAIC issues (e.g., "Safety; Privacy/surveillance")
        include_iris: If True, includes ontology IRIs for traceability

    Returns:
        dict with:
            - incident_types: List of all mapped types
            - primary_type: Most severe type for strict evaluation
            - unmapped_issues: Issues not in mapping (for analysis)
            - ontology_iris: List of related ontology IRIs (if include_iris=True)
    """
    if not issues_str or not issues_str.strip():
        result = {
            "incident_types": [],
            "primary_type": None,
            "unmapped_issues": []
        }
        if include_iris:
            result["ontology_iris"] = []
        return result

    issues = [i.strip() for i in issues_str.split(';')]

    ground_truth = {
        "incident_types": [],
        "primary_type": None,
        "unmapped_issues": []
    }

    if include_iris:
        ground_truth["ontology_iris"] = []

    max_priority = 0

    for issue in issues:
        if issue in ISSUE_PRIORITY_MAP_EXTENDED:
            priority, incident_type, iris = ISSUE_PRIORITY_MAP_EXTENDED[issue]

            # Add to list if not already present (avoid duplicates from merged mappings)
            if incident_type not in ground_truth["incident_types"]:
                ground_truth["incident_types"].append(incident_type)

            # Add ontology IRIs if requested
            if include_iris:
                for iri in iris:
                    if iri not in ground_truth["ontology_iris"]:
                        ground_truth["ontology_iris"].append(iri)

            # Update primary if higher priority
            if priority > max_priority:
                max_priority = priority
                ground_truth["primary_type"] = incident_type
        else:
            ground_truth["unmapped_issues"].append(issue)

    return ground_truth


def map_sector_to_context(sector_str: str) -> Dict:
    """
    Maps AIAAIC Sector(s) to EU AI Act deployment context.

    For multi-value sectors, applies "most restrictive" rule:
    HighRisk context takes precedence over MinimalRisk.

    Args:
        sector_str: Semicolon-separated AIAAIC sectors

    Returns:
        dict with:
            - contexts: List of all deployment contexts
            - primary_context: Most restrictive context
            - risk_indicator: Highest risk level found
    """
    if not sector_str or not sector_str.strip():
        return {
            "contexts": [],
            "primary_context": None,
            "risk_indicator": None
        }

    sectors = [s.strip() for s in sector_str.split(';')]

    result = {
        "contexts": [],
        "primary_context": None,
        "risk_indicator": None
    }

    risk_priority = {"HighRisk": 3, "LimitedRisk": 2, "MinimalRisk": 1}
    max_risk_priority = 0

    for sector in sectors:
        if sector in SECTOR_CONTEXT_MAP:
            context, risk = SECTOR_CONTEXT_MAP[sector]

            if context not in result["contexts"]:
                result["contexts"].append(context)

            # Apply most restrictive rule
            if risk_priority.get(risk, 0) > max_risk_priority:
                max_risk_priority = risk_priority[risk]
                result["primary_context"] = context
                result["risk_indicator"] = risk

    return result


def map_technology_to_system_type(tech_str: str) -> Dict:
    """
    Maps AIAAIC Technology(ies) to EU AI Act system type and purpose.

    Args:
        tech_str: Semicolon-separated AIAAIC technologies

    Returns:
        dict with:
            - system_types: List of system types (vision, nlp, tabular, multimodal)
            - purposes: List of identified purposes (BiometricIdentification, etc.)
            - primary_type: Most specific system type
    """
    if not tech_str or not tech_str.strip():
        return {
            "system_types": [],
            "purposes": [],
            "primary_type": None
        }

    technologies = [t.strip() for t in tech_str.split(';')]

    result = {
        "system_types": [],
        "purposes": [],
        "primary_type": None
    }

    # Priority: vision > multimodal > nlp > tabular (more specific = higher priority)
    type_priority = {"vision": 4, "multimodal": 3, "nlp": 2, "tabular": 1}
    max_priority = 0

    for tech in technologies:
        if tech in TECHNOLOGY_TYPE_MAP:
            sys_type, purpose = TECHNOLOGY_TYPE_MAP[tech]

            if sys_type not in result["system_types"]:
                result["system_types"].append(sys_type)

            if purpose and purpose not in result["purposes"]:
                result["purposes"].append(purpose)

            if type_priority.get(sys_type, 0) > max_priority:
                max_priority = type_priority[sys_type]
                result["primary_type"] = sys_type

    return result


def map_harms_to_risk_indicators(individual_harms: str, societal_harms: str = "") -> Dict:
    """
    Maps AIAAIC External harms to EU AI Act risk indicators.

    Args:
        individual_harms: Semicolon-separated individual harms
        societal_harms: Semicolon-separated societal harms

    Returns:
        dict with:
            - risk_indicators: List of risk indicators
            - causes_death_or_injury: bool
            - affects_fundamental_rights: bool
            - affects_minors: bool
    """
    result = {
        "risk_indicators": [],
        "causes_death_or_injury": False,
        "affects_fundamental_rights": False,
        "affects_minors": False,
        "has_legal_consequences": False
    }

    all_harms = []
    if individual_harms:
        all_harms.extend([h.strip() for h in individual_harms.split(';')])
    if societal_harms:
        all_harms.extend([h.strip() for h in societal_harms.split(';')])

    for harm in all_harms:
        if harm in HARM_RISK_INDICATORS:
            indicator = HARM_RISK_INDICATORS[harm]

            if indicator not in result["risk_indicators"]:
                result["risk_indicators"].append(indicator)

            # Set boolean flags
            if indicator == "CausesDeathOrInjury":
                result["causes_death_or_injury"] = True
            elif indicator == "AffectsFundamentalRights":
                result["affects_fundamental_rights"] = True
            elif indicator == "MinorsAffected":
                result["affects_minors"] = True
            elif indicator == "LegalConsequences":
                result["has_legal_consequences"] = True

    return result


def map_to_serious_incident_types(
    issues_str: str,
    sector_str: str,
    individual_harms_str: str,
    societal_harms_str: str = ""
) -> Dict:
    """
    Maps AIAAIC data to EU AI Act Article 3(49) serious incident types.

    Derives expected serious incident types from AIAAIC taxonomy for ground truth.

    Args:
        issues_str: Semicolon-separated AIAAIC issues
        sector_str: Semicolon-separated AIAAIC sectors
        individual_harms_str: Semicolon-separated individual harms
        societal_harms_str: Semicolon-separated societal harms

    Returns:
        dict with:
            - serious_incident_types: List of expected Art. 3(49) types
            - primary_type: Most likely serious incident type (priority-based)
            - sources: Dict showing which AIAAIC fields contributed each type
            - is_serious_incident: bool - whether this qualifies as a serious incident
    """
    result = {
        "serious_incident_types": [],
        "primary_type": None,
        "sources": {
            "from_harms": [],
            "from_issues": [],
            "from_sector": []
        },
        "is_serious_incident": False
    }

    # Priority order for determining primary type
    # DeathOrHealthHarm > CriticalInfrastructureDisruption > FundamentalRightsInfringement > PropertyOrEnvironmentHarm
    type_priority = {
        "DeathOrHealthHarm": 4,
        "CriticalInfrastructureDisruption": 3,
        "FundamentalRightsInfringement": 2,
        "PropertyOrEnvironmentHarm": 1
    }

    all_types = set()
    max_priority = 0

    # 1. Map from harms (most direct indicator)
    all_harms = []
    if individual_harms_str:
        all_harms.extend([h.strip() for h in individual_harms_str.split(';')])
    if societal_harms_str:
        all_harms.extend([h.strip() for h in societal_harms_str.split(';')])

    for harm in all_harms:
        if harm in HARM_TO_SERIOUS_INCIDENT:
            types = HARM_TO_SERIOUS_INCIDENT[harm]
            for t in types:
                if t not in all_types:
                    all_types.add(t)
                    result["sources"]["from_harms"].append({"harm": harm, "type": t})
                if type_priority.get(t, 0) > max_priority:
                    max_priority = type_priority[t]
                    result["primary_type"] = t

    # 2. Map from issues (less direct, but useful)
    if issues_str:
        issues = [i.strip() for i in issues_str.split(';')]
        for issue in issues:
            if issue in ISSUE_TO_SERIOUS_INCIDENT:
                types = ISSUE_TO_SERIOUS_INCIDENT[issue]
                for t in types:
                    if t not in all_types:
                        all_types.add(t)
                        result["sources"]["from_issues"].append({"issue": issue, "type": t})
                    if type_priority.get(t, 0) > max_priority:
                        max_priority = type_priority[t]
                        result["primary_type"] = t

    # 3. Map from sector (contextual indicator)
    if sector_str:
        sectors = [s.strip() for s in sector_str.split(';')]
        for sector in sectors:
            if sector in SECTOR_TO_SERIOUS_INCIDENT:
                types = SECTOR_TO_SERIOUS_INCIDENT[sector]
                for t in types:
                    if t not in all_types:
                        all_types.add(t)
                        result["sources"]["from_sector"].append({"sector": sector, "type": t})
                    if type_priority.get(t, 0) > max_priority:
                        max_priority = type_priority[t]
                        result["primary_type"] = t

    result["serious_incident_types"] = sorted(list(all_types), key=lambda x: -type_priority.get(x, 0))
    result["is_serious_incident"] = len(all_types) > 0

    return result


def create_full_ground_truth(row: Dict) -> Dict:
    """
    Creates complete ground truth from an AIAAIC CSV row.

    Args:
        row: Dictionary with AIAAIC CSV columns

    Returns:
        Complete ground truth structure for benchmark evaluation
    """
    ground_truth = {
        "aiaaic_id": row.get("aiaaic_id", ""),
        "headline": row.get("headline", ""),

        # Issue mapping (primary evaluation target)
        "issues": map_issues_to_ground_truth(row.get("issues", "")),

        # Context mapping (for risk level validation)
        "context": map_sector_to_context(row.get("sector", "")),

        # Technology mapping (for system type validation)
        "technology": map_technology_to_system_type(row.get("technology", "")),

        # Harm mapping (for scope determination)
        "harms": map_harms_to_risk_indicators(
            row.get("individual_harms", ""),
            row.get("societal_harms", "")
        ),

        # NEW: Serious incident type mapping (v0.41.0 - Art. 3(49))
        "serious_incident": map_to_serious_incident_types(
            row.get("issues", ""),
            row.get("sector", ""),
            row.get("individual_harms", ""),
            row.get("societal_harms", "")
        ),

        # Raw AIAAIC values for reference
        "raw": {
            "issues": row.get("issues", ""),
            "sector": row.get("sector", ""),
            "technology": row.get("technology", ""),
            "purpose": row.get("purpose", ""),
            "deployer": row.get("deployer", ""),
            "developer": row.get("developer", ""),
            "individual_harms": row.get("individual_harms", ""),
            "societal_harms": row.get("societal_harms", ""),
        }
    }

    # Determine expected risk level based on all indicators
    ground_truth["expected_risk_level"] = _determine_expected_risk(ground_truth)

    return ground_truth


def _determine_expected_risk(gt: Dict) -> str:
    """
    Determines expected risk level from ground truth indicators.

    Logic based on EU AI Act:
    - CausesDeathOrInjury -> Always HighRisk
    - AffectsFundamentalRights -> HighRisk
    - HighRisk context -> HighRisk
    - Otherwise -> Based on incident type severity
    """
    # Death/injury always brings into scope as HighRisk
    if gt["harms"]["causes_death_or_injury"]:
        return "HighRisk"

    # Fundamental rights impact -> HighRisk
    if gt["harms"]["affects_fundamental_rights"]:
        return "HighRisk"

    # HighRisk context from sector
    if gt["context"]["risk_indicator"] == "HighRisk":
        return "HighRisk"

    # Check if primary issue type indicates high risk
    high_risk_types = {"safety_failure", "privacy_violation", "bias", "accuracy_failure"}
    if gt["issues"]["primary_type"] in high_risk_types:
        return "HighRisk"

    # Default based on context
    if gt["context"]["risk_indicator"]:
        return gt["context"]["risk_indicator"]

    return "LimitedRisk"


# =============================================================================
# EVALUATION FUNCTIONS
# =============================================================================

def evaluate_incident_type(predicted: str, ground_truth: Dict) -> Dict:
    """
    Evaluates predicted incident type against ground truth.

    Returns both strict and flexible accuracy metrics.

    Args:
        predicted: Incident type predicted by the agent
        ground_truth: Ground truth from map_issues_to_ground_truth()

    Returns:
        dict with:
            - strict_match: True if matches primary_type
            - flexible_match: True if matches any incident_type
            - predicted: The predicted value
            - expected_primary: The primary expected value
            - expected_all: All expected values
    """
    # Normalize to lowercase for case-insensitive comparison
    predicted_lower = predicted.lower() if predicted else ""
    primary_lower = ground_truth["primary_type"].lower() if ground_truth["primary_type"] else ""
    types_lower = [t.lower() for t in ground_truth["incident_types"]]

    return {
        "strict_match": predicted_lower == primary_lower,
        "flexible_match": predicted_lower in types_lower,
        "predicted": predicted,
        "expected_primary": ground_truth["primary_type"],
        "expected_all": ground_truth["incident_types"]
    }


def evaluate_risk_level(predicted: str, ground_truth: Dict) -> Dict:
    """
    Evaluates predicted risk level against ground truth.

    Args:
        predicted: Risk level predicted by the agent
        ground_truth: Full ground truth from create_full_ground_truth()

    Returns:
        dict with match status and details
    """
    expected = ground_truth.get("expected_risk_level", "Unknown")

    return {
        "match": predicted == expected,
        "predicted": predicted,
        "expected": expected,
        "context_risk": ground_truth["context"]["risk_indicator"],
        "has_death_injury": ground_truth["harms"]["causes_death_or_injury"]
    }


def evaluate_serious_incident_type(predicted: List[str], ground_truth: Dict) -> Dict:
    """
    Evaluates predicted serious incident types against ground truth.

    Uses multi-label evaluation metrics:
    - strict_match: Predicted set exactly equals expected set
    - primary_match: Predicted primary type matches expected primary type
    - any_match: At least one predicted type is in expected types
    - precision: |predicted ∩ expected| / |predicted|
    - recall: |predicted ∩ expected| / |expected|
    - f1: Harmonic mean of precision and recall

    Args:
        predicted: List of serious incident types predicted by the agent
        ground_truth: Full ground truth from create_full_ground_truth()

    Returns:
        dict with evaluation metrics
    """
    serious_gt = ground_truth.get("serious_incident", {})
    expected = set(serious_gt.get("serious_incident_types", []))
    expected_primary = serious_gt.get("primary_type")
    is_serious = serious_gt.get("is_serious_incident", False)

    # Normalize predicted to set
    predicted_set = set(predicted) if predicted else set()

    # Handle edge cases
    if not expected and not predicted_set:
        # Both empty - correct negative
        return {
            "strict_match": True,
            "primary_match": True,
            "any_match": True,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
            "predicted": list(predicted_set),
            "expected": list(expected),
            "expected_primary": expected_primary,
            "is_serious_incident": is_serious,
            "correct_negative": True
        }

    if not expected and predicted_set:
        # False positive - predicted serious incident when none expected
        return {
            "strict_match": False,
            "primary_match": False,
            "any_match": False,
            "precision": 0.0,
            "recall": 1.0,  # Nothing to recall
            "f1": 0.0,
            "predicted": list(predicted_set),
            "expected": list(expected),
            "expected_primary": expected_primary,
            "is_serious_incident": is_serious,
            "false_positive": True
        }

    if expected and not predicted_set:
        # False negative - missed serious incident
        return {
            "strict_match": False,
            "primary_match": False,
            "any_match": False,
            "precision": 1.0,  # Nothing predicted incorrectly
            "recall": 0.0,
            "f1": 0.0,
            "predicted": list(predicted_set),
            "expected": list(expected),
            "expected_primary": expected_primary,
            "is_serious_incident": is_serious,
            "false_negative": True
        }

    # Both have values - calculate metrics
    intersection = predicted_set & expected
    precision = len(intersection) / len(predicted_set) if predicted_set else 0.0
    recall = len(intersection) / len(expected) if expected else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # Primary match - check if any predicted matches the expected primary
    primary_match = expected_primary in predicted_set if expected_primary else False

    return {
        "strict_match": predicted_set == expected,
        "primary_match": primary_match,
        "any_match": len(intersection) > 0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "predicted": list(predicted_set),
        "expected": list(expected),
        "expected_primary": expected_primary,
        "is_serious_incident": is_serious,
        "intersection": list(intersection),
        "missed": list(expected - predicted_set),
        "extra": list(predicted_set - expected)
    }


if __name__ == "__main__":
    # Test the mapper
    print("=== Ground Truth Mapper Test ===\n")

    # Test issue mapping without IRIs
    test_issues = "Accuracy/reliability; Mis/disinformation; Safety; Security"
    result = map_issues_to_ground_truth(test_issues)
    print(f"Issues: {test_issues}")
    print(f"Result (without IRIs): {result}")
    print()

    # Test issue mapping WITH IRIs
    result_with_iris = map_issues_to_ground_truth(test_issues, include_iris=True)
    print(f"Result (with IRIs):")
    print(f"  incident_types: {result_with_iris['incident_types']}")
    print(f"  primary_type: {result_with_iris['primary_type']}")
    print(f"  ontology_iris: {result_with_iris['ontology_iris']}")
    print()

    # Test sector mapping
    test_sector = "Health; Education"
    result = map_sector_to_context(test_sector)
    print(f"Sector: {test_sector}")
    print(f"Result: {result}")
    print()

    # Test technology mapping
    test_tech = "Facial recognition; Machine learning"
    result = map_technology_to_system_type(test_tech)
    print(f"Technology: {test_tech}")
    print(f"Result: {result}")
    print()

    # Test harm mapping
    test_harms = "Loss of life; Discrimination"
    result = map_harms_to_risk_indicators(test_harms)
    print(f"Harms: {test_harms}")
    print(f"Result: {result}")
    print()

    # Test serious incident mapping (NEW v0.41.0)
    print("=== Serious Incident Mapping Test (Art. 3(49)) ===\n")

    test_serious = map_to_serious_incident_types(
        issues_str="Safety; Privacy/surveillance",
        sector_str="Health; Govt - police",
        individual_harms_str="Loss of life; Discrimination",
        societal_harms_str=""
    )
    print(f"Test case: Safety + Privacy issues, Health + Police sectors, Death + Discrimination harms")
    print(f"  serious_incident_types: {test_serious['serious_incident_types']}")
    print(f"  primary_type: {test_serious['primary_type']}")
    print(f"  is_serious_incident: {test_serious['is_serious_incident']}")
    print(f"  sources: {test_serious['sources']}")
    print()

    # Test evaluation
    print("=== Serious Incident Evaluation Test ===\n")
    mock_ground_truth = {
        "serious_incident": test_serious
    }

    # Test 1: Perfect match
    eval1 = evaluate_serious_incident_type(
        ["DeathOrHealthHarm", "FundamentalRightsInfringement"],
        mock_ground_truth
    )
    print(f"Test 1 - Predicted: ['DeathOrHealthHarm', 'FundamentalRightsInfringement']")
    print(f"  strict_match: {eval1['strict_match']}")
    print(f"  primary_match: {eval1['primary_match']}")
    print(f"  f1: {eval1['f1']:.2f}")
    print()

    # Test 2: Partial match
    eval2 = evaluate_serious_incident_type(
        ["DeathOrHealthHarm"],
        mock_ground_truth
    )
    print(f"Test 2 - Predicted: ['DeathOrHealthHarm']")
    print(f"  strict_match: {eval2['strict_match']}")
    print(f"  primary_match: {eval2['primary_match']}")
    print(f"  precision: {eval2['precision']:.2f}")
    print(f"  recall: {eval2['recall']:.2f}")
    print(f"  f1: {eval2['f1']:.2f}")
    print()

    # Test 3: No match
    eval3 = evaluate_serious_incident_type(
        ["PropertyOrEnvironmentHarm"],
        mock_ground_truth
    )
    print(f"Test 3 - Predicted: ['PropertyOrEnvironmentHarm']")
    print(f"  any_match: {eval3['any_match']}")
    print(f"  f1: {eval3['f1']:.2f}")
