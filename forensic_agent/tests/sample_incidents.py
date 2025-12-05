"""Sample incident narratives from AIAAIC database for testing"""

SAMPLE_INCIDENTS = {
    "facebook_deepface_2015": {
        "narrative": """
Facebook DeepFace facial recognition system generated racially biased alt text,
identifying Black individuals as primates in 2015. The incident was discovered through
user reports on social media. Facebook publicly apologized and removed the automatic
alt text generation feature. However, no systemic changes were made to training data
or bias detection mechanisms. The system processed biometric data at high volume in
public social media contexts with automated decision-making and no human oversight.
        """.strip(),
        "source": "AIAAIC",
        "metadata": {
            "incident_id": "AIAAIC-2015-FB-001",
            "reported_date": "2015",
            "organization": "Facebook (Meta)"
        }
    },

    "amazon_rekognition_2019": {
        "narrative": """
Amazon Rekognition facial recognition system exhibited significant racial and gender
bias in 2019 research study. The system misidentified women and people of color at
much higher rates than white males. Researchers found error rates up to 34% for
dark-skinned women compared to less than 1% for light-skinned males. The system
was being marketed to law enforcement agencies for identification in public spaces.
Amazon initially disputed findings but eventually placed a moratorium on police use.
The incident raised concerns about biometric identification systems deployed in
law enforcement contexts without adequate bias testing or human oversight.
        """.strip(),
        "source": "AIAAIC",
        "metadata": {
            "incident_id": "AIAAIC-2019-AMZN-001",
            "reported_date": "2019-01",
            "organization": "Amazon"
        }
    },

    "compas_recidivism_2016": {
        "narrative": """
COMPAS recidivism prediction algorithm used in US criminal justice system was found
to be racially biased in 2016 ProPublica investigation. The system predicted future
criminal behavior to inform sentencing and parole decisions. Analysis showed Black
defendants were falsely flagged as high-risk at nearly twice the rate of white
defendants (45% vs 23%). White defendants were more likely to be incorrectly labeled
low-risk. The proprietary algorithm operated as an automated decision-making system
with limited transparency and no meaningful human oversight. The system processed
personal data including criminal history, demographic information, and social factors.
Northpointe (now Equivant) disputed the findings but did not provide transparent
methodology. The incident had direct impact on thousands of individuals' freedom
and constitutional rights in a high-stakes law enforcement context.
        """.strip(),
        "source": "AIAAIC",
        "metadata": {
            "incident_id": "AIAAIC-2016-COMPAS-001",
            "reported_date": "2016-05",
            "organization": "Northpointe (Equivant)"
        }
    },

    "clearview_ai_privacy_2020": {
        "narrative": """
Clearview AI scraped over 3 billion images from social media platforms without
consent to build facial recognition database in 2020. The company sold access to
law enforcement agencies and private companies. The system operated by scraping
photos from Facebook, Instagram, Twitter, and other platforms, violating their
terms of service. Users had no knowledge their biometric data was being collected
and used. Multiple privacy violations were identified across jurisdictions.
Canadian, Australian, and European regulators issued orders to stop operations
and delete data. The incident involved unauthorized collection of biometric data,
lack of transparency, and deployment in law enforcement without proper legal basis
or human rights safeguards. Clearview initially refused to comply with deletion
orders. Class action lawsuits were filed in multiple jurisdictions. The incident
represents large-scale privacy violation affecting billions of individuals globally.
        """.strip(),
        "source": "AIAAIC",
        "metadata": {
            "incident_id": "AIAAIC-2020-CLVW-001",
            "reported_date": "2020-01",
            "organization": "Clearview AI"
        }
    },

    "chatgpt_personal_data_leak_2023": {
        "narrative": """
ChatGPT experienced a data breach in March 2023 that exposed users' chat history
titles and personal payment information. The bug in an open-source library allowed
some users to view other users' conversation histories and payment details including
names, email addresses, and partial credit card information. The incident affected
approximately 1.2% of ChatGPT Plus subscribers during a 9-hour window. OpenAI took
the system offline upon discovery and patched the vulnerability. The breach exposed
personal and financial data of thousands of users. OpenAI notified affected users
and offered mitigation measures. The incident occurred in a high-volume commercial
AI system processing sensitive personal data without adequate security controls.
Investigation revealed the data leakage was due to a caching library issue.
Regulatory inquiries were launched in Italy and other jurisdictions regarding
GDPR compliance and data protection measures.
        """.strip(),
        "source": "AIAAIC",
        "metadata": {
            "incident_id": "AIAAIC-2023-OPENAI-001",
            "reported_date": "2023-03",
            "organization": "OpenAI"
        }
    }
}


def get_incident(incident_key: str) -> dict:
    """
    Get a sample incident by key

    Args:
        incident_key: Key from SAMPLE_INCIDENTS

    Returns:
        Dictionary with narrative, source, and metadata
    """
    if incident_key not in SAMPLE_INCIDENTS:
        raise KeyError(f"Unknown incident: {incident_key}. Available: {list(SAMPLE_INCIDENTS.keys())}")

    return SAMPLE_INCIDENTS[incident_key]


def get_all_incidents() -> list:
    """
    Get all sample incidents

    Returns:
        List of incident dictionaries
    """
    return list(SAMPLE_INCIDENTS.values())


def get_incident_keys() -> list:
    """
    Get all available incident keys

    Returns:
        List of incident keys
    """
    return list(SAMPLE_INCIDENTS.keys())
