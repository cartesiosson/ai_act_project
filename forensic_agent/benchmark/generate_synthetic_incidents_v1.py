"""
Generate synthetic AI incidents for benchmark testing - Version 1
Based on AIAAIC database patterns

Changes from original:
- Added transparency_failure templates (3 new)
- Added privacy_violation templates (2 new)
- Added MinimalRisk cases (2 new)
- Added Appropriation template (1 new)
- Added Copyright template (1 new)
- Reduced bias proportion
- Better distribution reflecting real-world incidents
"""

import json
import random
from typing import List, Dict

# Incident templates based on real AIAAIC patterns
# Reorganized for better distribution
INCIDENT_TEMPLATES = [
    # === PRIVACY VIOLATIONS (5 templates) ===

    # 1. Data Breach / Privacy Violation
    {
        "system_names": ["ChatAI", "PersonalAssist", "DataCollect", "UserTrack", "AnalyticsBot"],
        "system_type": "nlp",
        "purpose": "PersonalAssistant",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "template": "{system} exposed {data_types} of {affected_count} users in {year}. "
                   "Security vulnerability allowed unauthorized access to conversation histories. "
                   "System processed {data_volume} without adequate safeguards. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 2. Emotion Recognition Misuse
    {
        "system_names": ["EmotionAI", "MoodDetect", "FeelingTrack", "AffectAnalyze", "EmotionScan"],
        "system_type": "vision",
        "purpose": "EmotionRecognition",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "template": "{system} emotion recognition system deployed without consent in {context} in {year}. "
                   "Monitored {affected_group} processing {data_types}. "
                   "Used for {decision_type} with {oversight}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 3. Location Tracking Privacy (NEW)
    {
        "system_names": ["LocationTrack", "GeoSpy", "MoveMonitor", "PathTrace", "WhereAI"],
        "system_type": "tabular",
        "purpose": "SurveillanceMonitoring",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "template": "{system} location tracking system collected data from {affected_count} users without proper consent in {year}. "
                   "The system tracked movements across {context} storing {data_types}. "
                   "Data was shared with third parties without user knowledge. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 4. Biometric Data Collection (NEW)
    {
        "system_names": ["FaceLog", "BiometricStore", "IdentityVault", "FacePrint", "BioCollect"],
        "system_type": "vision",
        "purpose": "BiometricIdentification",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "template": "{system} collected biometric data from {affected_count} individuals without informed consent in {year}. "
                   "Facial images scraped from {platform} and stored indefinitely. "
                   "System used for {decision_type} in {context}. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 5. Voice Data Privacy (NEW)
    {
        "system_names": ["VoiceAssist", "SpeakAI", "AudioLog", "VoiceCapture", "ListenBot"],
        "system_type": "nlp",
        "purpose": "PersonalAssistant",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "template": "{system} voice assistant recorded and stored private conversations of {affected_count} users in {year}. "
                   "Audio data processed by human contractors without user awareness. "
                   "Recordings included {data_types} shared in private settings. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # === TRANSPARENCY FAILURES (3 templates - NEW) ===

    # 6. Algorithmic Opacity
    {
        "system_names": ["DecisionAI", "AutoDecide", "AlgoSystem", "SmartChoice", "AIDecider"],
        "system_type": "tabular",
        "purpose": "PublicServiceAllocation",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "template": "{system} automated decision system operated without explanation capabilities in {year}. "
                   "Affected {affected_count} individuals denied {services} with no rationale provided. "
                   "System lacked audit trails and decision logging required by regulations. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 7. Hidden AI Disclosure Failure
    {
        "system_names": ["ChatBot", "ConvoAI", "TalkAssist", "DialogueBot", "SpeakAI"],
        "system_type": "nlp",
        "purpose": "CustomerService",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "template": "{system} customer service AI failed to disclose its non-human nature in {year}. "
                   "{affected_count} users interacted believing they were communicating with humans. "
                   "Deployed in {context} violating AI disclosure requirements. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 8. Training Data Opacity
    {
        "system_names": ["DataAI", "TrainBot", "ModelGen", "LearnSystem", "AIBuilder"],
        "system_type": "multimodal",
        "purpose": "ContentGeneration",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "template": "{system} generative AI system failed to document training data sources in {year}. "
                   "Model trained on undisclosed datasets potentially containing {data_types}. "
                   "No transparency reports provided despite regulatory requirements. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # === BIAS (2 templates - reduced from original) ===

    # 9. Facial Recognition Bias
    {
        "system_names": ["FaceID", "RecogniTech", "VisionAI", "BiometricScan", "FaceMatch"],
        "system_type": "vision",
        "purpose": "BiometricIdentification",
        "incident_type": "bias",
        "risk_level": "HighRisk",
        "template": "{system} facial recognition system exhibited racial and gender bias in {year}. "
                   "The system misidentified {affected_group} at rates {error_rate}% higher than {baseline_group}. "
                   "Deployed in {context} with {decision_type}. {organization} {response_action}."
    },
    # 10. Search Algorithm Bias
    {
        "system_names": ["SearchAI", "QueryBot", "FinderAI", "ResultsEngine", "DiscoverAI"],
        "system_type": "nlp",
        "purpose": "ContentRecommendation",
        "incident_type": "bias",
        "risk_level": "HighRisk",
        "template": "{system} search algorithm showed systematic bias against {affected_group} content in {year}. "
                   "Results for {affected_group} were {error_rate}% less likely to appear in top positions. "
                   "Affected {affected_count} content creators and users. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # === DISCRIMINATION (2 templates - reduced from original) ===

    # 11. Hiring Discrimination
    {
        "system_names": ["HireBot", "TalentAI", "RecruitPro", "CVAnalyzer", "HiringAssistant"],
        "system_type": "nlp",
        "purpose": "EmploymentDecision",
        "incident_type": "discrimination",
        "risk_level": "HighRisk",
        "template": "{system} automated hiring system discriminated against {affected_group} in {year}. "
                   "Algorithm trained on historical data showing bias. Used for {context} with {decision_type}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 12. Credit Scoring Discrimination
    {
        "system_names": ["CreditAI", "LoanDecider", "FinanceScore", "RiskAnalyzer", "CreditBot"],
        "system_type": "tabular",
        "purpose": "CreditScoring",
        "incident_type": "discrimination",
        "risk_level": "HighRisk",
        "template": "{system} credit scoring algorithm discriminated against {affected_group} in {year}. "
                   "System denied loans at {error_rate}% higher rate for minority applicants. "
                   "Processed {data_types} with {decision_type}. {organization} {response_action}."
    },

    # === SAFETY FAILURES (3 templates) ===

    # 13. Healthcare AI Error
    {
        "system_names": ["MedAI", "DiagnosisBot", "HealthPredict", "PatientRisk", "ClinicalAI"],
        "system_type": "multimodal",
        "purpose": "HealthcareDecision",
        "incident_type": "safety_failure",
        "risk_level": "HighRisk",
        "template": "{system} diagnostic system made critical errors affecting {affected_count} patients in {year}. "
                   "Algorithm misdiagnosed {affected_group} due to training data bias. "
                   "Used in {context} for {decision_type}. {organization} {response_action}."
    },
    # 14. Autonomous Vehicle Accident
    {
        "system_names": ["AutoDrive", "SmartCar", "RoboDriver", "AutoPilot", "VehicleAI"],
        "system_type": "vision",
        "purpose": "AutonomousVehicle",
        "incident_type": "safety_failure",
        "risk_level": "HighRisk",
        "template": "{system} autonomous vehicle system caused {accident_type} in {year}. "
                   "Algorithm failed to detect {hazard} in {conditions}. "
                   "Resulted in {severity} injuries to {affected_count} people. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 15. Deepfake Safety Harm
    {
        "system_names": ["DeepFake", "SynthVoice", "VideoGen", "FaceSwap", "MediaSynth"],
        "system_type": "multimodal",
        "purpose": "ContentGeneration",
        "incident_type": "safety_failure",
        "risk_level": "HighRisk",
        "template": "{system} deepfake generation system misused to create non-consensual content in {year}. "
                   "Generated synthetic media of {affected_group} without consent. "
                   "Content spread on {platform} affecting {affected_count} individuals. "
                   "{organization} {response_action}."
    },

    # === APPROPRIATION (NEW) ===

    # 16. Data Appropriation
    {
        "system_names": ["DataScrape", "WebCrawlAI", "ContentMine", "InfoExtract", "HarvestBot"],
        "system_type": "nlp",
        "purpose": "ContentGeneration",
        "incident_type": "appropriation",
        "risk_level": "HighRisk",
        "template": "{system} AI training system scraped content from {affected_count} creators without authorization in {year}. "
                   "Data harvested from {platform} included copyrighted works and personal content. "
                   "Creators received no compensation or attribution. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # === COPYRIGHT (NEW) ===

    # 17. Copyright Infringement
    {
        "system_names": ["GenAI", "CreateBot", "ArtifactAI", "ContentGen", "ProduceAI"],
        "system_type": "multimodal",
        "purpose": "ContentGeneration",
        "incident_type": "copyright",
        "risk_level": "HighRisk",
        "template": "{system} generative AI produced content infringing copyrights of {affected_count} creators in {year}. "
                   "System reproduced substantial portions of copyrighted works without license. "
                   "Outputs distributed on {platform} causing economic harm to original creators. "
                   "{organization} {response_action} and {regulatory_response}."
    },

    # === MINIMAL RISK CASES (NEW) ===

    # 18. Spam Filter (Minimal Risk)
    {
        "system_names": ["SpamFilter", "JunkDetect", "MailSort", "InboxAI", "FilterBot"],
        "system_type": "nlp",
        "purpose": "EmailFiltering",
        "incident_type": "transparency_failure",
        "risk_level": "MinimalRisk",
        "template": "{system} email spam filter incorrectly classified {affected_count} legitimate emails as spam in {year}. "
                   "Users reported missing important communications due to overly aggressive filtering. "
                   "System lacked clear explanation for classification decisions. "
                   "{organization} {response_action}."
    },
    # 19. Game AI (Minimal Risk)
    {
        "system_names": ["GameAI", "PlayBot", "NPCBrain", "GameEngine", "EntertainAI"],
        "system_type": "multimodal",
        "purpose": "Entertainment",
        "incident_type": "bias",
        "risk_level": "MinimalRisk",
        "template": "{system} video game AI exhibited unexpected behavior patterns in {year}. "
                   "NPC characters showed {error_rate}% preference for certain player demographics. "
                   "Affected gameplay experience for {affected_count} players. "
                   "{organization} {response_action}."
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
    "online forums", "content sharing websites"
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
        "source": "Synthetic Benchmark v1",
        "metadata": {
            "benchmark_id": incident_id,
            "template_type": template["incident_type"],
            "system_type": template["system_type"],
            "purpose": template["purpose"],
            "expected_risk_level": template["risk_level"],
            "generated_year": year,
            "organization": organization
        }
    }


def generate_benchmark_dataset(n_incidents: int = 100) -> List[Dict]:
    """
    Generate benchmark dataset with improved distribution:
    - privacy_violation: ~25% (5 templates)
    - transparency_failure: ~15% (3 templates)
    - safety_failure: ~15% (3 templates)
    - discrimination: ~10% (2 templates)
    - bias: ~10% (2 templates)
    - appropriation: ~5% (1 template)
    - copyright: ~5% (1 template)
    - minimal_risk: ~10% (2 templates)
    """

    incidents = []
    incident_id = 1

    # Define distribution (template indices and counts)
    # Total: 19 templates
    distribution = {
        # Privacy violations (templates 0-4): 25 cases
        "privacy": (list(range(0, 5)), 25),
        # Transparency failures (templates 5-7): 15 cases
        "transparency": (list(range(5, 8)), 15),
        # Bias (templates 8-9): 10 cases
        "bias": (list(range(8, 10)), 10),
        # Discrimination (templates 10-11): 10 cases
        "discrimination": (list(range(10, 12)), 10),
        # Safety failures (templates 12-14): 15 cases
        "safety": (list(range(12, 15)), 15),
        # Appropriation (template 15): 5 cases
        "appropriation": ([15], 5),
        # Copyright (template 16): 5 cases
        "copyright": ([16], 5),
        # Minimal risk (templates 17-18): 10 cases
        "minimal_risk": (list(range(17, 19)), 10),
    }

    for category, (template_indices, count) in distribution.items():
        for _ in range(count):
            template_idx = random.choice(template_indices)
            incidents.append(generate_incident(incident_id, template_idx))
            incident_id += 1

    # Fill remaining with random (if any)
    while len(incidents) < n_incidents:
        incidents.append(generate_incident(incident_id))
        incident_id += 1

    # Shuffle to randomize order
    random.shuffle(incidents)

    return incidents


if __name__ == "__main__":
    # Generate 100 incidents
    print("Generating 100 synthetic AI incidents (v1)...")
    incidents = generate_benchmark_dataset(100)

    # Save to JSON
    output_file = "benchmark_incidents_v1.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(incidents, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(incidents)} incidents")
    print(f"Saved to: {output_file}")

    # Print statistics
    template_counts = {}
    risk_counts = {}
    for incident in incidents:
        t = incident["metadata"]["template_type"]
        r = incident["metadata"]["expected_risk_level"]
        template_counts[t] = template_counts.get(t, 0) + 1
        risk_counts[r] = risk_counts.get(r, 0) + 1

    print("\nIncident type distribution:")
    for incident_type, count in sorted(template_counts.items()):
        print(f"  {incident_type}: {count}")

    print("\nRisk level distribution:")
    for risk_level, count in sorted(risk_counts.items()):
        print(f"  {risk_level}: {count}")
