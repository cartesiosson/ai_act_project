# Feasibility Analysis: Forensic Compliance Agent with Llama 3.2 + Ontology + MCP SPARQL

## Executive Summary

**Question**: Can an SML agent with Llama 3.2, our EU AI Act ontology, and MCP SPARQL analyze real AI incidents from the AIAAIC database to determine compliance violations?

**Answer**: **✅ YES, with caveats and recommended enhancements**

The agent could perform **preliminary forensic analysis**, but would need **human expert review** for final enforcement decisions.

---

## What the Agent CAN Do Well

### 1. Extract System Properties from Incident Narratives

**Example Incident**: "Facebook's image recognition system misidentified Black men as 'primates'"

**Agent Process**:
```
Input (from incident narrative):
- System type: Image recognition (Computer Vision)
- Purpose: Content moderation / Automated decision
- Data type: Biometric (facial recognition)
- Affected population: All users (but bias against minorities)
- Harm: Discrimination, fundamental rights violation

↓

LLM Analysis (Llama 3.2):
1. Parse narrative for system properties
2. Identify EU AI Act relevance
3. Extract key characteristics

↓

Structured Output:
{
  "system_name": "Facebook Image Tagging System",
  "system_type": "Computer Vision / Facial Recognition",
  "primary_purpose": "Content Moderation",
  "secondary_purpose": "Automated User Categorization",
  "processes_data_type": ["BiometricData", "PersonalData"],
  "deployment_context": ["PublicSpaces", "HighVolume"],
  "affected_population": "All FB users (discriminatory impact on minorities)",
  "incident_type": "Discrimination / Bias",
  "year": 2015
}
```

**Assessment**: ⭐⭐⭐⭐⭐ **Excellent**
- Llama 3.2 is good at NLP extraction
- Can identify system types, purposes, data types
- Can recognize harmful outcomes from narratives

---

### 2. Query Ontology for Proper Classification

**Agent Process**:

```sparql
# Given extracted system properties, query ontology

SELECT ?criterion ?requirement ?label
WHERE {
  # System uses biometric facial recognition
  ai:BiometricIdentification ai:activatesCriterion ?criterion .

  # System deployed in public spaces at scale
  ai:PublicSpaces ai:triggersCriterion ?criterion .

  # System processes personal data
  ?criterion ai:activatesRequirement ?requirement .

  # Requirements related to discrimination/bias
  ?requirement ai:relatedTo ai:NonDiscriminationCriterion .

  ?requirement rdfs:label ?label .
}
```

**Result**:
```
Mandatory Requirements:
- BiometricSecurityRequirement
- FundamentalRightsAssessmentRequirement
- NonDiscriminationRequirement
- TransparencyRequirement
- HumanOversightRequirement
- DataGovernanceRequirement
```

**Assessment**: ⭐⭐⭐⭐⭐ **Excellent**
- Ontology queries are deterministic
- MCP SPARQL endpoint handles this perfectly
- Results are authoritative and reproducible

---

### 3. Identify Discrimination/Bias-Specific Requirements

**Agent Enhancement**: Custom queries for specific incident types

```sparql
# Query for bias-related requirements

SELECT ?requirement ?label
WHERE {
  # Find all discrimination-related criteria
  ?criterion a ai:Criterion ;
    rdfs:label ?criterionLabel .

  FILTER(CONTAINS(?criterionLabel, "Discrimin") ||
         CONTAINS(?criterionLabel, "Bias"))

  # Get their requirements
  ?criterion ai:activatesRequirement ?requirement .
  ?requirement rdfs:label ?label .
}
```

**Results for Facebook case**:
```
Discrimination/Bias Prevention:
- BiasDetectionRequirement
- FairnessEvaluationRequirement
- BiasMonitoringRequirement
- DiversityInTrainingDataRequirement
- AlgorithmicAuditRequirement
```

**Assessment**: ⭐⭐⭐⭐ **Very Good**
- Can identify specific requirement categories
- Supports incident-type-specific analysis
- May miss novel/emerging bias types

---

### 4. Detect Compliance Gaps

**Agent Process**:

```
System Claims (from FB in 2015):
- "We have content moderation guidelines"
- "We monitor for spam and abuse"

Mandatory Requirements:
✓ ContentModerationRequirement (implied by claims)
✗ BiasDetectionRequirement (NOT mentioned)
✗ FairnessEvaluationRequirement (NOT mentioned)
✗ DiversityInTrainingDataRequirement (NO EVIDENCE)
✗ BiasMonitoringRequirement (DISCOVERED AFTER INCIDENT)

Gap Analysis:
Missing 4/7 key requirements for facial recognition systems
```

**Assessment**: ⭐⭐⭐⭐ **Very Good**
- Can compare claims vs. mandatory requirements
- Highlights specific gaps
- Requires factual knowledge of what FB actually had

---

## What the Agent STRUGGLES With

### 1. Article 6(3) Residual Risk Identification

**Problem**: Article 6(3) requires **expert judgment** about "unforeseen risks"

```
Incident: Facebook bias (2015)
Question: Should this have been predictable under Article 6(3)?

Current Ontology Knowledge:
- Biometric systems have discrimination risks ✓
- Training data bias is a known issue ✓

But Article 6(3) is discretionary:
- "Unforeseen" risks (who can foresee what?)
- "Emerging threats" (what counts as emerging?)
- Requires regulatory judgment

Llama's Analysis:
"Given that facial recognition bias had been
 documented in prior academic literature,
 this was foreseeable and should have been
 flagged under Article 6(3)."

BUT: Who authorizes this judgment?
- Requires: Legal/regulatory expert review
- Cannot be fully automated
```

**Assessment**: ⭐⭐ **Difficult**
- LLM reasoning is uncertain for novel risk assessment
- Needs human regulatory expert approval
- Can flag *candidates* for Article 6(3), not determine

---

### 2. Exact System Classification at Incident Time

**Problem**: Incidents often lack precise technical details

```
Incident Narrative:
"Facebook's image recognition system"

Unknowns (crucial for classification):
- What model? (CNN, transformer, ensemble?)
- What training data? (Facebook's dataset only? COCO?)
- What exact version was deployed? (v2.3, v3.1?)
- What guardrails existed? (none mentioned)

Llama 3.2 Inferences:
"Probably a CNN based on 2015 technology level"
"Likely trained on user-generated content"

But these are guesses, not facts.

Ontology Query Accuracy:
- If classification is wrong → all derived requirements are wrong
```

**Assessment**: ⭐⭐⭐ **Moderate**
- Good for likely scenarios
- Poor for unusual/novel systems
- Needs technical documentation to be reliable

---

### 3. Timeline Reconstruction (Temporal Reasoning)

**Problem**: When should compliance have been achieved?

```
Incident Timeline:
- 2015: Bias discovered in Facebook system
- 2018: GDPR enters force
- 2024: EU AI Act enters force

Question: What were FB's obligations in 2015?
- GDPR didn't exist yet
- EU AI Act didn't exist
- No regulatory framework applied

Llama Analysis Challenge:
"In 2015, there were no EU regulations requiring
 this. But industry best practices suggested
 bias testing was necessary."

Problem:
- Retroactive analysis is hard
- Need historical regulatory context
- Ontology is current, not historical
```

**Assessment**: ⭐⭐ **Challenging**
- Temporal reasoning is weak in LLMs
- Requires explicit timeline data
- Good for post-EU AI Act incidents (2024+)

---

## Recommended MCP SPARQL Integration

### What the MCP Should Provide

```python
class ForensicSPARQLMCP:
    """
    MCP server for forensic analysis queries
    """

    def query_mandatory_requirements(self, purpose, context, data_types):
        """Given system properties, get all mandatory requirements"""
        # SPARQL query that Llama can call

    def query_incident_specific_requirements(self, incident_type):
        """Given incident type, get relevant requirements"""
        # e.g., "discrimination" → bias-related requirements

    def query_compliance_gap_analysis(self,
                                     mandatory_requirements,
                                     claimed_requirements):
        """Identify which requirements are missing"""

    def query_similar_incidents(self, system_type, incident_type):
        """Find other systems with same compliance gap"""

    def query_article_6_3_candidates(self, incident_characteristics):
        """Identify potential Article 6(3) violations"""
```

---

## Full Forensic Agent Workflow

### Phase 1: Incident Ingestion (LLM)
```
Input: Incident narrative from AIAAIC DB
↓
Llama 3.2 extracts:
- System name, type, purpose
- Data types processed
- Deployment context
- Harm type (discrimination, safety, privacy)
- Affected population
- Year/timeline
↓
Output: Structured incident data
```

### Phase 2: System Classification (Ontology)
```
Input: Extracted system properties
↓
MCP SPARQL queries:
1. What criteria should activate?
2. What requirements flow from those criteria?
3. What Article 6(3) risks apply?
↓
Output: Complete requirement list
```

### Phase 3: Gap Analysis (MCP + LLM)
```
Input:
- Mandatory requirements
- What system actually had (from narrative)

↓
Process:
1. LLM extracts claims from incident text
2. MCP compares against mandatory list
3. LLM explains gaps in enforcement language
↓
Output: Violation report with severity
```

### Phase 4: Expert Review (Human)
```
Input: Automated analysis
↓
Expert tasks:
1. Verify system classification accuracy
2. Assess Article 6(3) residual risks
3. Review temporal applicability
4. Determine enforcement severity
5. Identify systemic patterns
↓
Output: Final enforcement decision
```

---

## Capability Matrix

| Task | LLM | Ontology | MCP SPARQL | Human Expert |
|------|-----|----------|-----------|--------------|
| Extract incident properties | ⭐⭐⭐⭐⭐ | - | - | - |
| Classify system risk | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Identify requirements | - | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | - |
| Detect compliance gaps | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Article 6(3) judgment | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Timeline analysis | ⭐⭐ | - | - | ⭐⭐⭐⭐⭐ |
| Severity assessment | ⭐⭐⭐⭐ | - | - | ⭐⭐⭐⭐⭐ |
| Find systemic patterns | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Recommended Implementation: Hybrid Approach

```
┌─────────────────────────────────────────────────────┐
│         HYBRID FORENSIC ANALYSIS SYSTEM             │
└─────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ Layer 1: INCIDENT INGESTION (Llama 3.2)            │
│ ✓ Parse AIAAIC database entries                     │
│ ✓ Extract: system type, purpose, data, harm type   │
│ ✓ Confidence scoring for extractions               │
└──────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────┐
│ Layer 2: CLASSIFICATION (Ontology + MCP SPARQL)    │
│ ✓ Query mandatory requirements                      │
│ ✓ Identify compliance gaps                          │
│ ✓ Detect systemic patterns                          │
│ ✓ Flag Article 6(3) candidates                      │
└──────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────┐
│ Layer 3: ANALYSIS (LLM Reasoning)                   │
│ ✓ Explain violations in regulatory language        │
│ ✓ Calculate severity scores                         │
│ ✓ Generate audit trail                              │
│ ✓ Identify related cases                            │
└──────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────┐
│ Layer 4: EXPERT REVIEW (Human Oversight)            │
│ ✓ Verify accuracy of extraction                     │
│ ✓ Assess Article 6(3) judgment calls                │
│ ✓ Review temporal applicability                     │
│ ✓ Determine enforcement action                      │
│ ✓ Publish findings                                  │
└──────────────────────────────────────────────────────┘
```

---

## Real Example: Facebook Facial Recognition Case

### Incident (2015)
"Facebook's DeepFace system misidentified Black men as 'primates' in alt text"

### Agent Analysis

**Phase 1: Extraction (Llama)**
```json
{
  "system_name": "Facebook DeepFace",
  "system_type": "Computer Vision - Facial Recognition",
  "primary_purpose": "Image Tagging / Content Organization",
  "also_used_for": "Automated Alt Text Generation",
  "processes": ["BiometricData", "PersonalData", "ImageData"],
  "deployment": ["PublicSpaces", "HighVolume", "RealTimeProcessing"],
  "incident_type": "Discrimination - Racial Bias",
  "harm_level": "Fundamental Rights Violation",
  "year": 2015,
  "affected_population": "Millions of FB users",
  "confidence": 0.92
}
```

**Phase 2: Classification (MCP SPARQL)**
```
Query 1: What criteria should activate?
Result:
- BiometricIdentificationCriterion (facial recognition)
- AutomatedDecisionCriterion (alt text generation)
- HighVolumeCriterion (all FB users)

Query 2: What requirements?
Result:
- BiometricSecurityRequirement ✓
- FundamentalRightsAssessmentRequirement ✓
- NonDiscriminationRequirement ✓
- TransparencyRequirement ✓
- BiasDetectionRequirement ✓
- AuditabilityRequirement ✓
```

**Phase 3: Gap Analysis (LLM + MCP)**
```
From incident narrative:
- "Facebook had no specific bias testing protocol"
- "No diversity in training data mentioned"
- "Alt text generation was opaque to users"

Compliance Status:
✓ Implements basic content moderation
✓ Has some transparency (privacy policy)
✗ No BiasDetectionRequirement implementation
✗ No diverse training data evidence
✗ No BiasMonitoringRequirement
✗ No FundamentalRightsAssessment process

Gaps: 4/6 critical requirements missing

Root Cause: Missing BiasDetectionRequirement
- Led to training on biased datasets
- Resulted in discriminatory outputs
- Violated fundamental rights of minorities
```

**Phase 4: Expert Review (Human)**
```
✓ Classification verified: YES, facial recognition + automated decision
✓ Temporal: 2015 - pre-GDPR, pre-EU AI Act
   → Cannot apply EU AI Act directly
   → But demonstrates NEED for such regulation
✓ Article 6(3): YES - foreseeable bias risk not addressed
✓ Systemic pattern: Similar bias issues in other facial recognition systems
✓ Severity: HIGH - fundamental rights violation

Recommendation:
"If this incident occurred in 2024 post-EU AI Act:
 - Would be clear violation of Annex III + Article 6(3)
 - Fine: €10-15M range
 - Immediate system deactivation required
 - Training data audit required"
```

---

## Lessons and Limitations

### What Works Well
- ✅ Extracting system properties from narratives
- ✅ Querying ontology for requirements
- ✅ Identifying compliance gaps
- ✅ Ranking severity objectively
- ✅ Finding systemic patterns

### What Needs Human Review
- ⚠️ Article 6(3) judgment calls
- ⚠️ Temporal applicability (which law applies when?)
- ⚠️ Factual accuracy verification
- ⚠️ Novel/emerging incident types
- ⚠️ Final enforcement decisions

### Key Constraints of AIAAIC Database
```
Incident narratives in AIAAIC typically:
✓ Describe WHAT happened (harm, outcome)
✓ Identify WHICH system caused it
✓ Provide WHO was affected

BUT often lack:
✗ Precise technical architecture details
✗ Training data composition specifics
✗ Deployment configuration details
✗ Timeline of when features were enabled
✗ What safeguards existed (if any)
```

---

## Recommendation: Build a Pilot System

### Phase 1: Proof of Concept (3 months)
1. **Data**: Ingest 50 well-documented incidents from AIAAIC
2. **Agent**: Implement Llama 3.2 + MCP SPARQL extraction
3. **Validation**: Compare agent output vs. expert analysis
4. **Metrics**: Extract accuracy, requirement identification, gap detection

### Phase 2: Enhancement (3 months)
1. **Fine-tuning**: Train Llama on EU AI Act forensic analysis
2. **MCP Expansion**: Add incident-type-specific query templates
3. **Human Review**: Establish expert review process
4. **Feedback Loop**: Update ontology based on missing patterns

### Phase 3: Production (3 months)
1. **Scale**: Process full AIAAIC database (~1000+ incidents)
2. **Integration**: Connect to enforcement workflows
3. **Monitoring**: Track false positives, missed violations
4. **Regulatory Alignment**: Align with EC enforcement approach

---

## Conclusion

**Yes, a Llama 3.2 + Ontology + MCP SPARQL agent CAN perform forensic compliance analysis.**

**But**: It should be positioned as a **Human-in-the-Loop system**, where:
- The agent does the deterministic work (classification, requirement enumeration)
- Humans do the judgment work (Article 6(3), temporal, enforcement)

This is actually **ideal** for regulatory compliance:
- ✅ Deterministic + auditable (ontology queries)
- ✅ Scalable (can analyze hundreds of incidents)
- ✅ Explainable (full chain of reasoning)
- ✅ Human-accountable (experts make final decisions)

It prevents regulatory **bias** (all cases treated equally) while preserving **human judgment** (where it matters most).

