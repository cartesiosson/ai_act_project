"""
AIAAIC Issue to EU AI Act Requirement Mapping

This module defines the ground truth mapping between AIAAIC Issues and
expected EU AI Act compliance requirements. Used for benchmark evaluation.

Logic: If an incident has Issue X, then the system SHOULD have required Requirement Y.
       If the agent detects that Requirement Y is missing, that's a TRUE POSITIVE.
"""

from typing import Dict, List, Set

# =============================================================================
# REQUIREMENT SYNONYMS: Maps ontology requirement names to benchmark names
# =============================================================================
# The AIRO ontology uses different names than our benchmark expectations.
# This mapping allows detected requirements to match expected requirements.
#
# Format: "canonical_name": ["synonym1", "synonym2", ...]
# Where canonical_name is the benchmark expectation (lowercase, no separators)
# =============================================================================
REQUIREMENT_SYNONYMS: Dict[str, List[str]] = {
    # Safety: ontology uses SystemSafetyRequirement
    "safetyrequirement": [
        "systemsafetyrequirement",
    ],
    # Accuracy: ontology uses AccuracyEvaluationRequirement
    "accuracyrequirement": [
        "accuracyevaluationrequirement",
    ],
    # Risk Management: ontology uses RiskAssessmentRequirement
    "riskmanagementrequirement": [
        "riskassessmentrequirement",
    ],
    # Fairness: ontology splits into NonDiscrimination + BiasDetection
    # (BiasDetection already in mapping, NonDiscrimination is separate)
    "fairnessrequirement": [
        "nondiscriminationrequirement",
        "biasdetectionrequirement",
    ],
    # Cybersecurity: ontology uses SecurityRequirement
    "cybersecurityrequirement": [
        "securityrequirement",
    ],
    # Logging: ontology also has AuditTrailRequirement
    "loggingrequirement": [
        "audittrailrequirement",
    ],
    # Privacy: ontology also has DataPrivacyRequirement
    "privacyprotectionrequirement": [
        "dataprivacyrequirement",
    ],
}

# Build reverse mapping for fast lookup: synonym -> canonical
SYNONYM_TO_CANONICAL: Dict[str, str] = {}
for canonical, synonyms in REQUIREMENT_SYNONYMS.items():
    for syn in synonyms:
        SYNONYM_TO_CANONICAL[syn] = canonical


# AIAAIC Issue → Expected EU AI Act Requirements (that should be missing/violated)
ISSUE_TO_REQUIREMENTS: Dict[str, List[str]] = {
    # Core EU AI Act requirements
    "Transparency": [
        "TransparencyRequirement",
        "GPAITransparencyRequirement",
    ],
    "Accuracy/reliability": [
        "AccuracyRequirement",
        "RobustnessRequirement",
        "AccuracyEvaluationRequirement",
    ],
    "Privacy/surveillance": [
        "DataGovernanceRequirement",
        "PrivacyProtectionRequirement",
    ],
    "Privacy": [
        "DataGovernanceRequirement",
        "PrivacyProtectionRequirement",
    ],
    "Fairness": [
        "FairnessRequirement",
        "NonDiscriminationRequirement",
        "BiasDetectionRequirement",
    ],
    "Accountability": [
        "DocumentationRequirement",
        "HumanOversightRequirement",
        "LoggingRequirement",
    ],
    "Safety": [
        "SafetyRequirement",
        "RobustnessRequirement",
        "RiskManagementRequirement",
    ],
    "Security": [
        "SecurityRequirement",
        "CybersecurityRequirement",
    ],
    "Human rights/civil liberties": [
        "FundamentalRightsAssessmentRequirement",
        "HumanOversightRequirement",
    ],

    # Secondary mappings
    "Alignment": [
        "HumanOversightRequirement",
        "SafetyRequirement",
    ],
    "Mis/disinformation": [
        "TransparencyRequirement",
        "AccuracyRequirement",
    ],
    "Authenticity/integrity": [
        "TransparencyRequirement",
        "DocumentationRequirement",
    ],
    "Normalisation": [
        "HumanOversightRequirement",
        "SafetyRequirement",
    ],
    "Employment": [
        "FundamentalRightsAssessmentRequirement",
        "TransparencyRequirement",
        "NonDiscriminationRequirement",
    ],
    "Dual use": [
        "RiskManagementRequirement",
        "SafetyRequirement",
    ],
    "Ethics/values": [
        "HumanOversightRequirement",
        "FundamentalRightsAssessmentRequirement",
    ],
}

# Normalized requirement names (strip prefixes for matching)
def normalize_requirement(req: str) -> str:
    """Normalize requirement name for comparison."""
    # Remove common prefixes
    for prefix in ["ai:", "http://ai-act.eu/ai#", "AI#"]:
        if req.startswith(prefix):
            req = req[len(prefix):]
    return req.lower().replace("_", "").replace("-", "")


def get_expected_requirements(issues: List[str]) -> Set[str]:
    """
    Given AIAAIC issues, return the set of expected requirements
    that should have been in place (and thus should be missing).
    """
    expected = set()
    for issue in issues:
        # Clean issue string
        issue_clean = issue.strip()
        if issue_clean in ISSUE_TO_REQUIREMENTS:
            for req in ISSUE_TO_REQUIREMENTS[issue_clean]:
                expected.add(normalize_requirement(req))
    return expected


def get_detected_gaps(missing_requirements: List[str]) -> Set[str]:
    """
    Normalize the missing requirements detected by the agent.

    Applies synonym mapping so that ontology names match benchmark expectations.
    E.g., if agent detects "SystemSafetyRequirement", it maps to "safetyrequirement"
    which matches the expected "SafetyRequirement".
    """
    detected = set()
    for req in missing_requirements:
        normalized = normalize_requirement(req)
        # Check if this is a synonym and map to canonical name
        canonical = SYNONYM_TO_CANONICAL.get(normalized, normalized)
        detected.add(canonical)
    return detected


def calculate_metrics(expected: Set[str], detected: Set[str]) -> Dict:
    """
    Calculate metrics for requirement gap detection.

    KEY INSIGHT: Over-detection is NOT penalized. The agent detecting MORE gaps
    than AIAAIC labels is acceptable behavior - the agent may be more thorough.

    Metrics:
    - Coverage (primary): % of expected requirements that were detected
    - True Positive: Expected requirement is in detected gaps
    - Additional: Detected gaps beyond expected (informational, not penalized)
    - Missed: Expected requirements not detected (this IS penalized)

    Success criteria: Agent detects AT LEAST the expected requirements.
    """
    if not expected and not detected:
        return {
            "true_positives": 0,
            "additional_detected": 0,
            "missed": 0,
            "coverage": 1.0,
            "total_expected": 0,
            "total_detected": 0,
        }

    true_positives = len(expected & detected)
    additional_detected = len(detected - expected)  # Not penalized
    missed = len(expected - detected)  # This is what we care about

    # Coverage: What % of expected requirements were detected?
    coverage = true_positives / len(expected) if len(expected) > 0 else 1.0

    # For backwards compatibility, also compute traditional metrics
    # but the KEY metric is coverage (recall-only)
    precision = true_positives / len(detected) if len(detected) > 0 else 0.0
    recall = coverage  # Same as coverage
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "true_positives": true_positives,
        "additional_detected": additional_detected,  # Renamed from false_positives
        "missed": missed,  # Renamed from false_negatives
        "coverage": coverage,  # PRIMARY METRIC
        "precision": precision,  # For reference
        "recall": recall,  # Same as coverage
        "f1": f1,  # For reference
        "total_expected": len(expected),
        "total_detected": len(detected),
        "expected": list(expected),
        "detected": list(detected),
        "matched": list(expected & detected),
        "over_detected": list(detected - expected),
        "missed_list": list(expected - detected),
        # Legacy fields for backwards compatibility
        "false_positives": additional_detected,
        "false_negatives": missed,
    }


# Issue categories for heatmap grouping
ISSUE_CATEGORIES = {
    "Core Compliance": ["Transparency", "Accountability", "Safety", "Security"],
    "Data & Privacy": ["Privacy/surveillance", "Privacy", "Accuracy/reliability"],
    "Fairness & Rights": ["Fairness", "Human rights/civil liberties", "Employment"],
    "Content & Integrity": ["Mis/disinformation", "Authenticity/integrity", "Alignment"],
}


def get_all_mapped_issues() -> List[str]:
    """Return all issues that have requirement mappings."""
    return list(ISSUE_TO_REQUIREMENTS.keys())
