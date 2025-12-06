"""
Generate synthetic AI incidents for benchmark testing
Based on AIAAIC database patterns
"""

import json
import random
from typing import List, Dict

# Incident templates based on real AIAAIC patterns
INCIDENT_TEMPLATES = [
    # Facial Recognition Bias
    {
        "system_names": ["FaceID", "RecogniTech", "VisionAI", "BiometricScan", "FaceMatch"],
        "system_type": "vision",
        "purpose": "BiometricIdentification",
        "incident_type": "bias",
        "template": "{system} facial recognition system exhibited racial and gender bias in {year}. "
                   "The system misidentified {affected_group} at rates {error_rate}% higher than {baseline_group}. "
                   "Deployed in {context} with {decision_type}. {organization} {response_action}."
    },
    # Hiring Discrimination
    {
        "system_names": ["HireBot", "TalentAI", "RecruitPro", "CVAnalyzer", "HiringAssistant"],
        "system_type": "nlp",
        "purpose": "EmploymentDecision",
        "incident_type": "discrimination",
        "template": "{system} automated hiring system discriminated against {affected_group} in {year}. "
                   "Algorithm trained on historical data showing bias. Used for {context} with {decision_type}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # Credit Scoring Bias
    {
        "system_names": ["CreditAI", "LoanDecider", "FinanceScore", "RiskAnalyzer", "CreditBot"],
        "system_type": "tabular",
        "purpose": "CreditScoring",
        "incident_type": "discrimination",
        "template": "{system} credit scoring algorithm discriminated against {affected_group} in {year}. "
                   "System denied loans at {error_rate}% higher rate for minority applicants. "
                   "Processed {data_types} with {decision_type}. {organization} {response_action}."
    },
    # Healthcare AI Error
    {
        "system_names": ["MedAI", "DiagnosisBot", "HealthPredict", "PatientRisk", "ClinicalAI"],
        "system_type": "multimodal",
        "purpose": "HealthcareDecision",
        "incident_type": "safety_failure",
        "template": "{system} diagnostic system made critical errors affecting {affected_count} patients in {year}. "
                   "Algorithm misdiagnosed {affected_group} due to training data bias. "
                   "Used in {context} for {decision_type}. {organization} {response_action}."
    },
    # Predictive Policing Bias
    {
        "system_names": ["PredPol", "CrimePredict", "JusticeAI", "RiskAssess", "PoliceAI"],
        "system_type": "tabular",
        "purpose": "PredictivePolicing",
        "incident_type": "discrimination",
        "template": "{system} predictive policing algorithm showed racial bias in {year}. "
                   "System flagged {affected_group} as high-risk at {error_rate}% higher rates. "
                   "Deployed in {context} with {decision_type} and {oversight}. "
                   "{organization} {response_action}."
    },
    # Data Breach / Privacy Violation
    {
        "system_names": ["ChatAI", "PersonalAssist", "DataCollect", "UserTrack", "AnalyticsBot"],
        "system_type": "nlp",
        "purpose": "PersonalAssistant",
        "incident_type": "privacy_violation",
        "template": "{system} exposed {data_types} of {affected_count} users in {year}. "
                   "Security vulnerability allowed unauthorized access to conversation histories. "
                   "System processed {data_volume} without adequate safeguards. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # Emotion Recognition Misuse
    {
        "system_names": ["EmotionAI", "MoodDetect", "FeelingTrack", "AffectAnalyze", "EmotionScan"],
        "system_type": "vision",
        "purpose": "EmotionRecognition",
        "incident_type": "privacy_violation",
        "template": "{system} emotion recognition system deployed without consent in {context} in {year}. "
                   "Monitored {affected_group} processing {data_types}. "
                   "Used for {decision_type} with {oversight}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # Social Scoring System
    {
        "system_names": ["SocialScore", "TrustRank", "CitizenRate", "BehaviorTrack", "ReputationAI"],
        "system_type": "multimodal",
        "purpose": "SocialScoring",
        "incident_type": "discrimination",
        "template": "{system} social scoring system discriminated against {affected_group} in {year}. "
                   "Algorithm assigned lower scores based on {discriminatory_factors}. "
                   "Impacted access to {services} affecting {affected_count} people. "
                   "{organization} {response_action}."
    },
    # Deepfake / Synthetic Media
    {
        "system_names": ["DeepFake", "SynthVoice", "VideoGen", "FaceSwap", "MediaSynth"],
        "system_type": "multimodal",
        "purpose": "ContentGeneration",
        "incident_type": "safety_failure",
        "template": "{system} deepfake generation system misused to create non-consensual content in {year}. "
                   "Generated synthetic media of {affected_group} without consent. "
                   "Content spread on {platform} affecting {affected_count} individuals. "
                   "{organization} {response_action}."
    },
    # Autonomous Vehicle Accident
    {
        "system_names": ["AutoDrive", "SmartCar", "RoboDriver", "AutoPilot", "VehicleAI"],
        "system_type": "vision",
        "purpose": "AutonomousVehicle",
        "incident_type": "safety_failure",
        "template": "{system} autonomous vehicle system caused {accident_type} in {year}. "
                   "Algorithm failed to detect {hazard} in {conditions}. "
                   "Resulted in {severity} injuries to {affected_count} people. "
                   "{organization} {response_action} and {regulatory_response}."
    },
]

# Variable pools for template filling
ORGANIZATIONS = [
    "Meta", "Google", "Amazon", "Microsoft", "IBM", "Apple", "Tesla", "OpenAI",
    "Clearview AI", "Palantir", "Axon", "Verkada", "Clearview", "PredPol Inc",
    "HireVue", "Pymetrics", "Cognism", "ZestFinance", "Upstart", "LendingClub"
]

AFFECTED_GROUPS = [
    "women", "people of color", "Black individuals", "Hispanic users",
    "LGBTQ+ individuals", "elderly users", "people with disabilities",
    "low-income communities", "minority groups", "non-native speakers",
    "immigrants", "young people", "darker-skinned women"
]

BASELINE_GROUPS = [
    "white males", "lighter-skinned users", "majority populations",
    "higher-income groups", "native speakers"
]

CONTEXTS = [
    "law enforcement contexts", "public spaces", "employment decisions",
    "credit assessments", "healthcare facilities", "educational institutions",
    "border controls", "airport security", "retail environments",
    "workplace monitoring", "social media platforms", "public transportation"
]

DATA_TYPES = [
    "biometric data", "personal data", "health records", "financial data",
    "location data", "behavioral data", "communication records",
    "biometric and personal data", "sensitive personal information"
]

DECISION_TYPES = [
    "automated decision-making", "semi-automated decisions",
    "fully automated processes", "algorithmic recommendations"
]

OVERSIGHT = [
    "no human oversight", "limited human review", "minimal human intervention",
    "inadequate oversight mechanisms"
]

RESPONSE_ACTIONS = [
    "disputed findings", "placed moratorium on system", "removed feature",
    "issued public apology", "updated algorithm", "provided no response",
    "denied allegations", "launched internal investigation",
    "suspended operations temporarily", "offered compensation to affected users"
]

DISCOVERY_METHODS = [
    "external audit", "media investigation", "user complaints",
    "regulatory inquiry", "academic research", "whistleblower report"
]

REGULATORY_RESPONSES = [
    "faced regulatory fines", "received cease and desist order",
    "underwent compliance review", "was subject to investigation",
    "settled class action lawsuit"
]

DISCRIMINATORY_FACTORS = [
    "demographic characteristics", "socioeconomic status", "geographic location",
    "historical biases in training data"
]

SERVICES = [
    "housing", "employment opportunities", "financial services",
    "government benefits", "educational programs"
]

PLATFORMS = [
    "social media platforms", "messaging apps", "video sharing sites",
    "online forums", "dark web markets"
]

ACCIDENT_TYPES = [
    "fatal collision", "pedestrian injury", "rear-end collision",
    "intersection accident"
]

HAZARDS = [
    "pedestrians", "emergency vehicles", "construction zones",
    "cyclists", "road obstacles"
]

CONDITIONS = [
    "low-light conditions", "adverse weather", "heavy traffic",
    "complex intersections"
]

SEVERITIES = [
    "fatal", "serious", "moderate", "minor"
]


def generate_incident(incident_id: int, template_idx: int = None) -> Dict:
    """Generate a single synthetic incident"""

    if template_idx is None:
        template_idx = random.randint(0, len(INCIDENT_TEMPLATES) - 1)

    template = INCIDENT_TEMPLATES[template_idx]

    # Select random system name from template options
    system_name = random.choice(template["system_names"])
    organization = random.choice(ORGANIZATIONS)
    year = random.randint(2015, 2024)

    # Build narrative from template
    narrative = template["template"].format(
        system=system_name,
        organization=organization,
        year=year,
        affected_group=random.choice(AFFECTED_GROUPS),
        baseline_group=random.choice(BASELINE_GROUPS),
        error_rate=random.randint(15, 45),
        context=random.choice(CONTEXTS),
        data_types=random.choice(DATA_TYPES),
        decision_type=random.choice(DECISION_TYPES),
        oversight=random.choice(OVERSIGHT),
        response_action=random.choice(RESPONSE_ACTIONS),
        discovery_method=random.choice(DISCOVERY_METHODS),
        regulatory_response=random.choice(REGULATORY_RESPONSES),
        affected_count=random.randint(100, 100000),
        discriminatory_factors=random.choice(DISCRIMINATORY_FACTORS),
        services=random.choice(SERVICES),
        platform=random.choice(PLATFORMS),
        accident_type=random.choice(ACCIDENT_TYPES),
        hazard=random.choice(HAZARDS),
        conditions=random.choice(CONDITIONS),
        severity=random.choice(SEVERITIES),
        data_volume="sensitive personal data"
    )

    return {
        "id": f"BENCH-{incident_id:04d}",
        "narrative": narrative,
        "source": "Synthetic Benchmark",
        "metadata": {
            "benchmark_id": incident_id,
            "template_type": template["incident_type"],
            "system_type": template["system_type"],
            "purpose": template["purpose"],
            "generated_year": year,
            "organization": organization
        }
    }


def generate_benchmark_dataset(n_incidents: int = 100) -> List[Dict]:
    """Generate benchmark dataset with diverse incidents"""

    incidents = []

    # Ensure we have good coverage of all template types
    templates_per_type = n_incidents // len(INCIDENT_TEMPLATES)

    incident_id = 1
    for template_idx in range(len(INCIDENT_TEMPLATES)):
        for _ in range(templates_per_type):
            incidents.append(generate_incident(incident_id, template_idx))
            incident_id += 1

    # Fill remaining with random templates
    while len(incidents) < n_incidents:
        incidents.append(generate_incident(incident_id))
        incident_id += 1

    # Shuffle to randomize order
    random.shuffle(incidents)

    return incidents


if __name__ == "__main__":
    # Generate 100 incidents
    print("Generating 100 synthetic AI incidents...")
    incidents = generate_benchmark_dataset(100)

    # Save to JSON
    output_file = "benchmark_incidents.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(incidents, f, indent=2, ensure_ascii=False)

    print(f"✓ Generated {len(incidents)} incidents")
    print(f"✓ Saved to: {output_file}")

    # Print statistics
    template_counts = {}
    for incident in incidents:
        t = incident["metadata"]["template_type"]
        template_counts[t] = template_counts.get(t, 0) + 1

    print("\nIncident type distribution:")
    for incident_type, count in sorted(template_counts.items()):
        print(f"  {incident_type}: {count}")
