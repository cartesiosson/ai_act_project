# EU AI Act Ontology - Comprehensive Guide

> Complete technical documentation of the EU AI Act ontology (v0.37.2) including architecture, class hierarchies, properties, and reasoning mechanisms.

## Table of Contents

1. [Overview](#overview)
2. [Core Architecture](#core-architecture)
3. [Class Hierarchy](#class-hierarchy)
4. [Properties](#properties)
5. [Three Compliance Mechanisms](#three-compliance-mechanisms)
6. [Reasoning Chains](#reasoning-chains)
7. [Data Flow](#data-flow)
8. [Examples](#examples)
9. [Query Patterns](#query-patterns)

---

## Overview

The EU AI Act Ontology models the complete regulatory framework of the EU Artificial Intelligence Act in formal semantic web standards (OWL 2.0).

### Key Statistics

```
Version:          0.37.2
Namespace:        http://ai-act.eu/ai#
Language:         OWL 2.0 DL + SWRL
Classes:          50+
Object Properties: 30+
Data Properties:  15+
Named Individuals: 100+
Total Triples:    1,800+
Coverage:         EU AI Act Annex I-IV + Articles 51-55
Standards:        ISO 42001, NIST AI RMF, AIRO
```

### Unified Namespace

All concepts consolidated under single namespace `http://ai-act.eu/ai#` for:
- **Simplicity**: Reduces namespace proliferation
- **Discoverability**: All AI Act concepts in one place
- **Interoperability**: Single context for JSON-LD and RDF

---

## Core Architecture

### Top-Level Concept: IntelligentSystem

The ontology models AI systems as instances of `ai:IntelligentSystem`, which is the central entity that holds all compliance information.

```mermaid
graph TD
    IS["IntelligentSystem<br/>(Central Entity)"]

    IS -->|declares| Purpose["Purpose<br/>(Primary function)"]
    IS -->|deploys in| Context["DeploymentContext<br/>(Where it runs)"]
    IS -->|uses| Data["TrainingDataOrigin<br/>(Data source)"]
    IS -->|employs| Algorithm["AlgorithmType<br/>(ML approach)"]
    IS -->|has| Scale["ModelScale<br/>(Size indicator)"]

    IS -->|activates via Annex III| Crit1["Criterion<br/>(Purpose/Context)"]
    IS -->|manually adds via Art 6-3| Crit2["Criterion<br/>(Expert judgment)"]
    IS -->|has capability| Metric["CapabilityMetric<br/>(GPAI indicator)"]

    Crit1 -->|determines| Risk["RiskLevel<br/>(HighRisk/Limited/Minimal)"]
    Crit2 -->|determines| Risk
    Metric -->|determines| GPAI["GPAI Classification"]

    Crit1 -->|activates| Req["ComplianceRequirement<br/>(Controls to implement)"]
    Crit2 -->|activates| Req

    Risk --> IR["InferredRiskProfile<br/>(System compliance state)"]
    Req --> IR
    GPAI --> IR

    style IS fill:#ffcccc
    style Req fill:#ccffcc
    style Risk fill:#ccccff
```

### Conceptual Layers

```mermaid
graph LR
    L1["LAYER 1: Input Properties<br/>(What we declare about system)<br/>Purpose, Context, DataOrigin, Algorithm"]

    L2["LAYER 2: Derived Criteria<br/>(What applies to system)<br/>Automatic + Manual criteria"]

    L3["LAYER 3: Compliance Requirements<br/>(What must be implemented)<br/>Data governance, Security, Oversight"]

    L4["LAYER 4: Risk Assessment<br/>(What level of risk)<br/>HighRisk, LimitedRisk, MinimalRisk"]

    L1 -->|SWRL/Derivation| L2
    L2 -->|Activation rules| L3
    L2 & L3 -->|Assessment| L4

    style L1 fill:#fff3cd
    style L2 fill:#cfe2ff
    style L3 fill:#d1ecf1
    style L4 fill:#f8d7da
```

---

## Class Hierarchy

### Complete Class Taxonomy

```mermaid
graph TD
    OWL["owl:Thing"]

    OWL --> IS["IntelligentSystem<br/>(Central entity for AI systems)"]
    OWL --> C["Criterion<br/>(Classification unit)"]
    OWL --> Purpose["Purpose<br/>(Declared function)"]
    OWL --> Context["DeploymentContext<br/>(Operational scenario)"]
    OWL --> Req["ComplianceRequirement<br/>(Regulatory control)"]
    OWL --> Risk["RiskLevel<br/>(Classification level)"]
    OWL --> Data["TrainingDataOrigin<br/>(Data source)"]
    OWL --> Algo["AlgorithmType<br/>(ML approach)"]
    OWL --> Scale["ModelScale<br/>(Size category)"]

    C --> NC["NormativeCriterion<br/>(Based on EU AI Act articles)"]
    C --> CC["ContextualCriterion<br/>(Context-specific risks)"]
    C --> TC["TechnicalCriterion<br/>(Technical standards)"]
    C --> SCC["SystemCapabilityCriterion<br/>(Capability-based)"]

    NC --> BIC["BiometricIdentificationCriterion"]
    NC --> JC["JudicialSupportCriterion"]
    NC --> LEC["LawEnforcementCriterion"]
    NC --> MBC["MigrationBorderCriterion"]
    NC --> CIC["CriticalInfrastructureCriterion"]
    NC --> EEC["EducationEvaluationCriterion"]
    NC --> REC["RecruitmentEmploymentCriterion"]
    NC --> WEC["WorkforceEvaluationCriterion"]
    NC --> EAC["EssentialServicesAccessCriterion"]

    CC --> CMR["ChildrenAndMinorsRiskCriterion"]
    CC --> EDR["ElderlyAndDisabledRiskCriterion"]
    CC --> SVR["SocioeconomicVulnerabilityRiskCriterion"]
    CC --> ADR["AutonomousDecisionmakingRiskCriterion"]
    CC --> RTA["RealTimeAutonomousRiskCriterion"]
    CC --> WSI["WidespreadSystemicImpactRiskCriterion"]
    CC --> CII["CriticalInfrastructureInterdependencyRiskCriterion"]
    CC --> BDR["BlackBoxDecisionRiskCriterion"]
    CC --> HSD["HighStakesDecisionWithoutAppealRiskCriterion"]
    CC --> HBR["HistoricalBiasReplicationRiskCriterion"]
    CC --> PCI["ProtectedCharacteristicInferenceRiskCriterion"]
    CC --> BDS["BiometricDataSensitivityRiskCriterion"]
    CC --> PDR["PersonalDataRetentionRiskCriterion"]
    CC --> LEI["LargeScaleEnvironmentalImpactRiskCriterion"]
    CC --> MAR["MisinformationAmplificationRiskCriterion"]

    SCC --> SRA["SystemicRiskAssessmentCriterion"]
    SCC --> DUR["DualUseRiskCriterion"]

    Req --> DR["DataGovernanceRequirement"]
    Req --> TR["TransparencyRequirement"]
    Req --> TecR["TechnicalRequirement"]
    Req --> RobR["RobustnessRequirement"]
    Req --> SecR["SecurityRequirement"]
    Req --> LogR["LoggingRequirement"]
    Req --> DocR["DocumentationRequirement"]
    Req --> HOR["HumanOversightRequirement"]
    Req --> FRA["FundamentalRightsAssessmentRequirement"]
    Req --> NDR["NonDiscriminationRequirement"]
    Req --> BDtR["BiasDetectionRequirement"]
    Req --> BDSSecR["BiometricSecurityRequirement"]
    Req --> ENC["EncryptionRequirement"]
    Req --> ACR["AccessControlRequirement"]

    Risk --> UR["UnacceptableRisk"]
    Risk --> HR["HighRisk"]
    Risk --> LR["LimitedRisk"]
    Risk --> MR["MinimalRisk"]

    style IS fill:#ff6b6b
    style C fill:#4ecdc4
    style NC fill:#45b7d1
    style CC fill:#96ceb4
    style SCC fill:#ffeaa7
    style Req fill:#dfe6e9
    style Risk fill:#fab1a0
    style Purpose fill:#74b9ff
    style Context fill:#a29bfe
```

### Criterion Classification

```mermaid
graph TD
    Crit["Criterion<br/>(Abstract)"]

    subgraph "Purpose-Based<br/>(Automatic via SWRL)"
        NC["NormativeCriterion<br/>(Annex III)"]
        NC1["BiometricIdentificationCriterion"]
        NC2["JudicialSupportCriterion"]
        NC3["LawEnforcementCriterion"]
        NC4["MigrationBorderCriterion"]
        NC5["CriticalInfrastructureCriterion"]
        NC6["EducationEvaluationCriterion"]
        NC7["RecruitmentEmploymentCriterion"]
        NC8["WorkforceEvaluationCriterion"]
        NC9["EssentialServicesAccessCriterion"]

        NC --> NC1
        NC --> NC2
        NC --> NC3
        NC --> NC4
        NC --> NC5
        NC --> NC6
        NC --> NC7
        NC --> NC8
        NC --> NC9
    end

    subgraph "Expert-Identified<br/>(Manual via Article 6-3)"
        CC["ContextualCriterion<br/>(15 vulnerability factors)"]
        CC1["ChildrenAndMinorsRiskCriterion"]
        CC2["ElderlyAndDisabledRiskCriterion"]
        CC3["SocioeconomicVulnerabilityRiskCriterion"]
        CC4["AutonomousDecisionmakingRiskCriterion"]
        CC5["RealTimeAutonomousRiskCriterion"]
        CC6["WidespreadSystemicImpactRiskCriterion"]

        CC --> CC1
        CC --> CC2
        CC --> CC3
        CC --> CC4
        CC --> CC5
        CC --> CC6
    end

    subgraph "Capability-Based<br/>(Technical indicators)"
        SCC["SystemCapabilityCriterion<br/>(Articles 51-55)"]
        SCC1["SystemicRiskAssessmentCriterion"]
        SCC2["DualUseRiskCriterion"]

        SCC --> SCC1
        SCC --> SCC2
    end

    Crit --> NC
    Crit --> CC
    Crit --> SCC

    style Crit fill:#ffcccc
    style NC fill:#cfe2ff
    style CC fill:#d1ecf1
    style SCC fill:#fff3cd
```

### Compliance Requirements Hierarchy

```mermaid
graph TD
    CR["ComplianceRequirement<br/>(What must be implemented)"]

    CR --> DG["DataGovernanceRequirement<br/>(Data quality, lineage, minimization)"]
    CR --> TR["TransparencyRequirement<br/>(User disclosure, explainability)"]
    CR --> TecR["TechnicalRequirement<br/>(Performance, robustness, accuracy)"]
    CR --> RobR["RobustnessRequirement<br/>(Reliability, error handling)"]
    CR --> SecR["SecurityRequirement<br/>(Encryption, access control, audit trails)"]
    CR --> LogR["LoggingRequirement<br/>(Event tracking, audit logs)"]
    CR --> DocR["DocumentationRequirement<br/>(Technical docs, risk assessments)"]
    CR --> HOR["HumanOversightRequirement<br/>(Manual review, intervention)"]
    CR --> FRA["FundamentalRightsAssessmentRequirement<br/>(FRIA - human dignity protection)"]
    CR --> NDR["NonDiscriminationRequirement<br/>(Fairness, bias detection)"]
    CR --> BDR["BiasDetectionRequirement<br/>(Monitoring for discrimination)"]
    CR --> BDSR["BiometricSecurityRequirement<br/>(Biometric-specific security)"]
    CR --> ENC["EncryptionRequirement<br/>(Data encryption in transit/at rest)"]
    CR --> ACR["AccessControlRequirement<br/>(Who can access what)"]

    style CR fill:#d1ecf1
    style DG fill:#e2f0ff
    style TR fill:#e2f0ff
    style TecR fill:#e2f0ff
    style SecR fill:#ffe2e2
    style HOR fill:#ffe2f0
    style FRA fill:#fff0e2
```

---

## Properties

### Object Properties (IRI → IRI References)

```mermaid
graph LR
    IS["IntelligentSystem"]

    IS -->|hasPurpose| Purpose["Purpose"]
    IS -->|hasDeploymentContext| Context["DeploymentContext"]
    IS -->|hasTrainingDataOrigin| Data["TrainingDataOrigin"]
    IS -->|hasAlgorithmType| Algo["AlgorithmType"]
    IS -->|hasModelScale| Scale["ModelScale"]
    IS -->|hasCapability| Cap["Capability"]

    IS -->|hasActivatedCriterion| Crit1["Criterion<br/>(Auto via Annex III)"]
    IS -->|hasManuallyIdentifiedCriterion| Crit2["Criterion<br/>(Manual via Art 6-3)"]
    IS -->|hasSystemCapabilityCriteria| Crit3["Criterion<br/>(Tech indicators)"]

    Crit1 -->|assignsRiskLevel| Risk["RiskLevel"]
    Crit1 -->|activatesRequirement| Req["ComplianceRequirement"]
    Crit2 -->|activatesRequirement| Req
    Crit3 -->|activatesRequirement| Req

    IS -->|hasComplianceRequirement| Req
    IS -->|hasRiskLevel| Risk

    Purpose -->|activatesCriterion| Crit1
    Context -->|triggersCriterion| Crit1

    style IS fill:#ffcccc
    style Purpose fill:#fff3cd
    style Context fill:#cfe2ff
    style Req fill:#d1ecf1
    style Risk fill:#ffe2e2
```

### Data Properties (IRI → Literal Values)

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `hasName` | `xsd:string` | System identifier | "EduEval-AI" |
| `hasUrn` | `xsd:anyURI` | Unique resource identifier | "urn:uuid:abc-123" |
| `hasVersion` | `xsd:string` | System version | "1.0.0" |
| `hasDescription` | `xsd:string` | System description | "Student evaluation system" |
| `hasFLOPS` | `xsd:double` | Computational capacity | 1e13 |

### Property Relationships

```mermaid
graph TD
    Purpose["Purpose (declared)"]
    Context["DeploymentContext (declared)"]
    Data["TrainingDataOrigin (declared)"]

    Purpose -->|SWRL Rule 1| AC["hasActivatedCriterion"]
    Context -->|SWRL Rule 2| AC
    Data -->|SWRL Rule 3| AC

    AC -->|SWRL Rule 4| Req["hasComplianceRequirement"]
    Req -->|Implementation| CR["ComplianceRequirement"]

    AC -->|SWRL Rule 5| Risk["hasRiskLevel"]
    Risk -->|Classification| RL["RiskLevel"]

    style Purpose fill:#fff3cd
    style Context fill:#cfe2ff
    style Data fill:#d1ecf1
    style AC fill:#ccffcc
    style Req fill:#d1ecf1
    style Risk fill:#ffe2e2
```

---

## Three Compliance Mechanisms

### Mechanism 1: Annex III (Purpose/Context → Automatic Criteria)

**Regulatory Basis**: EU AI Act Annex III defines 8 high-risk AI system categories

```mermaid
graph TD
    Input["System declares:<br/>hasPurpose + hasDeploymentContext"]

    Rule1["SWRL Rule:<br/>Purpose.activatesCriterion"]
    Rule2["SWRL Rule:<br/>Context.triggersCriterion"]

    Input -->|SWRL| Rule1
    Input -->|SWRL| Rule2

    Rule1 -->|derives| AC["hasActivatedCriterion<br/>(Normative Criterion)"]
    Rule2 -->|derives| AC

    AC -->|ontology traversal| Req["Requirement Activation"]
    AC -->|ontology traversal| Risk["Risk Assignment"]

    Req --> Impl["Criterion.activatesRequirement<br/>→ hasComplianceRequirement"]
    Risk --> RL["Criterion.assignsRiskLevel<br/>→ hasRiskLevel"]

    style Input fill:#fff3cd
    style Rule1 fill:#e2f0ff
    style Rule2 fill:#e2f0ff
    style AC fill:#ccffcc
    style Impl fill:#d1ecf1
    style RL fill:#ffe2e2
```

**10 Annex III Purposes:**
1. BiometricIdentification
2. EducationAccess
3. HealthCare
4. JudicialDecisionSupport
5. LawEnforcementSupport
6. MigrationControl
7. PublicServiceAllocation
8. RecruitmentOrEmployment
9. WorkforceEvaluationPurpose
10. CriticalInfrastructureOperation

### Mechanism 2: Article 6(3) (Expert Judgment → Manual Criteria)

**Regulatory Basis**: EU AI Act Article 6(3) for residual/unforeseen risks

```mermaid
graph TD
    Expert["Expert Evaluation:<br/>Identifies unforeseen risk"]

    API["PUT /systems/{urn}/<br/>manually-identified-criteria"]

    Expert -->|submits| API

    API -->|backend receives| MIC["hasManuallyIdentifiedCriterion<br/>(ContextualCriterion)"]

    MIC -->|derive_requirements_from_criteria| Req["Automatic Requirement Derivation"]

    Req -->|traverses| REQ["Criterion.activatesRequirement"]
    REQ -->|merges with auto| CR["hasComplianceRequirement<br/>(merged set)"]

    MIC -->|ontology traversal| Risk["Risk Determination"]
    Risk -->|assignsRiskLevel| RL["hasRiskLevel<br/>(usually HighRisk)"]

    CR -->|persist| MongoDB["MongoDB (system doc)"]
    CR -->|persist| Fuseki["Fuseki (RDF triple)"]

    style Expert fill:#fff3cd
    style API fill:#e2f0ff
    style MIC fill:#ccffcc
    style Req fill:#d1ecf1
    style CR fill:#d1ecf1
    style Risk fill:#ffe2e2
    style MongoDB fill:#f0f0f0
    style Fuseki fill:#f0f0f0
```

**15 Article 6(3) Contextual Criteria:**
1. ChildrenAndMinorsRiskCriterion
2. ElderlyAndDisabledRiskCriterion
3. SocioeconomicVulnerabilityRiskCriterion
4. AutonomousDecisionmakingRiskCriterion
5. RealTimeAutonomousRiskCriterion
6. WidespreadSystemicImpactRiskCriterion
7. CriticalInfrastructureInterdependencyRiskCriterion
8. BlackBoxDecisionRiskCriterion
9. HighStakesDecisionWithoutAppealRiskCriterion
10. HistoricalBiasReplicationRiskCriterion
11. ProtectedCharacteristicInferenceRiskCriterion
12. BiometricDataSensitivityRiskCriterion
13. PersonalDataRetentionRiskCriterion
14. LargeScaleEnvironmentalImpactRiskCriterion
15. MisinformationAmplificationRiskCriterion

### Mechanism 3: Articles 51-55 (Capability-Based → GPAI Classification)

**Regulatory Basis**: EU AI Act Articles 51-55 for General Purpose AI systemic risk

```mermaid
graph TD
    Input["System Capabilities:<br/>parameterCount, modelScale,<br/>autonomyLevel, isGenerallyApplicable"]

    PythonDerivation["Python Derivation:<br/>derive_capability_metrics"]

    Input -->|evaluate| PythonDerivation

    PythonDerivation -->|threshold check| HPC["HighParameterCount<br/>(>10B)"]
    PythonDerivation -->|explicit check| FMC["FoundationModelCapability<br/>(hasModelScale)"]
    PythonDerivation -->|evaluation check| FAC["FullyAutonomousCapability<br/>(autonomyLevel)"]
    PythonDerivation -->|context check| RTC["RealTimeProcessingCapability"]
    PythonDerivation -->|assessment check| GAC["GenerallyApplicableCapability<br/>(multi-domain)"]

    HPC -->|result| SCC["hasCapabilityMetric<br/>(SystemCapabilityCriterion)"]
    FMC -->|result| SCC
    FAC -->|result| SCC
    RTC -->|result| SCC
    GAC -->|result| SCC

    SCC -->|if sufficient| GPAI["hasGPAIClassification<br/>= GeneralPurposeAI"]

    GPAI -->|activates| GPAI_Req["GPAI-Specific Requirements:<br/>Articles 51-55"]

    GPAI_Req --> PR["GPAIProviderObligationRequirement"]
    GPAI_Req --> TR["GPAITransparencyRequirement"]
    GPAI_Req --> DQR["GPAIDataQualityRequirement"]
    GPAI_Req --> PMR["GPAIPerformanceMonitoringRequirement"]
    GPAI_Req --> DR["GPAIDocumentationRequirement"]

    style Input fill:#fff3cd
    style PythonDerivation fill:#e2f0ff
    style SCC fill:#ccffcc
    style GPAI fill:#ffe2e2
    style GPAI_Req fill:#d1ecf1
```

**5 Capability Metrics:**
1. HighParameterCount (>10 billion parameters)
2. FoundationModelCapability (explicitly foundation model)
3. FullyAutonomousCapability (no human-in-loop)
4. RealTimeProcessingCapability (real-time inference)
5. GenerallyApplicableCapability (adaptable to any domain)

---

## Reasoning Chains

### Example 1: Education System Reasoning

```mermaid
graph TD
    IN1["Input:<br/>hasPurpose = EducationAccess<br/>hasDeploymentContext = Education<br/>hasTrainingDataOrigin = ExternalDataset"]

    R1["SWRL Rule:<br/>Purpose.activatesCriterion"]
    R2["SWRL Rule:<br/>Context.triggersCriterion"]
    R3["SWRL Rule:<br/>ExternalDataset.requiresDataGov"]

    IN1 -->|check| R1
    IN1 -->|check| R2
    IN1 -->|check| R3

    R1 -->|activate| EC["EducationEvaluationCriterion"]
    R2 -->|activate| EC
    R3 -->|activate| DGR["DataGovernanceRequirement"]

    EC -->|traversal| ECR["Criterion.activatesRequirement"]
    ECR -->|derive| ACC["AccuracyEvaluationRequirement"]
    ECR -->|derive| HOR["HumanOversightRequirement"]
    ECR -->|derive| POM["ProtectionOfMinorsRequirement"]
    ECR -->|derive| TR["TraceabilityRequirement"]

    EC -->|assignment| RiskR["Criterion.assignsRiskLevel"]
    RiskR -->|assign| HR["HighRisk"]

    ACC -->|final state| OUT["hasComplianceRequirement:<br/>AccuracyEvaluation,<br/>HumanOversight,<br/>ProtectionOfMinors,<br/>TraceabilityRequirement,<br/>DataGovernanceRequirement<br/><br/>hasRiskLevel:<br/>HighRisk"]
    HOR -->|final state| OUT
    POM -->|final state| OUT
    TR -->|final state| OUT
    DGR -->|final state| OUT

    style IN1 fill:#fff3cd
    style R1 fill:#e2f0ff
    style R2 fill:#e2f0ff
    style R3 fill:#e2f0ff
    style EC fill:#ccffcc
    style OUT fill:#d1ecf1
    style HR fill:#ffe2e2
```

### Example 2: Biometric + Article 6(3) Reasoning

```mermaid
graph TD
    IN1["Input:<br/>hasPurpose = BiometricIdentification<br/>hasDeploymentContext = PublicSpaces"]

    AutoR["Automatic (Annex III)"]
    R1["BiometricIdentification<br/>.activatesCriterion"]
    R2["PublicSpaces<br/>.triggersCriterion"]

    IN1 -->|SWRL| AutoR
    AutoR -->|fire| R1
    AutoR -->|fire| R2

    R1 -->|derive| BIC["BiometricIdentificationCriterion"]
    R2 -->|derive| BIC

    BIC -->|activate| BIC_Req["DataGovernanceRequirement<br/>FundamentalRightsAssessment<br/>HumanOversightRequirement<br/>BiometricSecurityRequirement"]
    BIC -->|assign| HR1["HighRisk"]

    ManualInput["Expert Review:<br/>Identifies additional risk:<br/>MassPublicSurveillance"]

    API["PUT /systems/{urn}/<br/>manually-identified-criteria"]

    ManualInput -->|submit| API

    MIC["ChildrenAndMinorsRiskCriterion<br/>+ RealTimeAutonomousRiskCriterion"]

    API -->|receive| MIC

    MIC -->|derive_requirements| MIC_Req["ProtectionOfMinorsRequirement<br/>HumanOversightRequirement (merge)"]

    BIC_Req -->|merge with| Final_Req["Final hasComplianceRequirement:<br/>DataGovernance<br/>FundamentalRightsAssessment<br/>HumanOversight (merged)<br/>BiometricSecurity<br/>ProtectionOfMinors"]
    MIC_Req -->|merge with| Final_Req

    Final_Req -->|persist| MongoDB["MongoDB + Fuseki"]

    HR1 -->|confirmed| FinalRisk["hasRiskLevel = HighRisk"]

    style IN1 fill:#fff3cd
    style AutoR fill:#e2f0ff
    style BIC fill:#ccffcc
    style ManualInput fill:#fff3cd
    style MIC fill:#ccffcc
    style Final_Req fill:#d1ecf1
    style FinalRisk fill:#ffe2e2
```

### Example 3: Foundation Model (GPAI) Reasoning

```mermaid
graph TD
    IN["Input:<br/>hasPurpose = GeneralPurposeLLM<br/>parameterCount = 1,000,000,000,000<br/>hasModelScale = FoundationModelScale<br/>autonomyLevel = FullyAutonomous<br/>isGenerallyApplicable = true<br/>hasDeploymentContext = RealTimeProcessing"]

    CapMetrics["Python: derive_capability_metrics()"]

    IN -->|evaluate| CapMetrics

    CapMetrics -->|parameterCount > 10B| HPC["HighParameterCount ✓"]
    CapMetrics -->|hasModelScale = Foundation| FMC["FoundationModelCapability ✓"]
    CapMetrics -->|autonomyLevel = Fully| FAC["FullyAutonomousCapability ✓"]
    CapMetrics -->|RealTimeProcessing| RTC["RealTimeProcessingCapability ✓"]
    CapMetrics -->|isGenerallyApplicable = true| GAC["GenerallyApplicableCapability ✓"]

    HPC -->|collect| CMCollection["hasCapabilityMetric:<br/>[HPC, FMC, FAC, RTC, GAC]"]
    FMC -->|collect| CMCollection
    FAC -->|collect| CMCollection
    RTC -->|collect| CMCollection
    GAC -->|collect| CMCollection

    CMCollection -->|sufficient metrics| GPAI["hasGPAIClassification<br/>= GeneralPurposeAI ✓"]

    GPAI -->|automatic| GPAIReq["Articles 51-55 Requirements<br/>GPAIProviderObligation<br/>GPAITransparency<br/>GPAIDataQuality<br/>GPAIPerformanceMonitoring<br/>GPAIDocumentation"]

    CMCollection -->|ontology traversal| SystemicReq["SystemicRiskAssessmentCriterion<br/>.activatesRequirement<br/>→ AdditionalGPAIRequirements"]

    GPAIReq -->|merge| Final["hasComplianceRequirement:<br/>All GPAI + Systemic Requirements"]
    SystemicReq -->|merge| Final

    Final -->|persist| Store["MongoDB + Fuseki"]

    GPAI -->|classification| Risk["hasRiskLevel<br/>= HighRisk"]

    style IN fill:#fff3cd
    style CapMetrics fill:#e2f0ff
    style HPC fill:#ccffcc
    style FMC fill:#ccffcc
    style FAC fill:#ccffcc
    style RTC fill:#ccffcc
    style GAC fill:#ccffcc
    style GPAI fill:#ffe2e2
    style GPAIReq fill:#d1ecf1
    style Risk fill:#ffe2e2
```

---

## Data Flow

### Complete System Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend as Backend<br/>API
    participant Derivation as Derivation<br/>Engine
    participant Reasoner as Reasoner<br/>Service
    participant MongoDB
    participant Fuseki

    User->>Frontend: Create AI System
    Frontend->>Backend: POST /systems/

    Backend->>Backend: SHACL Validation (PRE)
    alt Validation Fails
        Backend->>Frontend: Error Response
        Frontend->>User: Display Errors
    else Validation Passes
        Backend->>Derivation: Extract Purpose,<br/>Context, Data

        Derivation->>Derivation: SWRL Rule 1<br/>(Purpose.activates)
        Derivation->>Derivation: SWRL Rule 2<br/>(Context.triggers)
        Derivation->>Derivation: Derive criteria

        Derivation->>Derivation: derive_requirements_<br/>from_criteria()
        Derivation->>Derivation: collect all<br/>activated requirements

        Derivation->>Backend: Return: criteria +<br/>requirements + risk

        Backend->>Reasoner: POST /reason<br/>(RDF+SWRL)

        Reasoner->>Reasoner: Load ontology
        Reasoner->>Reasoner: Apply SWRL rules
        Reasoner->>Reasoner: Infer relationships

        Reasoner->>Backend: Return inferred RDF

        Backend->>Backend: SHACL Validation (POST)

        Backend->>MongoDB: Save system doc
        Backend->>Fuseki: Insert RDF triples

        Backend->>Frontend: Return complete<br/>system + inferences
        Frontend->>User: Display results
    end
```

### Requirements Derivation Flow

```mermaid
graph TD
    Start["Starting with:<br/>hasPurpose = BiometricIdentification"]

    Step1["Step 1: Query Ontology<br/>BiometricIdentification<br/>.activatesCriterion"]
    Step2["Result:<br/>BiometricIdentificationCriterion"]

    Step3["Step 2: Query Ontology<br/>BiometricIdentificationCriterion<br/>.activatesRequirement"]

    Step4a["Result<br/>DataGovernanceRequirement"]
    Step4b["Result<br/>FundamentalRightsAssessment"]
    Step4c["Result<br/>HumanOversightRequirement"]
    Step4d["Result<br/>BiometricSecurityRequirement"]
    Step4e["Result<br/>TransparencyRequirement"]

    Step5["Step 3: Merge Results"]
    Final["hasComplianceRequirement:<br/>[DataGov, FundamentalRights,<br/>HumanOversight, BiometricSec,<br/>Transparency]"]

    Start -->|query| Step1
    Step1 -->|derives| Step2
    Step2 -->|query| Step3
    Step3 -->|finds| Step4a
    Step3 -->|finds| Step4b
    Step3 -->|finds| Step4c
    Step3 -->|finds| Step4d
    Step3 -->|finds| Step4e

    Step4a -->|collect| Step5
    Step4b -->|collect| Step5
    Step4c -->|collect| Step5
    Step4d -->|collect| Step5
    Step4e -->|collect| Step5

    Step5 -->|output| Final

    style Start fill:#fff3cd
    style Step2 fill:#ccffcc
    style Final fill:#d1ecf1
```

---

## Examples

### Example 1: Simple Education System

**Input:**
```json
{
  "hasName": "StudentGradeAnalyzer",
  "hasPurpose": ["ai:EducationAccess"],
  "hasDeploymentContext": ["ai:Education"],
  "hasTrainingDataOrigin": ["ai:InternalDataset"],
  "hasAlgorithmType": ["ai:NeuralNetwork"],
  "hasVersion": "1.0"
}
```

**Reasoning Process:**

1. **Purpose Rule Fires**
   - `ai:EducationAccess` activates `ai:EducationEvaluationCriterion`

2. **Context Rule Fires**
   - `ai:Education` triggers `ai:EducationEvaluationCriterion`

3. **Additional Rule Fires** (Protection of Minors)
   - Education + minor risk → `ai:ProtectionOfMinorsRiskCriterion`

4. **Requirement Derivation**
   - `ai:EducationEvaluationCriterion` activates:
     - `ai:AccuracyEvaluationRequirement`
     - `ai:HumanOversightRequirement`
     - `ai:TraceabilityRequirement`
     - `ai:DataGovernanceRequirement`
   - `ai:ProtectionOfMinorsRiskCriterion` activates:
     - `ai:ProtectionOfMinorsRequirement`
     - `ai:ParentalConsentRequirement`

5. **Risk Assignment**
   - Both criteria assign `ai:HighRisk`

**Output:**
```json
{
  "urn": "urn:uuid:student-grade-analyzer-12345",
  "hasActivatedCriterion": [
    "ai:EducationEvaluationCriterion",
    "ai:ProtectionOfMinorsRiskCriterion"
  ],
  "hasComplianceRequirement": [
    "ai:AccuracyEvaluationRequirement",
    "ai:HumanOversightRequirement",
    "ai:TraceabilityRequirement",
    "ai:DataGovernanceRequirement",
    "ai:ProtectionOfMinorsRequirement",
    "ai:ParentalConsentRequirement"
  ],
  "hasRiskLevel": "ai:HighRisk",
  "totalInferences": 6
}
```

### Example 2: Biometric System with Expert Override

**Input (Automatic):**
```json
{
  "hasName": "AirportBiometricSystem",
  "hasPurpose": ["ai:BiometricIdentification"],
  "hasDeploymentContext": ["ai:Migration", "ai:PublicSpaces"],
  "hasTrainingDataOrigin": ["ai:ExternalDataset"],
  "hasVersion": "2.1"
}
```

**Automatic Requirements:**
- DataGovernance, FundamentalRights, HumanOversight, BiometricSecurity, Transparency
- **Risk:** HighRisk

**Expert Adds (Article 6(3)):**
```json
{
  "hasManuallyIdentifiedCriterion": [
    "ai:ChildrenAndMinorsRiskCriterion",
    "ai:RealTimeAutonomousRiskCriterion"
  ]
}
```

**Additional Requirements from Manual Criteria:**
- ProtectionOfMinors (merges HumanOversight)
- RealTimeProcessingCapabilityRequirement

**Final Output:**
```json
{
  "hasActivatedCriterion": [
    "ai:BiometricIdentificationCriterion",
    "ai:MigrationBorderCriterion"
  ],
  "hasManuallyIdentifiedCriterion": [
    "ai:ChildrenAndMinorsRiskCriterion",
    "ai:RealTimeAutonomousRiskCriterion"
  ],
  "hasComplianceRequirement": [
    "ai:DataGovernanceRequirement",
    "ai:FundamentalRightsAssessmentRequirement",
    "ai:HumanOversightRequirement",
    "ai:BiometricSecurityRequirement",
    "ai:TransparencyRequirement",
    "ai:ProtectionOfMinorsRequirement",
    "ai:RealTimeProcessingCapabilityRequirement"
  ],
  "hasRiskLevel": "ai:HighRisk"
}
```

### Example 3: Foundation Model (GPAI)

**Input:**
```json
{
  "hasName": "LargeLanguageModel-XL",
  "hasPurpose": ["ai:GeneralPurposeLLM"],
  "parameterCount": 1000000000000,
  "hasModelScale": "ai:FoundationModelScale",
  "autonomyLevel": "FullyAutonomous",
  "isGenerallyApplicable": true,
  "hasDeploymentContext": ["ai:RealTimeProcessing"]
}
```

**Capability Analysis:**
- HighParameterCount: 1T > 10B ✓
- FoundationModelCapability: Explicit ✓
- FullyAutonomousCapability: No human oversight ✓
- RealTimeProcessingCapability: Real-time inference ✓
- GenerallyApplicableCapability: Adaptable to all domains ✓

**Output:**
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
  "hasComplianceRequirement": [
    "ai:GPAIProviderObligationRequirement",
    "ai:GPAITransparencyRequirement",
    "ai:GPAIDataQualityRequirement",
    "ai:GPAIPerformanceMonitoringRequirement",
    "ai:GPAIDocumentationRequirement",
    "ai:ModelEvaluationRequirement",
    "ai:PostMarketMonitoringRequirement"
  ],
  "hasRiskLevel": "ai:HighRisk"
}
```

---

## Query Patterns

### SPARQL Query Examples

#### Query 1: Find All Systems in HighRisk Category

```sparql
PREFIX ai: <http://ai-act.eu/ai#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?system ?name ?purpose ?context
WHERE {
  ?system rdf:type ai:IntelligentSystem ;
          ai:hasName ?name ;
          ai:hasRiskLevel ai:HighRisk ;
          ai:hasPurpose ?purpose ;
          ai:hasDeploymentContext ?context .
}
```

#### Query 2: Find All Requirements for Biometric Systems

```sparql
PREFIX ai: <http://ai-act.eu/ai#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?system ?requirement ?label
WHERE {
  ?system rdf:type ai:IntelligentSystem ;
          ai:hasPurpose ai:BiometricIdentification ;
          ai:hasComplianceRequirement ?requirement .
  ?requirement rdfs:label ?label .
}
```

#### Query 3: Find Systems Missing Security Requirements

```sparql
PREFIX ai: <http://ai-act.eu/ai#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?system ?name
WHERE {
  ?system rdf:type ai:IntelligentSystem ;
          ai:hasName ?name ;
          ai:hasRiskLevel ai:HighRisk .

  # Find high-risk systems
  ?system ai:hasActivatedCriterion ?criterion .

  # Criterion should activate security requirement
  ?criterion ai:activatesRequirement ai:SecurityRequirement .

  # But system doesn't have it
  MINUS {
    ?system ai:hasComplianceRequirement ai:SecurityRequirement .
  }
}
```

#### Query 4: Find All GPAI Models

```sparql
PREFIX ai: <http://ai-act.eu/ai#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?system ?name ?paramCount
WHERE {
  ?system rdf:type ai:IntelligentSystem ;
          ai:hasName ?name ;
          ai:hasGPAIClassification ai:GeneralPurposeAI ;
          ai:hasFLOPS ?paramCount .
}
ORDER BY DESC(?paramCount)
```

#### Query 5: Compliance Coverage Analysis

```sparql
PREFIX ai: <http://ai-act.eu/ai#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?system ?name (COUNT(?criterion) as ?activatedCriteria)
       (COUNT(?requirement) as ?requirements)
WHERE {
  ?system rdf:type ai:IntelligentSystem ;
          ai:hasName ?name .

  OPTIONAL {
    ?system ai:hasActivatedCriterion ?criterion .
  }

  OPTIONAL {
    ?system ai:hasComplianceRequirement ?requirement .
  }
}
GROUP BY ?system ?name
```

---

## Appendix: Namespace and Prefixes

```turtle
@prefix ai: <http://ai-act.eu/ai#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix swrl: <http://www.w3.org/2003/11/swrl#> .
@prefix airo: <https://w3id.org/airo#> .
@prefix dct: <http://purl.org/dc/terms/> .
```

---

**Version**: 0.37.2 | **Last Updated**: 2025-11-24 | **Status**: Production Ready
