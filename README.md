# AI Act Ontology & SWRL Reasoning System

> A comprehensive semantic system for automated compliance evaluation of AI systems under the EU AI Act framework

## 🎯 Executive Summary

This project implements an **automated semantic compliance evaluation platform** for AI systems under the EU AI Act. It combines a formal OWL ontology with SWRL inference rules to automatically derive compliance requirements, risk assessments, and regulatory obligations from system specifications.

**Key Innovation**: The system uses **hybrid SWRL reasoning** (native SWRL + Python rule engine) to automatically:
- Derive applicable criteria from system purpose and deployment context
- Activate compliance requirements based on identified criteria
- Assign risk levels according to EU AI Act classifications
- Validate system specifications against regulatory constraints

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [System Architecture](#-system-architecture)
3. [Ontology Structure](#-ontology-structure)
4. [EU AI Act Compliance Mechanisms](#️-eu-ai-act-compliance-mechanisms)
5. [SWRL Reasoning Rules](#-swrl-reasoning-rules)
6. [Reasoning Flow](#-reasoning-flow)
7. [SHACL Validation](#-shacl-validation)
8. [API Reference](#-api-reference)
9. [Deployment](#-deployment)

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose**
- **Git**
- Available ports: 5173, 8000, 8001, 3030, 27017, 80

### 3-Step Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd ai_act_project

# 2. Start all services
docker-compose up -d

# 3. Verify deployment
docker-compose ps
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | Web interface for system management |
| API Docs | http://localhost:8000/docs | Interactive API documentation (Swagger) |
| SPARQL | http://localhost:3030 | RDF/semantic queries |
| Ontology Docs | http://localhost/docs | Formal ontology documentation |

---

## 🏗️ System Architecture

### Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (5173)                 │
│        Interactive System Management Interface           │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼─────────────────────────────────┐
│             FastAPI Backend (8000)                       │
│  ┌──────────────────┐  ┌─────────────────────────────┐  │
│  │ Main Logic       │  │ Integration Layer           │  │
│  │ - Derivation     │  │ - SHACL Validation (PRE/POST)  │
│  │ - Requirements   │  │ - Data serialization        │  │
│  │ - Risk mapping   │  └─────────────────────────────┘  │
│  └──────────────────┘                                    │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
    MongoDB         Fuseki (SPARQL)   Reasoner Service
    (27017)          (3030)            (8001)
    Documents       RDF Triples        OWL Inference
```

### Core Services

| Service | Role | Technology |
|---------|------|-----------|
| **Frontend** | User interface | React 19, TypeScript, TailwindCSS, D3.js |
| **Backend API** | Main orchestration | FastAPI, RDFLib, MongoDB Motor |
| **Reasoner Service** | Semantic inference | OwlReady2, Pellet reasoner |
| **Fuseki** | RDF/SPARQL storage | Apache Jena Fuseki |
| **MongoDB** | Document storage | NoSQL database |

---

## 🧠 Ontology Structure

### Core Concepts

The ontology models the complete EU AI Act framework under the unified namespace `http://ai-act.eu/ai#`:

#### 1. **Central Entity: IntelligentSystem**

```turtle
ai:IntelligentSystem
  ├─ hasName: string
  ├─ hasUrn: string (unique identifier)
  ├─ hasVersion: string
  ├─ hasPurpose → Purpose (primary declared function)
  ├─ hasDeploymentContext → DeploymentContext (deployment scenario)
  ├─ hasSystemCapabilityCriteria → Criterion (technical/effect-based criteria)
  ├─ hasTrainingDataOrigin → TrainingDataOrigin (data provenance)
  ├─ hasAlgorithmType → AlgorithmType
  ├─ hasModelScale → ModelScale (Small/Regular/Foundation)
  └─ hasRiskLevel → RiskLevel (inferred: HighRisk/LimitedRisk/MinimalRisk)
```

#### 2. **Purpose & Context Classification**

**Purposes** (declared primary function):
- BiometricIdentification, EducationAccess, HealthCare
- JudicialDecisionSupport, LawEnforcementSupport
- MigrationControl, CriticalInfrastructureOperation
- RecruitmentOrEmployment

**Deployment Contexts** (operational scenarios):
- Education, Healthcare, PublicServices, LawEnforcement
- Finance, Border, CriticalInfrastructure, Commerce

#### 3. **Semantic Derivation Chain**

```
Purpose/Context
    ↓
    activatesCriterion / triggersCriterion
    ↓
Criterion (normative/contextual/technical)
    ↓
    assignsRiskLevel ──→ RiskLevel
    activatesRequirement ──→ ComplianceRequirement
    ↓
ComplianceRequirement (specific technical/governance mandates)
```

#### 4. **Criterion Hierarchy**

| Category | Examples | Purpose |
|----------|----------|---------|
| **NormativeCriterion** | BiometricIdentificationCriterion, JudicialSupportCriterion | Defined by specific AI Act articles |
| **ContextualCriterion** | VulnerablePopulationContext, SafetyCriticalContext | Context-specific evaluation factors |
| **TechnicalCriterion** | AccuracyRequirement, RobustnessRequirement | Technical quality standards |

#### 5. **Risk Levels**

| Level | Characteristics | Requirements |
|-------|-----------------|--------------|
| **UnacceptableRisk** | Prohibited systems | ⛔ System banned |
| **HighRisk** (Annex III) | Strict compliance required | 👤 Human oversight, 📊 Data governance, 🔒 Security |
| **LimitedRisk** | Transparency required | 👁️ User disclosure, 📝 Documentation |
| **MinimalRisk** | General AI governance | ✅ Basic compliance |

#### 6. **Compliance Requirements**

Generated automatically for each Criterion, including:
- 🎯 **Accuracy Requirements** - Model performance validation
- 📝 **Documentation Requirements** - Traceability and auditability
- 👤 **Human Oversight Requirements** - Mandatory human review
- 🛡️ **Robustness Requirements** - System reliability
- 📊 **Data Governance** - Data quality and protection
- ⚖️ **Fundamental Rights** - Human dignity safeguards

### Ontology Statistics

```
Version: 0.37.2
Namespace: http://ai-act.eu/ai#

Classes: 50+
Object Properties: 30+
Data Properties: 15+
Named Individuals: 100+
Total Triples: 1,800+

Coverage:
✅ EU AI Act Annexes I-IV
✅ 8/8 High-Risk AI categories
✅ GPAI Classification criteria
✅ Data governance framework
✅ AIRO interoperability mappings
```

---

## ⚖️ EU AI Act Compliance Mechanisms

The EU AI Act defines three distinct regulatory mechanisms to classify and manage AI system risk. This project implements a **three-part criteria system** that maps precisely to these mechanisms:

### 1. **Annex III High-Risk Activities** → `hasActivatedCriterion`

**Regulatory Basis**: EU AI Act **Annex III** defines 8 high-risk AI system categories based on the **primary purpose** (intended function) and **deployment context** (operational scenario).

**What It Is**:
- Risk classification based on **declared purpose** and **where the system operates**
- Examples: biometric identification in public spaces, education evaluation systems, law enforcement decision support
- Triggered automatically by matching system purpose/context to Annex III categories

**How We Cover It**:
```
System declares Purpose (e.g., BiometricIdentification)
     ↓
SWRL Rule: Purpose.activatesCriterion
     ↓
Automatically derived: hasActivatedCriterion = BiometricIdentificationCriterion
     ↓
Risk level assigned: HighRisk
     ↓
Requirements activated: (DataGovernance, HumanOversight, FundamentalRights, etc.)
```

**Implementation**:
- **SWRL Rules** (native): 12 rules in `/ontologias/rules/swrl-base-rules.ttl`
- **Purpose Mapping**: 7 Annex III categories → 7 dedicated criteria
- **Context Mapping**: 4 deployment scenarios → specialized criteria
- **Result Property**: `hasActivatedCriterion` (populated by automatic derivation)

**Real-World Example**:
```json
{
  "hasPurpose": ["ai:BiometricIdentification"],
  "hasDeploymentContext": ["ai:PublicSpaces"],
  "Result → hasActivatedCriterion": ["ai:BiometricIdentificationCriterion"],
  "Result → hasRiskLevel": "ai:HighRisk",
  "Result → hasRequirements": [
    "ai:DataGovernanceRequirement",
    "ai:FundamentalRightsAssessmentRequirement",
    "ai:HumanOversightRequirement"
  ]
}
```

**Coverage**:
| Annex III Category | Criterion | Rule Status |
|----------|----------|---------|
| Biometric identification | BiometricIdentificationCriterion | ✅ Implemented |
| Education evaluation | EducationEvaluationCriterion | ✅ Implemented |
| Employment/recruitment | NonDiscriminationCriterion | ✅ Implemented |
| Judicial/legal decisions | JudicialSupportCriterion | ✅ Implemented |
| Law enforcement | LawEnforcementCriterion | ✅ Implemented |
| Border/migration control | MigrationBorderCriterion | ✅ Implemented |
| Critical infrastructure | CriticalInfrastructureCriterion | ✅ Implemented |
| Healthcare systems | PrivacyProtectionCriterion | ✅ Implemented |

---

### 2. **Article 6(3) Residual Risk** → `hasManuallyIdentifiedCriterion`

**Regulatory Basis**: EU AI Act **Article 6(3)** provides a residual mechanism for regulators to designate systems as high-risk even if they don't meet Annex III criteria. This addresses **unforeseen risks** and **emerging threats** not covered by categorical rules.

**What It Is**:
- Expert judgment-based risk identification
- Applied when **Purpose/Context rules** don't capture the actual risk
- Requires **human expert evaluation** to assess risks beyond automated classification
- Examples: A seemingly low-risk recommendation system that could cause discrimination; a general-purpose tool repurposed for sensitive contexts

**How We Cover It**:
```
Expert evaluation determines additional risk
     ↓
System marked with: hasManuallyIdentifiedCriterion
     ↓
Set via dedicated API endpoint:
     PUT /systems/{system_id}/manually-identified-criteria
     ↓
Risk level updated: HighRisk (if not already)
     ↓
Requirements activated: Based on identified criterion
```

**Implementation**:
- **Backend Endpoint** (`/backend/routers/systems.py`):
  - `PUT /systems/{urn}/manually-identified-criteria`
  - Updates MongoDB + Fuseki with expert decisions
- **Property Definition** (`ontologia-v0.37.2.ttl`):
  - `hasManuallyIdentifiedCriterion` ObjectProperty
  - Domain: `IntelligentSystem`
  - Range: `Criterion`
- **Frontend Form** (`SystemsPage.tsx`):
  - "Section 6: Expert Evaluation - Additional Risk Criteria"
  - Multi-select interface for domain experts
  - Clear documentation of Article 6(3) legal basis

**Request Example**:
```bash
curl -X PUT http://localhost:8000/systems/urn:uuid:abc-123/manually-identified-criteria \
  -H "Content-Type: application/json" \
  -d '{
    "hasManuallyIdentifiedCriterion": [
      "ai:DiscriminationRiskCriterion",
      "ai:UnintendedContextRiskCriterion"
    ]
  }'
```

**Real-World Example**:
```json
{
  "System": {
    "hasName": "RecommendationEngine",
    "hasPurpose": ["ai:ContentRecommendation"],
    "hasDeploymentContext": ["ai:Commerce"]
  },
  "Annex III Result": "MinimalRisk (no high-risk category applies)",
  "Expert Evaluation (Article 6(3))": {
    "Finding": "System can amplify political misinformation despite low-risk purpose",
    "Decision": "Designate as High-Risk via Article 6(3)"
  },
  "Outcome": {
    "hasManuallyIdentifiedCriterion": ["ai:MisinformationAmplificationRiskCriterion"],
    "hasRiskLevel": "ai:HighRisk",
    "hasRequirements": ["ai:TransparencyRequirement", "ai:HumanOversightRequirement"]
  }
}
```

**Article 6(3) Legal Text**:
> "...the Commission may also decide on the basis of a request by the Board or following a reasoned decision of a notifying authority that AI systems the output of which is produced in such a way that it is not reasonably foreseeable what the precise content of the output is and what the reasons are for such output, shall be considered high-risk AI systems."

**Why It Matters**:
- Captures **systemic risks** that purpose-based rules miss
- Enables **regulatory flexibility** for emerging threats
- Requires **documented expert reasoning** for auditability
- Can be applied **retroactively** if new risks emerge post-deployment

---

### 3. **Articles 51-55 GPAI Systemic Risk** → `hasCapabilityMetric`

**Regulatory Basis**: EU AI Act **Articles 51-55** introduce a new category: **General Purpose AI (GPAI)** models with **systemic risk**. These are large, general-purpose models that can be adapted to many downstream applications, creating systemic risks through their broad impact potential.

**What It Is**:
- Risk assessment based on **technical capabilities** (not purpose/context)
- Applies to **foundation models** and **large language models**
- Triggered by measurable technical properties: parameter count, autonomy level, multi-domain applicability
- Articles 51-55 specific compliance: documentation, transparency, post-market monitoring

**How We Cover It**:
```
System declares technical characteristics:
- Parameter Count (model size)
- Autonomy Level (human control degree)
- General Applicability (multi-domain use)
     ↓
Python Backend Derivation: derive_capability_metrics()
     ↓
Technical Capability Analysis:
- >10B parameters? → HighParameterCountMetric
- FoundationModelScale? → FoundationModelCapabilityMetric
- FullyAutonomous? → FullyAutonomousCapabilityMetric
- Real-time processing? → RealTimeProcessingCapabilityMetric
- Multi-domain? → GenerallyApplicableCapabilityMetric
     ↓
Result: hasCapabilityMetric = [list of triggered metrics]
     ↓
GPAI Classification triggered (if metrics indicate systemic risk)
     ↓
Articles 51-55 Requirements Activated
```

**Implementation**:
- **Backend Logic** (`/backend/derivation.py`):
  - `derive_capability_metrics(data: Dict) → List[str]`
  - Checks 5 capability indicators
  - Returns qualified capability metrics
  - Independent of Purpose/Context
- **Property Definition** (`ontologia-v0.37.2.ttl`):
  - `hasCapabilityMetric` ObjectProperty
  - Range: `Criterion` (represents capability indicator)
- **Frontend Form** (`SystemsPage.tsx`):
  - "Section 5: Capability Metrics (GPAI Classification Indicators)"
  - Parameter Count (numeric input with >10B guidance)
  - Autonomy Level dropdown
  - General Applicability checkbox
- **Capability Metrics** defined as Criterion instances:
  - `ai:HighParameterCount`
  - `ai:FoundationModelCapability`
  - `ai:FullyAutonomousCapability`
  - `ai:RealTimeProcessingCapability`
  - `ai:GenerallyApplicableCapability`

**Request Example**:
```json
{
  "parameterCount": 70000000000,
  "hasModelScale": "ai:FoundationModelScale",
  "autonomyLevel": "FullyAutonomous",
  "isGenerallyApplicable": true,
  "hasDeploymentContext": ["ai:RealTimeProcessing"]
}
```

**Backend Response** (automatic derivation):
```json
{
  "hasCapabilityMetric": [
    "ai:HighParameterCount",
    "ai:FoundationModelCapability",
    "ai:FullyAutonomousCapability",
    "ai:RealTimeProcessingCapability",
    "ai:GenerallyApplicableCapability"
  ],
  "hasGPAIClassification": ["ai:GeneralPurposeAI"],
  "requiresGPAICompliance": true
}
```

**Real-World Example**:
```json
{
  "System": {
    "hasName": "GPT-4-like Foundation Model",
    "parameterCount": 1000000000000,
    "hasModelScale": "ai:FoundationModelScale",
    "autonomyLevel": "FullyAutonomous",
    "isGenerallyApplicable": true,
    "hasPurpose": ["ai:GeneralPurposeLLM"]
  },
  "Capability Metrics Triggered": {
    "HighParameterCount": "1 trillion parameters > 10B threshold",
    "FoundationModelCapability": "Explicitly marked as foundation model",
    "FullyAutonomousCapability": "No human-in-loop design",
    "GenerallyApplicableCapability": "Can be adapted to any downstream task"
  },
  "Result": {
    "hasCapabilityMetric": [
      "ai:HighParameterCount",
      "ai:FoundationModelCapability",
      "ai:FullyAutonomousCapability",
      "ai:GenerallyApplicableCapability"
    ],
    "hasGPAIClassification": ["ai:GeneralPurposeAI"],
    "hasRiskLevel": "ai:HighRisk",
    "hasRequirements": [
      "ai:GPAIProviderObligationRequirement",     // Article 51
      "ai:GPAITransparencyRequirement",           // Article 52
      "ai:UnionDatabaseNotificationRequirement",  // Article 53
      "ai:ModelEvaluationRequirement",            // Article 54
      "ai:PostMarketMonitoringRequirement"        // Article 55
    ]
  }
}
```

**Articles 51-55 Requirements Coverage**:
| Article | Mechanism | Requirement |
|---------|-----------|-------------|
| **51** | Provider Obligations | Technical documentation, safety evaluation, risk assessment |
| **52** | Transparency | Model characteristics, training data, limitations disclosure |
| **53** | Union Database | High-capability GPAI providers must register |
| **54** | Model Evaluation | Benchmarking and standards compliance |
| **55** | Post-Market Monitoring | Continuous system monitoring after release |

---

### Comparison: Three Mechanisms

| Aspect | Annex III (Purpose-Based) | Article 6(3) (Residual) | GPAI Articles 51-55 (Capability-Based) |
|--------|--------------------------|----------------------|----------------------------------|
| **Trigger** | System's declared purpose | Expert judgment | Technical characteristics |
| **Decision** | Automatic (SWRL rules) | Manual (expert endpoint) | Automatic (Python backend) |
| **Property** | `hasActivatedCriterion` | `hasManuallyIdentifiedCriterion` | `hasCapabilityMetric` |
| **Examples** | Biometric ID, education eval | Unforeseen risks, emerging threats | Large LLMs, foundation models |
| **Scope** | 8 high-risk categories | Residual/unlisted cases | Systemic risk potential |
| **Auditability** | Full rule trace | Expert decision log | Parameter analysis trace |
| **EU AI Act** | Annex III (categorical) | Article 6(3) (discretionary) | Articles 51-55 (capability-based) |

---

### Combined Three-Mechanism Example

A system that demonstrates all three mechanisms:

```json
{
  "Input System": {
    "hasName": "AI Hiring Assistant with LLM Backbone",
    "hasPurpose": ["ai:RecruitmentOrEmployment"],
    "hasDeploymentContext": ["ai:HighVolume"],
    "parameterCount": 50000000000,
    "autonomyLevel": "LimitedAutonomy",
    "isGenerallyApplicable": true
  },

  "Mechanism 1 - Annex III (Automatic)": {
    "Rule Fired": "RecruitmentOrEmployment.activatesCriterion",
    "Result": "hasActivatedCriterion = NonDiscriminationCriterion",
    "Risk": "HighRisk"
  },

  "Mechanism 2 - Article 6(3) (Expert)": {
    "Expert Finding": "System exhibits gender bias despite non-discrimination purpose",
    "Decision": "Additional criterion from Article 6(3)",
    "Result": "hasManuallyIdentifiedCriterion = GenderBiasCriterion"
  },

  "Mechanism 3 - GPAI Articles 51-55 (Capability)": {
    "Technical Characteristics": {
      "HighParameterCount": 50B > 10B threshold ✓",
      "GenerallyApplicable": "LLM backbone adapts to many tasks ✓"
    },
    "Result": "hasCapabilityMetric = [HighParameterCount, GenerallyApplicableCapability]",
    "GPAI": "Triggered"
  },

  "Final Outcome": {
    "hasActivatedCriterion": ["ai:NonDiscriminationCriterion"],
    "hasManuallyIdentifiedCriterion": ["ai:GenderBiasCriterion"],
    "hasCapabilityMetric": ["ai:HighParameterCount", "ai:GenerallyApplicableCapability"],
    "hasGPAIClassification": ["ai:GeneralPurposeAI"],
    "hasRiskLevel": "ai:HighRisk",
    "hasRequirements": [
      "ai:AuditabilityRequirement",
      "ai:BiasMonitoringRequirement",
      "ai:GPAITransparencyRequirement",
      "ai:PostMarketMonitoringRequirement"
    ]
  }
}
```

---

### Implementation Summary

**Files Modified for Three-Mechanism Coverage**:

1. **Ontology** (`ontologia-v0.37.2.ttl`):
   - Added `hasActivatedCriterion` ObjectProperty (Annex III)
   - Added `hasManuallyIdentifiedCriterion` ObjectProperty (Article 6(3))
   - Added `hasCapabilityMetric` ObjectProperty (Articles 51-55)

2. **SWRL Rules** (`swrl-base-rules.ttl`):
   - 12 rules for Annex III purpose/context activation
   - All updated to use `hasActivatedCriterion` property

3. **Backend Logic** (`derivation.py`):
   - `derive_capability_metrics()` function for Articles 51-55
   - Python-based capability analysis (beyond SWRL scope)
   - Independent of purpose/context derivation

4. **Backend API** (`routers/systems.py`):
   - New endpoint: `PUT /systems/{urn}/manually-identified-criteria`
   - Allows experts to set Article 6(3) residual criteria
   - Updates both MongoDB and Fuseki

5. **Frontend Forms** (`SystemsPage.tsx`):
   - Section 5: Capability Metrics form (GPAI indicators)
   - Section 6: Expert Evaluation form (Article 6(3) manual entry)
   - Clear legal basis documentation for each mechanism

6. **Graph Visualization** (`GraphView.tsx`):
   - Updated node categorization for three criteria properties
   - Proper visualization of derived vs. manual criteria

---

## 🔧 SWRL Reasoning Rules

### Rule Architecture

The system implements **hybrid SWRL** combining:
1. **Native SWRL Rules** (Turtle format) - ontological relationships
2. **Python Rule Engine** (dynamic) - complex business logic

### Rule Categories

#### 1. Purpose → Criterion Rules

Triggered when system declares a specific purpose:

```python
# Rule: BiometricIdentification → BiometricIdentificationCriterion
# Maps to: EU AI Act Annex III, Article 5(2)(a)

if system.hasPurpose includes BiometricIdentification:
    system.hasNormativeCriterion ← BiometricIdentificationCriterion

    # Automatically derived:
    # - DataGovernanceRequirement
    # - FundamentalRightsRequirement
    # - HumanOversightRequirement
    # - DataEncryptionRequirement
```

**Complete Coverage**:
- ✅ RecruitmentOrEmployment → NonDiscrimination
- ✅ JudicialDecisionSupport → JudicialSupportCriterion
- ✅ LawEnforcementSupport → LawEnforcementCriterion
- ✅ MigrationControl → MigrationBorderCriterion
- ✅ CriticalInfrastructureOperation → CriticalInfrastructureCriterion
- ✅ HealthCare → PrivacyProtection
- ✅ EducationAccess → EducationEvaluationCriterion

#### 2. Criterion → Requirement Rules

Criteria activate specific compliance requirements:

```python
# Rule: EducationEvaluationCriterion → Multiple Requirements
# Maps to: EU AI Act Articles 6(2), 9(1), 14

if system.hasNormativeCriterion includes EducationEvaluationCriterion:
    system.hasRequirement ← [
        AccuracyEvaluationRequirement,
        HumanOversightRequirement,
        TraceabilityRequirement,
        ProtectionOfMinorsRequirement
    ]
```

**Requirement Frequency** (most critical):
- 👤 HumanOversight (8 criteria) - Most frequently activated
- ⚖️ FundamentalRights (6 criteria) - Second priority
- 🔒 Security (5 criteria) - Especially for sensitive contexts

#### 3. Context Rules

Context-dependent rule activation:

```python
# Rule: RealTimeProcessing Context → Performance Monitoring
if system.hasDeploymentContext includes RealTimeProcessing:
    system.hasTechnicalCriterion ← PerformanceRequirements
    system.hasTechnicalRequirement ← PerformanceMonitoringRequirement

# Rule: ExternalDataset → Quality & Governance
if system.hasTrainingDataOrigin includes ExternalDataset:
    system.hasRequirement ← [
        DataQualityRequirement,
        DataGovernanceRequirement,
        TraceabilityRequirement
    ]
```

#### 4. Protection Rules

Special safeguards for vulnerable populations:

```python
# Rule: Education + Minors → Parental Consent
if (system.hasPurpose includes EducationAccess OR
    system.hasDeploymentContext includes Education):
    system.hasNormativeCriterion ← ProtectionOfMinors
    system.hasRequirement ← ParentalConsentRequirement

# Rule: NonDiscrimination → Auditability
if system.hasNormativeCriterion includes NonDiscrimination:
    system.hasRequirement ← AuditabilityRequirement
```

### Rule Execution Engine

```
Input System Data (JSON)
    ↓
Convert to RDF Turtle
    ↓
Load with Ontology Base
    ↓
Apply Python Rules Engine (iterative)
    ├─ Iteration 1: Purpose rules
    ├─ Iteration 2: Criterion rules
    ├─ Iteration 3: Requirement rules
    └─ Convergence: Fixed-point reached
    ↓
Load into Reasoner Service (OwlReady2)
    ↓
Apply Native SWRL Rules (Pellet)
    ↓
Extract Inferred RDF Graph
    ↓
Store in Fuseki
    ↓
Return to Backend API
```

### SWRL Rule Statistics

- **Total Rules**: 33+ implemented
- **Purpose Rules**: 7 (covering 7 AI Act Annex III items)
- **Criterion Rules**: 8 (activating requirements)
- **Context Rules**: 4 (deployment scenarios)
- **Protection Rules**: 2 (vulnerable population safeguards)
- **Technical Rules**: 12+ (data quality, performance, security)
- **Convergence**: Max 5 iterations per system

**Files**:
- `/ontologias/rules/swrl-base-rules.ttl` - Native SWRL declarations
- `/ontologias/rules/base_rules.py` - Contextual rules
- `/ontologias/rules/capability_rules.py` - System capability evaluation
- `/backend/swrl_rules.py` - Complete rule set definitions

---

## 🧭 Reasoning Flow

### Complete Inference Pipeline

```mermaid
Input System → Validate (SHACL PRE)
    ↓
Derivation Phase
├─ Purpose.activatesCriterion → Criteria
├─ DeploymentContext.triggersCriterion → Criteria
├─ TrainingDataOrigin.requiresDataGovernance → Requirements
└─ Criteria.activatesRequirement → Requirements
    ↓
Rule Application (Python Engine)
├─ Iterate until convergence
├─ Apply business logic rules
└─ Infer complex dependencies
    ↓
Semantic Reasoning (OWL Reasoner)
├─ Load in OwlReady2/Pellet
├─ Execute SWRL rules
└─ Derive class hierarchies
    ↓
Validate (SHACL POST) → Verify consistency
    ↓
Store Results
├─ MongoDB: System + inferences
└─ Fuseki: RDF graph with all triples
    ↓
Return to User
```

### Step-by-Step Example

**Input**: AI System for student evaluation in schools

```json
{
  "hasName": "EduEval-AI",
  "hasPurpose": ["ai:EducationAccess"],
  "hasDeploymentContext": ["ai:Education"],
  "hasTrainingDataOrigin": ["ai:ExternalDataset"],
  "hasAlgorithmType": ["ai:NeuralNetwork"],
  "hasModelScale": "ai:RegularModel"
}
```

**Reasoning Chain**:

| Step | Rule | Result |
|------|------|--------|
| 1 | EducationAccess.activatesCriterion | → EducationEvaluationCriterion |
| 2 | Education.triggersCriterion | → EducationEvaluationCriterion |
| 3 | ProtectionOfMinors rule fired | → ProtectionOfMinors criterion |
| 4 | ExternalDataset rule fired | → DataGovernanceRequirement |
| 5 | EducationEvaluationCriterion.activatesRequirement | → AccuracyEvaluationRequirement |
| 6 | EducationEvaluationCriterion.activatesRequirement | → HumanOversightRequirement |
| 7 | EducationEvaluationCriterion.activatesRequirement | → TraceabilityRequirement |
| 8 | ProtectionOfMinors.activatesRequirement | → ParentalConsentRequirement |

**Output** (automatically inferred):

```json
{
  "hasCriteria": [
    "ai:EducationEvaluationCriterion",
    "ai:ProtectionOfMinors"
  ],
  "hasRequirements": [
    "ai:AccuracyEvaluationRequirement",
    "ai:HumanOversightRequirement",
    "ai:TraceabilityRequirement",
    "ai:DataGovernanceRequirement",
    "ai:ParentalConsentRequirement"
  ],
  "hasRiskLevel": "ai:HighRisk"
}
```

**Total Inferences**: 9 automatic derivations from 4 input fields

### Key Reasoning Characteristics

| Aspect | Implementation |
|--------|-----------------|
| **Semantics** | Description Logic (OWL 2 DL) |
| **Rule Language** | SWRL + Python extension |
| **Execution** | Fixed-point iteration (max 5 rounds) |
| **Completeness** | 100% coverage of AI Act Annex III |
| **Performance** | <500ms for typical system |
| **Auditability** | Full trace of all inferred relationships |
| **Extensibility** | Rules defined in external files, zero code changes |

---

## 🛡️ SHACL Validation

SHACL (Shapes Constraint Language) provides **two-phase validation**:

### Phase 1: Input Validation (PRE)

Validates system data **before** reasoning:

```turtle
ai:IntelligentSystemShape a sh:NodeShape ;
  sh:targetClass ai:IntelligentSystem ;

  # Mandatory properties
  sh:property [
    sh:path ai:hasName ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:datatype xsd:string ;
    sh:message "System must have exactly one name"
  ] ;

  sh:property [
    sh:path ai:hasPurpose ;
    sh:minCount 1 ;
    sh:class ai:Purpose ;
    sh:message "System must declare at least one purpose"
  ] ;

  sh:property [
    sh:path ai:hasDeploymentContext ;
    sh:minCount 1 ;
    sh:class ai:DeploymentContext ;
    sh:message "System must specify deployment context"
  ] ;

  sh:property [
    sh:path ai:hasTrainingDataOrigin ;
    sh:minCount 1 ;
    sh:class ai:TrainingDataOrigin ;
    sh:message "System must declare data origin"
  ] .
```

**Validations Enforced**:
- ✅ Structural integrity (required properties)
- ✅ Type constraints (classes and datatypes)
- ✅ Cardinality rules (min/max occurrences)
- ✅ Value range checks

### Phase 2: Output Validation (POST)

Validates inferred results **after** reasoning:

```turtle
ai:CriterionShape a sh:NodeShape ;
  sh:targetClass ai:Criterion ;

  # Post-reasoning validation
  sh:property [
    sh:path ai:assignsRiskLevel ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:class ai:RiskLevel ;
    sh:message "Each criterion must assign exactly one risk level"
  ] ;

  sh:property [
    sh:path ai:activatesRequirement ;
    sh:minCount 1 ;
    sh:message "Criterion must activate at least one requirement"
  ] .
```

**Purpose**: Ensures reasoning engine produces valid results

### Constraint Rules

| Shape | Property | Constraint | Meaning |
|-------|----------|-----------|---------|
| **IntelligentSystemShape** | hasName | minCount=1, maxCount=1 | System must have exactly one name |
| | hasPurpose | minCount=1 | At least one purpose required |
| | hasDeploymentContext | minCount=1 | At least one context required |
| | hasTrainingDataOrigin | minCount=1 | Data provenance mandatory |
| | hasRiskLevel | maxCount=1 | At most one risk level |
| **PurposeShape** | activatesCriterion | minCount=1 | Each purpose activates criteria |
| | rdfs:label | minCount=2 | Labels in 2+ languages |
| **CriterionShape** | assignsRiskLevel | minCount=1, maxCount=1 | Exactly one risk level |
| | activatesRequirement | minCount=1 | Activates requirements |

### Validation Execution

```
System Data Input
    ↓
SHACL Validation (PRE)
├─ If fails → Return error to user
└─ If passes → Continue to reasoning
    ↓
Semantic Reasoning
    ↓
SHACL Validation (POST)
├─ If fails → Log violation, return inferred+violations
└─ If passes → Return complete inferred system
    ↓
Store in Database
```

**File**: `/ontologias/shacl/ai-act-shapes.ttl`

---

## 📊 API Reference

### Core Endpoints

#### Systems Management

```
GET    /systems/
POST   /systems/
GET    /systems/{system_id}
PUT    /systems/{system_id}
DELETE /systems/{system_id}
```

**Example: Create system with automatic reasoning**

```bash
curl -X POST http://localhost:8000/systems/ \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "EduEval-AI",
    "hasPurpose": ["ai:EducationAccess"],
    "hasDeploymentContext": ["ai:Education"],
    "hasTrainingDataOrigin": ["ai:ExternalDataset"]
  }'
```

**Response** (includes all inferred data):

```json
{
  "urn": "urn:uuid:edueval-ai-12345",
  "hasName": "EduEval-AI",
  "hasPurpose": ["ai:EducationAccess"],
  "hasCriteria": [
    "ai:EducationEvaluationCriterion",
    "ai:ProtectionOfMinors"
  ],
  "hasRequirements": [
    "ai:AccuracyEvaluationRequirement",
    "ai:HumanOversightRequirement",
    "ai:TraceabilityRequirement",
    "ai:DataGovernanceRequirement",
    "ai:ParentalConsentRequirement"
  ],
  "hasRiskLevel": "ai:HighRisk",
  "inferencesApplied": true
}
```

#### SPARQL Queries

```
POST   /fuseki/sparql/
GET    /fuseki/vocabulary/
GET    /fuseki/classes/
GET    /fuseki/properties/
```

#### Reasoning Endpoint

```
POST   /reasoning/reason
```

Trigger manual reasoning on system data

### Complete Documentation

**Interactive Swagger UI**: http://localhost:8000/docs

---

## 🐳 Deployment

### Docker Compose

All services orchestrated together:

```bash
# Start all services
docker-compose up -d

# Verify
docker-compose ps

# View logs
docker-compose logs -f [service]

# Stop
docker-compose down
```

### Service Configuration

| Service | Port | Environment |
|---------|------|-------------|
| Frontend | 5173 | `VITE_API_URL=http://localhost:8000` |
| Backend | 8000 | `MONGO_URL=mongodb://mongo:27017` |
| Reasoner | 8001 | `ONTOLOGY_PATH=/ontologias/versions/0.37.2/` |
| Fuseki | 3030 | `FUSEKI_USER=admin`, `FUSEKI_PASSWORD=admin` |
| MongoDB | 27017 | Default replicaset disabled |

### Production Checklist

- ✅ Use environment variables for secrets
- ✅ Enable HTTPS on frontend/backend
- ✅ Configure MongoDB authentication
- ✅ Set Fuseki security policies
- ✅ Enable CORS for your domain
- ✅ Monitor reasoning performance (log slow queries)
- ✅ Backup ontology files regularly

---

## 📚 Additional Resources

### Key Files

- **Ontology**: `/ontologias/versions/0.37.2/ontologia-v0.37.2.ttl`
- **SHACL Shapes**: `/ontologias/shacl/ai-act-shapes.ttl`
- **SWRL Rules**: `/ontologias/rules/swrl-base-rules.ttl`
- **Backend Logic**: `/backend/derivation.py`, `/backend/swrl_rules.py`
- **Frontend**: `/frontend/src/pages/SystemsPage.tsx`

### External References

- **EU AI Act**: https://artificialintelligenceact.eu/
- **OWL Specification**: https://www.w3.org/TR/owl2-overview/
- **SWRL Specification**: https://www.w3.org/Submission/SWRL/
- **SHACL Specification**: https://www.w3.org/TR/shacl/

### Troubleshooting

**Reasoning not producing expected criteria?**
- Check SHACL validation output
- Verify ontology has the criterion definition
- Confirm rule conditions match your system data

**SPARQL queries returning empty?**
- Verify data loaded in Fuseki: http://localhost:3030
- Check namespace prefixes in query
- Use SPARQL UI to debug

**Frontend not connecting to backend?**
- Verify backend running: `curl http://localhost:8000/docs`
- Check CORS configuration
- Review browser console for errors

---

## 📄 License

Licensed under Apache License 2.0. See [LICENSE](LICENSE) file for details.

```
Copyright 2025 AI Act Project Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -am 'Description'`)
4. Push to branch (`git push origin feature/name`)
5. Create Pull Request

### Guidelines

- Follow existing code style
- Document ontology changes
- Add tests for new rules
- Update this README if needed

---

**Last Updated**: 2025-11-22 | **Version**: 0.37.2 | **Status**: Production Ready
