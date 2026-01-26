"""
Generate synthetic AI incidents for benchmark testing - Version 2
Aligned with AIAAIC Repository real distribution (n=2,132)

Distribution based on AIAAIC Issue(s) field analysis:
- Transparency: 34.8%
- Accuracy/Reliability: 33.1%
- Privacy/Surveillance: 23.7%
- Safety: 22.6%
- Fairness (Bias): 19.9%
- Accountability: 19.0%
- Mis/disinformation: 16.3%
- Security: 9.2%
- Copyright: 7.5%
- Employment: 6.9%

Note: Percentages sum >100% because incidents can have multiple issues.
For benchmark, we normalize to 100% using primary issue assignment.

v2.1 Changes (2026-01-11):
- Added model_scale to templates (FoundationModel, Large, Medium, Small)
- Added jurisdiction to templates (EU, US, Global)
- Narratives now include explicit mentions of automated decision-making
- Ground truth metadata includes all fields required by SystemProperties model
"""

import json
import random
from typing import List, Dict

# =============================================================================
# NEW: Model scale and jurisdiction pools for complete extraction
# =============================================================================

MODEL_SCALES = ["FoundationModel", "Large", "Medium", "Small"]
MODEL_SCALE_WEIGHTS = [0.15, 0.35, 0.35, 0.15]  # Weighted distribution

JURISDICTIONS = ["EU", "US", "Global"]
JURISDICTION_WEIGHTS = [0.4, 0.3, 0.3]  # Favor EU for AI Act relevance

# =============================================================================
# INCIDENT TEMPLATES - Organized by AIAAIC Issue Categories
# =============================================================================

INCIDENT_TEMPLATES = [
    # =========================================================================
    # TRANSPARENCY (34.8% in AIAAIC) - Templates 0-5
    # =========================================================================

    # 0. Algorithmic Opacity - Public Services
    {
        "system_names": ["DecisionAI", "AutoDecide", "AlgoSystem", "SmartChoice", "AIDecider"],
        "system_type": "tabular",
        "purpose": "PublicServiceAllocation",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale AI system, operated as a fully automated decision-making system without explanation capabilities in {year}. "
                   "Deployed in {jurisdiction} jurisdiction, the system affected {affected_count} individuals denied {services} with no rationale provided. "
                   "The automated system lacked audit trails and decision logging required by regulations. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 1. Hidden AI Disclosure Failure
    {
        "system_names": ["ChatBot", "ConvoAI", "TalkAssist", "DialogueBot", "AssistBot"],
        "system_type": "nlp",
        "purpose": "CustomerService",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale language model, failed to disclose its non-human nature in {year}. "
                   "{affected_count} users in {jurisdiction} interacted believing they were communicating with humans. "
                   "The automated AI system was deployed in {context} violating AI disclosure requirements. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 2. Training Data Opacity
    {
        "system_names": ["DataAI", "TrainBot", "ModelGen", "LearnSystem", "AIBuilder"],
        "system_type": "multimodal",
        "purpose": "ContentGeneration",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale generative AI system operating in {jurisdiction}, failed to document training data sources in {year}. "
                   "The automated model trained on undisclosed datasets potentially containing {data_types}. "
                   "No transparency reports provided despite regulatory requirements. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 3. Black Box Healthcare Decision
    {
        "system_names": ["HealthScore", "PatientRank", "CareAI", "MedDecide", "TriageBot"],
        "system_type": "tabular",
        "purpose": "HealthcareDecision",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale healthcare AI deployed in {jurisdiction}, provided no explanations for its automated decisions in {year}. "
                   "Patients and doctors could not understand why {affected_count} cases were deprioritized. "
                   "The fully automated system operated as black box in {context}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 4. Opaque Credit Decision
    {
        "system_names": ["CreditScore", "LoanAI", "FinDecide", "RiskBot", "ApprovalAI"],
        "system_type": "tabular",
        "purpose": "CreditScoring",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale automated credit scoring system in {jurisdiction}, denied {affected_count} applications without explanation in {year}. "
                   "Applicants received no information about factors affecting their scores. "
                   "The automated system processed {data_types} with {decision_type}. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 5. Undisclosed AI Content
    {
        "system_names": ["ContentAI", "WriteBot", "ArticleGen", "NewsAI", "TextPro"],
        "system_type": "nlp",
        "purpose": "ContentGeneration",
        "incident_type": "transparency_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale language model, published AI-generated content without disclosure in {year}. "
                   "{affected_count} articles distributed as human-written content in {jurisdiction}. "
                   "Readers unaware of automated AI involvement in {context}. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # =========================================================================
    # ACCURACY/RELIABILITY (33.1% in AIAAIC) - Templates 6-11
    # =========================================================================

    # 6. Facial Recognition Misidentification
    {
        "system_names": ["FaceMatch", "IDVerify", "RecogAI", "FaceScan", "IdentityCheck"],
        "system_type": "vision",
        "purpose": "BiometricIdentification",
        "incident_type": "accuracy_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale biometric AI system deployed in {jurisdiction}, misidentified {affected_count} individuals in {year}. "
                   "The automated facial recognition led to wrongful detentions in {context}. "
                   "System accuracy for {affected_group} was {error_rate}% lower than claimed. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 7. Medical Diagnosis Error
    {
        "system_names": ["DiagnosAI", "MedScan", "HealthDetect", "ClinicalAI", "PathologyBot"],
        "system_type": "multimodal",
        "purpose": "HealthcareDecision",
        "incident_type": "accuracy_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale medical AI operating in {jurisdiction}, produced incorrect automated diagnoses for {affected_count} patients in {year}. "
                   "Misdiagnosis rate was {error_rate}% higher than manufacturer claims. "
                   "Errors occurred primarily for {affected_group} in {context}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 8. Predictive Policing Errors
    {
        "system_names": ["PredPol", "CrimePredict", "SafetyAI", "PatrolBot", "RiskMap"],
        "system_type": "tabular",
        "purpose": "LawEnforcementSupport",
        "incident_type": "accuracy_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale predictive policing AI in {jurisdiction}, generated unreliable automated predictions in {year}. "
                   "False positive rate of {error_rate}% led to over-policing of {affected_group} communities. "
                   "The automated system deployed in {context} with {oversight}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 9. Autonomous Vehicle Perception Failure
    {
        "system_names": ["AutoDrive", "VisionDrive", "PerceptAI", "DriveBot", "RoadSense"],
        "system_type": "vision",
        "purpose": "AutonomousVehicle",
        "incident_type": "accuracy_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale autonomous driving AI deployed in {jurisdiction}, failed to correctly detect {hazard} in {year}. "
                   "The automated perception system error rate increased {error_rate}% in {conditions}. "
                   "Incident affected {affected_count} road users. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 10. Content Moderation Errors
    {
        "system_names": ["ModerateAI", "ContentCheck", "SafePost", "FilterBot", "ReviewAI"],
        "system_type": "nlp",
        "purpose": "ContentModeration",
        "incident_type": "accuracy_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale content moderation AI in {jurisdiction}, incorrectly flagged {affected_count} legitimate posts through automated decisions in {year}. "
                   "False positive rate for {affected_group} content was {error_rate}% higher. "
                   "Appeals process inadequate with {oversight}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 11. Translation AI Errors
    {
        "system_names": ["TranslateAI", "LangBot", "InterpreAI", "SpeechConvert", "LinguaAI"],
        "system_type": "nlp",
        "purpose": "Translation",
        "incident_type": "accuracy_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale translation AI deployed in {jurisdiction}, produced critical automated translation errors in {context} in {year}. "
                   "Mistranslations affected {affected_count} users with {error_rate}% error rate. "
                   "Errors particularly severe for {affected_group} languages. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # =========================================================================
    # PRIVACY/SURVEILLANCE (23.7% in AIAAIC) - Templates 12-16
    # =========================================================================

    # 12. Mass Surveillance
    {
        "system_names": ["WatchAI", "SurveilBot", "MonitorAll", "TrackSystem", "ObserveAI"],
        "system_type": "vision",
        "purpose": "SurveillanceMonitoring",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale surveillance AI deployed in {jurisdiction}, automatically collected data on {affected_count} individuals without consent in {year}. "
                   "Automated facial recognition deployed in {context} capturing {data_types}. "
                   "No legal basis established for automated data collection. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 13. Voice Assistant Privacy
    {
        "system_names": ["VoiceAssist", "SpeakAI", "AudioLog", "ListenBot", "VoiceCapture"],
        "system_type": "nlp",
        "purpose": "PersonalAssistant",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale voice AI operating in {jurisdiction}, automatically recorded private conversations of {affected_count} users in {year}. "
                   "Audio data processed by contractors without user awareness. "
                   "The automated system captured recordings including {data_types} from private settings. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 14. Location Tracking
    {
        "system_names": ["LocationTrack", "GeoSpy", "MoveMonitor", "PathTrace", "WhereAI"],
        "system_type": "tabular",
        "purpose": "SurveillanceMonitoring",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale tracking AI in {jurisdiction}, automatically collected movement data from {affected_count} users without consent in {year}. "
                   "The automated system tracked users across {context} storing {data_types}. "
                   "Data shared with third parties without user knowledge. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 15. Biometric Data Scraping
    {
        "system_names": ["FaceLog", "BiometricStore", "IdentityVault", "FacePrint", "BioCollect"],
        "system_type": "vision",
        "purpose": "BiometricIdentification",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale biometric AI deployed in {jurisdiction}, automatically collected biometric data from {affected_count} individuals without consent in {year}. "
                   "Facial images scraped from {platform} and stored indefinitely. "
                   "The automated system used for {decision_type} in {context}. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 16. Employee Monitoring
    {
        "system_names": ["WorkWatch", "EmployeeTrack", "ProductivityAI", "StaffMonitor", "WorkerSense"],
        "system_type": "multimodal",
        "purpose": "WorkforceMonitoring",
        "incident_type": "privacy_violation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale workplace AI in {jurisdiction}, automatically tracked {affected_count} workers without proper notice in {year}. "
                   "The automated system captured {data_types} including keystrokes and screen activity. "
                   "Deployed in {context} with {oversight}. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # =========================================================================
    # SAFETY (22.6% in AIAAIC) - Templates 17-21
    # =========================================================================

    # 17. Autonomous Vehicle Accident
    {
        "system_names": ["AutoPilot", "SmartDrive", "RoboCar", "SelfDrive", "VehicleAI"],
        "system_type": "vision",
        "purpose": "AutonomousVehicle",
        "incident_type": "safety_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale autonomous driving AI deployed in {jurisdiction}, caused {accident_type} in {year}. "
                   "The automated algorithm failed to detect {hazard} in {conditions}. "
                   "Resulted in {severity} injuries to {affected_count} people. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 18. Medical Device Malfunction
    {
        "system_names": ["MedDevice", "HealthBot", "CareAI", "TreatmentAI", "TherapyBot"],
        "system_type": "tabular",
        "purpose": "HealthcareDecision",
        "incident_type": "safety_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale medical AI operating in {jurisdiction}, malfunctioned affecting {affected_count} patients in {year}. "
                   "The automated system provided incorrect dosage recommendations with {error_rate}% error rate. "
                   "Used in {context} for {decision_type}. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 19. Industrial Robot Injury
    {
        "system_names": ["RoboWorker", "FactoryAI", "AutoArm", "IndustrialBot", "ManufactureAI"],
        "system_type": "vision",
        "purpose": "IndustrialAutomation",
        "incident_type": "safety_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale industrial AI deployed in {jurisdiction}, caused workplace injury to {affected_count} workers in {year}. "
                   "The automated safety system failed to detect human presence in {conditions}. "
                   "Incident occurred in {context} with {oversight}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 20. Drone Incident
    {
        "system_names": ["DroneAI", "FlyBot", "AerialAI", "SkyDrone", "AutoFly"],
        "system_type": "vision",
        "purpose": "AutonomousVehicle",
        "incident_type": "safety_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale autonomous drone AI in {jurisdiction}, caused incident affecting {affected_count} people in {year}. "
                   "The automated navigation system failed in {conditions} near {context}. "
                   "Resulted in {severity} damage and injuries. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 21. Chatbot Harmful Advice
    {
        "system_names": ["AdviceBot", "CounselAI", "HelpChat", "SupportAI", "GuidanceBot"],
        "system_type": "nlp",
        "purpose": "MentalHealthSupport",
        "incident_type": "safety_failure",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale mental health AI deployed in {jurisdiction}, provided harmful automated advice to {affected_count} vulnerable users in {year}. "
                   "The automated system failed to recognize crisis situations in {context}. "
                   "Responses potentially endangered {affected_group}. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # =========================================================================
    # FAIRNESS/BIAS (19.9% in AIAAIC) - Templates 22-25
    # =========================================================================

    # 22. Hiring Algorithm Bias
    {
        "system_names": ["HireBot", "TalentAI", "RecruitPro", "CVAnalyzer", "HiringAssistant"],
        "system_type": "nlp",
        "purpose": "EmploymentDecision",
        "incident_type": "bias",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale hiring AI deployed in {jurisdiction}, discriminated against {affected_group} through automated decisions in {year}. "
                   "The automated system rejected qualified candidates at {error_rate}% higher rate. "
                   "Algorithm trained on biased historical data for {context}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 23. Facial Recognition Racial Bias
    {
        "system_names": ["FaceID", "RecogniTech", "VisionAI", "BiometricScan", "FaceMatch"],
        "system_type": "vision",
        "purpose": "BiometricIdentification",
        "incident_type": "bias",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale biometric AI operating in {jurisdiction}, exhibited racial bias in automated identifications in {year}. "
                   "The automated system misidentified {affected_group} at rates {error_rate}% higher than {baseline_group}. "
                   "Deployed in {context} with {decision_type}. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 24. Credit Scoring Bias
    {
        "system_names": ["CreditAI", "LoanDecider", "FinanceScore", "RiskAnalyzer", "CreditBot"],
        "system_type": "tabular",
        "purpose": "CreditScoring",
        "incident_type": "bias",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale credit AI in {jurisdiction}, showed bias against {affected_group} in automated credit decisions in {year}. "
                   "The automated system denied applications at {error_rate}% higher rate for equivalent profiles. "
                   "System processed {data_types} with {decision_type}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 25. Healthcare Algorithm Bias
    {
        "system_names": ["HealthRisk", "PatientScore", "CarePredict", "MedRank", "TreatmentAI"],
        "system_type": "tabular",
        "purpose": "HealthcareDecision",
        "incident_type": "bias",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale healthcare AI deployed in {jurisdiction}, systematically disadvantaged {affected_group} through automated decisions in {year}. "
                   "Automated risk scores for {affected_group} were {error_rate}% less accurate. "
                   "Led to delayed care for {affected_count} patients. "
                   "{organization} {response_action} after {discovery_method}."
    },

    # =========================================================================
    # MIS/DISINFORMATION (16.3% in AIAAIC) - Templates 26-29
    # =========================================================================

    # 26. Deepfake Political Content
    {
        "system_names": ["DeepFake", "SynthMedia", "FakeGen", "VideoForge", "MediaSynth"],
        "system_type": "multimodal",
        "purpose": "ContentGeneration",
        "incident_type": "misinformation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale generative AI system operating in {jurisdiction}, automatically generated deepfake political content that spread to {affected_count} viewers in {year}. "
                   "The automated synthetic media falsely depicted public figures in {context}. "
                   "Content spread on {platform} before detection. "
                   "{organization} {response_action} and {regulatory_response}."
    },
    # 27. AI-Generated Fake News
    {
        "system_names": ["NewsGen", "ArticleBot", "ContentAI", "WriteBot", "StoryForge"],
        "system_type": "nlp",
        "purpose": "ContentGeneration",
        "incident_type": "misinformation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale language model deployed in {jurisdiction}, automatically generated fake news articles viewed by {affected_count} people in {year}. "
                   "The automated AI-created content mimicked legitimate journalism in {context}. "
                   "Disinformation spread on {platform} affecting public discourse. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 28. Chatbot Hallucinations
    {
        "system_names": ["ChatAI", "ConvoBot", "TalkGPT", "DialogueAI", "AssistChat"],
        "system_type": "nlp",
        "purpose": "InformationRetrieval",
        "incident_type": "misinformation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale conversational AI operating in {jurisdiction}, automatically generated false information for {affected_count} users in {year}. "
                   "The automated system hallucinated facts about {context} with high confidence. "
                   "Users relied on incorrect automated information for {decision_type}. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 29. Synthetic Audio Scam
    {
        "system_names": ["VoiceClone", "AudioGen", "SpeechSynth", "VoiceForge", "SoundAI"],
        "system_type": "nlp",
        "purpose": "ContentGeneration",
        "incident_type": "misinformation",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale voice synthesis AI deployed in {jurisdiction}, was used to automatically impersonate executives defrauding {affected_count} in {year}. "
                   "The automated synthetic audio enabled fraudulent wire transfers in {context}. "
                   "Victims lost significant funds before detection. "
                   "{organization} {response_action} and {regulatory_response}."
    },

    # =========================================================================
    # COPYRIGHT (7.5% in AIAAIC) - Templates 30-31
    # =========================================================================

    # 30. Training Data Copyright
    {
        "system_names": ["DataScrape", "WebCrawlAI", "ContentMine", "TrainHarvest", "DataCollect"],
        "system_type": "nlp",
        "purpose": "ContentGeneration",
        "incident_type": "copyright",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale generative AI operating in {jurisdiction}, was trained on copyrighted content from {affected_count} creators without authorization in {year}. "
                   "Automated data harvesting from {platform} included protected works. "
                   "Creators received no compensation or attribution. "
                   "{organization} {response_action} after {discovery_method}."
    },
    # 31. Generated Content Infringement
    {
        "system_names": ["GenAI", "CreateBot", "ArtifactAI", "ContentGen", "ProduceAI"],
        "system_type": "multimodal",
        "purpose": "ContentGeneration",
        "incident_type": "copyright",
        "risk_level": "HighRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale generative AI deployed in {jurisdiction}, automatically reproduced copyrighted works affecting {affected_count} creators in {year}. "
                   "Automated outputs substantially similar to protected content. "
                   "Distributed on {platform} causing economic harm. "
                   "{organization} {response_action} and {regulatory_response}."
    },

    # =========================================================================
    # MINIMAL RISK (for scope testing) - Templates 32-33
    # =========================================================================

    # 32. Spam Filter
    {
        "system_names": ["SpamFilter", "JunkDetect", "MailSort", "InboxAI", "FilterBot"],
        "system_type": "nlp",
        "purpose": "EmailFiltering",
        "incident_type": "accuracy_failure",
        "risk_level": "MinimalRisk",
        "is_automated_decision": True,
        "template": "{system}, a {model_scale}-scale email AI deployed in {jurisdiction}, incorrectly classified {affected_count} legitimate emails through automated filtering in {year}. "
                   "Users reported missing important communications. "
                   "The automated system lacked clear explanation for decisions. "
                   "{organization} {response_action}."
    },
    # 33. Game AI
    {
        "system_names": ["GameAI", "PlayBot", "NPCBrain", "GameEngine", "EntertainAI"],
        "system_type": "multimodal",
        "purpose": "Entertainment",
        "incident_type": "bias",
        "risk_level": "MinimalRisk",
        "is_automated_decision": False,
        "template": "{system}, a {model_scale}-scale game AI operating in {jurisdiction}, exhibited unexpected automated behavior in {year}. "
                   "NPC characters showed preference patterns affecting {affected_count} players. "
                   "Gameplay experience impacted but no real-world harm from this entertainment system. "
                   "{organization} {response_action}."
    },
]

# =============================================================================
# Variable pools for template filling
# =============================================================================

ORGANIZATIONS = [
    "Meta", "Google", "Amazon", "Microsoft", "IBM", "Apple", "Tesla", "OpenAI",
    "Clearview AI", "Palantir", "Axon", "ByteDance", "Alibaba", "Baidu",
    "HireVue", "Pymetrics", "ZestFinance", "Upstart", "SenseTime", "Megvii"
]

AFFECTED_GROUPS = [
    "women", "people of color", "Black individuals", "Hispanic users",
    "LGBTQ+ individuals", "elderly users", "people with disabilities",
    "low-income communities", "minority groups", "non-native speakers",
    "immigrants", "young people", "darker-skinned individuals"
]

BASELINE_GROUPS = [
    "white males", "lighter-skinned users", "majority populations",
    "higher-income groups", "native speakers"
]

CONTEXTS = [
    "law enforcement", "public spaces", "employment screening",
    "credit assessment", "healthcare facilities", "educational institutions",
    "border control", "airport security", "retail environments",
    "workplace settings", "social media", "public transportation"
]

DATA_TYPES = [
    "biometric data", "personal data", "health records", "financial data",
    "location data", "behavioral data", "communication records",
    "sensitive personal information", "facial images"
]

DECISION_TYPES = [
    "automated decision-making", "semi-automated decisions",
    "fully automated processes", "algorithmic recommendations"
]

OVERSIGHT = [
    "no human oversight", "limited human review", "minimal intervention",
    "inadequate oversight mechanisms"
]

RESPONSE_ACTIONS = [
    "disputed findings", "placed moratorium on system", "removed feature",
    "issued public apology", "updated algorithm", "provided no response",
    "denied allegations", "launched internal investigation",
    "suspended operations", "offered compensation"
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

SERVICES = [
    "housing", "employment opportunities", "financial services",
    "government benefits", "educational programs", "healthcare access"
]

PLATFORMS = [
    "social media platforms", "messaging apps", "video sharing sites",
    "online forums", "news websites", "e-commerce sites"
]

ACCIDENT_TYPES = [
    "fatal collision", "pedestrian injury", "multi-vehicle accident",
    "intersection collision", "highway incident"
]

HAZARDS = [
    "pedestrians", "emergency vehicles", "construction zones",
    "cyclists", "road obstacles", "other vehicles"
]

CONDITIONS = [
    "low-light conditions", "adverse weather", "heavy traffic",
    "complex intersections", "construction areas"
]

SEVERITIES = ["fatal", "serious", "moderate", "minor"]


def generate_incident(incident_id: int, template_idx: int = None) -> Dict:
    """Generate a single synthetic incident"""

    if template_idx is None:
        template_idx = random.randint(0, len(INCIDENT_TEMPLATES) - 1)

    template = INCIDENT_TEMPLATES[template_idx]

    system_name = random.choice(template["system_names"])
    organization = random.choice(ORGANIZATIONS)
    year = random.randint(2018, 2025)

    # NEW: Generate model_scale and jurisdiction for complete extraction
    model_scale = random.choices(MODEL_SCALES, weights=MODEL_SCALE_WEIGHTS)[0]
    jurisdiction = random.choices(JURISDICTIONS, weights=JURISDICTION_WEIGHTS)[0]
    is_automated_decision = template.get("is_automated_decision", True)

    narrative = template["template"].format(
        system=system_name,
        organization=organization,
        year=year,
        model_scale=model_scale,
        jurisdiction=jurisdiction,
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
        services=random.choice(SERVICES),
        platform=random.choice(PLATFORMS),
        accident_type=random.choice(ACCIDENT_TYPES),
        hazard=random.choice(HAZARDS),
        conditions=random.choice(CONDITIONS),
        severity=random.choice(SEVERITIES)
    )

    return {
        "id": f"BENCH-{incident_id:04d}",
        "narrative": narrative,
        "source": "Synthetic Benchmark v2.1 (AIAAIC-aligned)",
        "metadata": {
            "benchmark_id": incident_id,
            "template_type": template["incident_type"],
            "system_type": template["system_type"],
            "purpose": template["purpose"],
            "expected_risk_level": template["risk_level"],
            "generated_year": year,
            "organization": organization,
            # NEW: Complete ground truth for all required SystemProperties fields
            "expected_model_scale": model_scale,
            "expected_jurisdiction": jurisdiction,
            "expected_is_automated_decision": is_automated_decision
        }
    }


def generate_benchmark_dataset(n_incidents: int = 50) -> List[Dict]:
    """
    Generate benchmark dataset aligned with AIAAIC distribution.

    Target distribution (normalized from AIAAIC):
    - Transparency: 18% (was 34.8%, normalized)
    - Accuracy/Reliability: 17% (was 33.1%)
    - Privacy/Surveillance: 12% (was 23.7%)
    - Safety: 12% (was 22.6%)
    - Fairness/Bias: 10% (was 19.9%)
    - Mis/disinformation: 8% (was 16.3%)
    - Copyright: 4% (was 7.5%)
    - Minimal Risk: 5% (for scope testing)

    Note: AIAAIC percentages sum to >100% due to multi-labeling.
    We normalize to 100% for single-label benchmark.
    """

    incidents = []
    incident_id = 1

    # Distribution for 50 cases (aligned with AIAAIC proportions)
    distribution = {
        # Transparency (templates 0-5): 18%
        "transparency": (list(range(0, 6)), int(n_incidents * 0.18)),
        # Accuracy/Reliability (templates 6-11): 17%
        "accuracy": (list(range(6, 12)), int(n_incidents * 0.17)),
        # Privacy/Surveillance (templates 12-16): 12%
        "privacy": (list(range(12, 17)), int(n_incidents * 0.12)),
        # Safety (templates 17-21): 12%
        "safety": (list(range(17, 22)), int(n_incidents * 0.12)),
        # Fairness/Bias (templates 22-25): 10%
        "bias": (list(range(22, 26)), int(n_incidents * 0.10)),
        # Mis/disinformation (templates 26-29): 8%
        "misinformation": (list(range(26, 30)), int(n_incidents * 0.08)),
        # Copyright (templates 30-31): 4%
        "copyright": (list(range(30, 32)), int(n_incidents * 0.04)),
        # Minimal Risk (templates 32-33): 5%
        "minimal_risk": (list(range(32, 34)), int(n_incidents * 0.05)),
    }

    for category, (template_indices, count) in distribution.items():
        for _ in range(count):
            template_idx = random.choice(template_indices)
            incidents.append(generate_incident(incident_id, template_idx))
            incident_id += 1

    # Fill remaining with random high-risk categories
    while len(incidents) < n_incidents:
        # Exclude minimal risk for remaining
        template_idx = random.randint(0, 31)
        incidents.append(generate_incident(incident_id, template_idx))
        incident_id += 1

    random.shuffle(incidents)
    return incidents


if __name__ == "__main__":
    print("Generating 50 synthetic AI incidents (v2.1 - AIAAIC-aligned with complete ground truth)...")
    incidents = generate_benchmark_dataset(50)

    output_file = "benchmark_incidents_v2.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(incidents, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(incidents)} incidents")
    print(f"Saved to: {output_file}")

    # Print statistics
    template_counts = {}
    risk_counts = {}
    model_scale_counts = {}
    jurisdiction_counts = {}
    for incident in incidents:
        t = incident["metadata"]["template_type"]
        r = incident["metadata"]["expected_risk_level"]
        m = incident["metadata"]["expected_model_scale"]
        j = incident["metadata"]["expected_jurisdiction"]
        template_counts[t] = template_counts.get(t, 0) + 1
        risk_counts[r] = risk_counts.get(r, 0) + 1
        model_scale_counts[m] = model_scale_counts.get(m, 0) + 1
        jurisdiction_counts[j] = jurisdiction_counts.get(j, 0) + 1

    print("\nIncident type distribution:")
    for incident_type, count in sorted(template_counts.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(incidents) * 100
        print(f"  {incident_type}: {count} ({pct:.1f}%)")

    print("\nRisk level distribution:")
    for risk_level, count in sorted(risk_counts.items()):
        pct = count / len(incidents) * 100
        print(f"  {risk_level}: {count} ({pct:.1f}%)")

    print("\nModel scale distribution:")
    for scale, count in sorted(model_scale_counts.items()):
        pct = count / len(incidents) * 100
        print(f"  {scale}: {count} ({pct:.1f}%)")

    print("\nJurisdiction distribution:")
    for jur, count in sorted(jurisdiction_counts.items()):
        pct = count / len(incidents) * 100
        print(f"  {jur}: {count} ({pct:.1f}%)")
