# 📝 CHANGELOG - AI Act Ontology

All notable changes to the AI Act Ontology project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.37.5] - 2025-12-23

### 🔗 EUROPEAN LEGISLATION IDENTIFIER (ELI) INTEGRATION

Complete integration with [European Legislation Identifier (ELI)](https://eur-lex.europa.eu/eli-register/about.html) for EUR-Lex interoperability and persistent legislation references.

#### ✅ ELI Integration

- **New Prefix**: `eli: <http://data.europa.eu/eli/ontology#>`
- **Property**: `eli:cites` linking ontology concepts to EUR-Lex URIs
- **Reference Standards**: Council Conclusions 2012/C 325/02, Decision (EU) 2017/1191

#### 🔗 ELI URIs Added

**Article 5 - Prohibited Practices**:
| Criterion/Requirement | ELI URI |
|----------------------|---------|
| SubliminalManipulationCriterion | `art_5/par_1/pnt_a/oj` |
| VulnerabilityExploitationCriterion | `art_5/par_1/pnt_b/oj` |
| SocialScoringCriterion | `art_5/par_1/pnt_c/oj` |
| PredictivePolicingProfilingCriterion | `art_5/par_1/pnt_d/oj` |
| RealTimeBiometricIdentificationCriterion | `art_5/par_1/pnt_h/oj` |
| VictimSearchException | `art_5/par_2/pnt_a/oj` |
| TerroristThreatException | `art_5/par_2/pnt_b/oj` |
| SeriousCrimeException | `art_5/par_2/pnt_c/oj` |
| All Art. 5.2 Requirements | `art_5/par_2/oj` |

**High-Risk Requirements**:
| Requirement | Article | ELI URI |
|-------------|---------|---------|
| RiskManagementRequirement | Art. 9 | `art_9/oj` |
| DataGovernanceRequirement | Art. 10 | `art_10/oj` |
| NonDiscriminationRequirement | Art. 10(2)(f) | `art_10/par_2/pnt_f/oj` |
| DocumentationRequirement | Art. 11 | `art_11/oj` |
| TraceabilityRequirement | Art. 12 | `art_12/oj` |
| TransparencyRequirement | Art. 13 | `art_13/oj` |
| HumanOversightRequirement | Art. 14 | `art_14/oj` |
| AccuracyEvaluationRequirement | Art. 15 | `art_15/oj` |
| RobustnessRequirement | Art. 15 | `art_15/oj` |
| SecurityRequirement | Art. 15 | `art_15/oj` |
| FundamentalRightsAssessmentRequirement | Art. 27 | `art_27/oj` |
| GPAITransparencyRequirement | Art. 53 | `art_53/oj` |

**ELI Base URI**: `http://data.europa.eu/eli/reg/2024/1689`

#### 📁 Files Modified

- `versions/0.37.4/ontologia-v0.37.4.ttl` → v0.37.5
- `mappings/dpv-integration.ttl` → v0.2.0
- `json-ld-context.json` - Added `eli:` prefix and `eli:cites` property
- `forensic_agent/app/services/evidence_planner.py` - Added `eli_uri` field
- `forensic_agent/app/services/persistence.py` - ELI serialization in Turtle

#### 🎯 Benefits

1. **EUR-Lex Interoperability**: Direct dereferenceable links to official legislation
2. **Persistent Identifiers**: URIs survive legislative consolidations
3. **Semantic Web Compliance**: Standard EU vocabulary for legislation references
4. **Audit Trail**: Machine-readable links for compliance verification

---

## [0.37.4] - 2025-12-14

### 🔗 W3C DPV 2.2 INTEGRATION

Complete integration with [W3C Data Privacy Vocabulary (DPV) 2.2](https://w3c.github.io/dpv/) for compliance evidence planning and documentation.

#### ✅ DPV Integration Module (`mappings/dpv-integration.ttl`)

- **New Ontology Module**: `dpv-integration.ttl` (v0.1.0)
  - Namespace declarations for DPV 2.2 extensions
  - Mappings between AI Act requirements and DPV Technical/Organizational Measures
  - Evidence types for compliance documentation
  - Risk-to-measure mappings for Evidence Planner Agent

- **DPV Namespaces Integrated**:
  - `dpv:` - Core DPV vocabulary
  - `dpv-ai:` - AI-specific concepts
  - `dpv-risk:` - Risk management
  - `dpv-tech:` - Technical measures
  - `dpv-legal-eu-aiact:` - EU AI Act legal concepts
  - `dpv-legal-eu-gdpr:` - GDPR concepts

- **6 Evidence Types Defined**:
  | Type | Description | Examples |
  |------|-------------|----------|
  | `PolicyEvidence` | Policies and procedures | Human Oversight Policy |
  | `TechnicalEvidence` | Technical documentation | Model Card, System Architecture |
  | `AuditEvidence` | Logs, tests, audits | Bias Audit Report |
  | `TrainingEvidence` | Training records | Operator Training Records |
  | `AssessmentEvidence` | Impact assessments | FRIA Report, DPIA |
  | `ContractualEvidence` | Contracts and agreements | Data Processing Agreement |

- **14 Requirement-to-Measure Mappings**:
  | Requirement | Article | DPV Measure | Evidence Items |
  |-------------|---------|-------------|----------------|
  | HumanOversightRequirement | Art. 14 | `dpv:HumanInvolvement` | 3 items |
  | TransparencyRequirement | Art. 13 | `dpv:Transparency` | 3 items |
  | FundamentalRightsAssessmentRequirement | Art. 27 | `dpv:ImpactAssessment` | 3 items |
  | DataGovernanceRequirement | Art. 10 | `dpv:DataGovernancePolicies` | 3 items |
  | DocumentationRequirement | Art. 11 | `dpv:RecordsOfActivities` | 3 items |
  | RiskManagementRequirement | Art. 9 | `dpv:RiskManagementPlan` | 3 items |
  | NonDiscriminationRequirement | Art. 10 | `dpv:BiasAssessment` | 3 items |
  | AccuracyEvaluationRequirement | Art. 15 | `dpv:ReviewProcedure` | 3 items |
  | RobustnessRequirement | Art. 15 | `dpv:SecurityAssessment` | 3 items |
  | TraceabilityRequirement | Art. 12 | `dpv:RecordsOfActivities` | 3 items |
  | SecurityRequirement | Art. 15 | `dpv:TechnicalSecurityMeasure` | 3 items |
  | GPAITransparencyRequirement | Art. 52 | `dpv:Transparency` | 3 items |
  | ProtectionOfMinorsRequirement | - | `dpv:ChildrenDataProtection` | 3 items |

- **DPV-Legal EU AI Act Alignments**:
  - `ai:ComplianceRequirement` ↔ `dpv-legal-eu-aiact:AIActRequirement`
  - `ai:HighRisk` ↔ `dpv-legal-eu-aiact:RiskLevelHigh`
  - `ai:MinimalRisk` ↔ `dpv-legal-eu-aiact:RiskLevelMinimal`
  - `ai:Unacceptable` ↔ `dpv-legal-eu-aiact:RiskLevelProhibited`
  - `ai:AIDeployer` ↔ `dpv-legal-eu-aiact:AIDeployer`
  - `ai:AIDeveloper` ↔ `dpv-legal-eu-aiact:AIProvider`

- **Evidence Plan Class**:
  - `ai:EvidencePlan` - Structured plan for generating compliance evidence
  - Properties: `hasGap`, `hasEvidenceItem`, `planPriority`, `planDeadline`, `responsibleRole`

#### 🖥️ DPV Browser (Frontend)

- **New Page**: `DPVPage.tsx` - Interactive W3C DPV 2.2 explorer
- **Route**: `/dpv`
- **Features**:
  - Browse DPV taxonomies: Risks, Measures, AI Act concepts
  - Search and filter DPV terms
  - View concept hierarchies and relationships
  - Link to official W3C DPV documentation

#### 📊 DPV Statistics

- **Total Evidence Items**: ~40 defined
- **Requirement Mappings**: 14 requirements → DPV measures
- **Evidence Types**: 6 categories
- **Properties Added**: 8 new (`requiresEvidence`, `mapsToDPVMeasure`, `evidenceDescription`, `evidencePriority`, `evidenceFrequency`, `hasGap`, `hasEvidenceItem`, `planPriority`, `planDeadline`, `responsibleRole`)

---

### 🚫 ARTICLE 5: PROHIBITED PRACTICES (UNACCEPTABLE RISK)

Complete implementation of EU AI Act Article 5 covering prohibited AI practices with unacceptable risk. Systems with these practices **CANNOT be deployed in the EU** (maximum penalties: €35M or 7% global annual turnover).

#### ✅ Added

- **ProhibitedPracticeCriterion** class (Article 5 - Unacceptable Risk)
  - New base class for AI practices that are absolutely prohibited
  - 5 prohibited practices as individuals with full bilingual support (ES/EN):
    1. **SubliminalManipulationCriterion** (Article 5.1.a) - Subliminal manipulation beyond conscious awareness
    2. **VulnerabilityExploitationCriterion** (Article 5.1.b) - Exploiting vulnerabilities (age, disability, economic situation)
    3. **SocialScoringCriterion** (Article 5.1.c) - Social scoring by public authorities
    4. **PredictivePolicingProfilingCriterion** (Article 5.1.d) - Crime prediction based solely on profiling
    5. **RealTimeBiometricIdentificationCriterion** (Article 5.1.h) - Real-time biometric ID in public spaces

- **Legal Exceptions** (Article 5.2) - Limited exceptions for real-time biometric identification only:
  - VictimSearchException (Article 5.2.a) - Search for kidnapping/trafficking victims
  - TerroristThreatException (Article 5.2.b) - Prevention of terrorist threats
  - SeriousCrimeException (Article 5.2.c) - Prosecution of serious crimes (3+ years imprisonment)
  - All exceptions require prior judicial authorization

- **New Ontology Properties**:
  - `ai:hasProhibitedPractice` - Links systems to prohibited practices
  - `ai:articleReference` - References specific article numbers
  - `ai:prohibitionScope` - Describes prohibition scope (absolute vs. with exceptions)
  - `ai:hasException` - Links to legal exceptions (only for real-time biometric)

- **New Requirements** (7 enforcement-related):
  - JudicialAuthorizationRequirement
  - ProportionalityAssessmentRequirement
  - TemporalSpatialLimitationRequirement
  - PublicRegistryNotificationRequirement
  - ProhibitionEnforcementRequirement
  - MarketWithdrawalRequirement
  - VulnerablePopulationProtectionRequirement

- **New Purposes** for prohibited practices:
  - SubliminalManipulation
  - BehaviorManipulation
  - SocialScoring
  - CrimeRiskPrediction

- **New Deployment Contexts**:
  - PublicSpaces (for biometric identification)
  - VulnerablePopulationContext (for exploitation detection)

- **New Algorithm Type**:
  - ProfilingAlgorithm (for predictive policing detection)

#### 🔧 Technical Implementation

- **Backend API** (`backend/main.py`):
  - New endpoint: `GET /vocab/prohibited_practices` - Returns all 5 prohibited practices with metadata
  - New endpoint: `GET /vocab/legal_exceptions` - Returns Article 5.2 exceptions

- **Backend Model** (`backend/models/system.py`):
  - Added `hasProhibitedPractice: List[str]` field
  - Added `hasLegalException: List[str]` field
  - Added `hasJudicialAuthorization: bool` field

- **Python Rules** (`ontologias/rules/base_rules.py`):
  - RULE_ART5_1A: Detects subliminal manipulation
  - RULE_ART5_1B: Detects vulnerability exploitation
  - RULE_ART5_1C: Detects social scoring
  - RULE_ART5_1D: Detects predictive policing by profiling
  - RULE_ART5_1H: Detects real-time biometric identification in public spaces
  - Total rules: 12 → 17 base rules

- **SWRL Rules** (`ontologias/rules/swrl-base-rules.ttl`):
  - Added 5 Article 5 detection rules (for documentation)
  - Total rules: 25 → 30
  - Updated to version 1.1.0-article5

- **Frontend** (`frontend/src/pages/SystemsPage.tsx`):
  - New Section 8: "Article 5: Prohibited Practices" with prominent red warning design
  - Multi-select for prohibited practices with real-time warnings
  - Conditional display of legal exceptions (only for real-time biometric ID)
  - Judicial authorization checkbox with validation
  - Warning badges showing deployment prohibition status

- **System Card** (`frontend/src/pages/SystemCard.tsx`):
  - Prominent red warning banner for prohibited practices
  - Display of legal exceptions and judicial authorization status
  - Clear indication of EU deployment prohibition

- **Forensic Agent** (`forensic_agent/app/models/incident.py`, `forensic_agent/app/services/incident_extractor.py`):
  - Added Article 5 fields to incident extraction model
  - Enhanced LLM extraction prompt with detailed Article 5 detection rules
  - Automatic detection of prohibited practices from incident narratives
  - Extraction of legal exceptions and judicial authorization status

#### 📊 Ontology Statistics (v0.37.4)

- **Triples**: 1,685 → 1,900+ (+215 triples including DPV integration)
- **Classes**: ProhibitedPracticeCriterion (1 new base + 5 individuals) + 7 Evidence classes
- **Properties**: 4 new Article 5 + 8 new DPV (total 12 new properties)
- **Requirements**: 7 new enforcement-related requirements
- **Purposes**: 4 new prohibited purposes
- **SWRL Rules**: 25 → 30 rules
- **Python Rules**: 12 → 17 base rules
- **API Endpoints**: 2 new vocabulary endpoints
- **DPV Mappings**: 14 requirement-to-measure mappings with ~40 evidence items
- **Frontend Pages**: 1 new (DPV Browser)

#### 🌍 Compliance & Standards

- ✅ **Bilingual**: All labels and comments in Spanish and English
- ✅ **EU AI Act Article 5**: Full implementation with legal exceptions
- ✅ **AIRO Compatible**: Follows AI Risk Ontology patterns
- ✅ **W3C DPV 2.2**: Full integration with Data Privacy Vocabulary
- ⚠️ **ISO/NIST Mappings**: Article 5 is EU-specific regulation, not mapped to ISO 42001 or NIST AI RMF
- ✅ **Validated**: Ontology successfully parsed with rdflib (1,900+ triples)

#### 🔍 Detection Logic

Systems are flagged with prohibited practices when:
1. **Subliminal Manipulation**: Purpose = `SubliminalManipulation`
2. **Vulnerability Exploitation**: Purpose = `BehaviorManipulation` + Context = `VulnerablePopulationContext`
3. **Social Scoring**: Purpose = `SocialScoring` (only applies to public authorities)
4. **Predictive Policing**: Purpose = `CrimeRiskPrediction` + Algorithm = `ProfilingAlgorithm`
5. **Real-time Biometric**: Purpose = `BiometricIdentification` + Context = `RealTimeProcessing` + Context = `PublicSpaces`

---

## [0.37.3] - 2025-12-12

### 🎯 FORENSIC BENCHMARK OPTIMIZATION

Major improvements to ontology requirement coverage validated against real-world AI incidents from the AIAAIC database.

#### ✅ Added

- **FairnessRequirement** class (Article 10 compliance)
  - New requirement class ensuring AI systems treat all individuals and groups fairly
  - Added to RecruitmentEmploymentCriterion, WorkforceEvaluationCriterion, EssentialServicesAccessCriterion
  - Covers discrimination prevention beyond bias detection

- **Enhanced EssentialServicesAccessCriterion**
  - Added BiasDetectionRequirement activation
  - Added RobustnessRequirement activation
  - Added AccuracyRequirement activation
  - Now covers fairness, accuracy, and robustness gaps in essential services

- **Enhanced SystemicRiskAssessmentCriterion**
  - Added AccuracyRequirement activation
  - Added AccuracyEvaluationRequirement activation
  - Better coverage for GPAI accuracy-related incidents

- **Enhanced DualUseRiskCriterion**
  - Added NonDiscriminationRequirement activation
  - Added FundamentalRightsAssessmentRequirement activation
  - Improved coverage for employment/transparency dual issues

#### 📊 Benchmark Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Coverage (Primary KPI)** | 31.8% | 88.2% | **+56.4%** |
| True Positives | 19 | 30 | +11 |
| Missed Requirements | 41 | 4 | -37 |

#### 🔧 Issue-Level Coverage

| Issue Category | Coverage |
|----------------|----------|
| Employment | 100% |
| Accuracy/reliability | 100% |
| Transparency | 94.4% |
| Fairness | 93.3% |
| Privacy/surveillance | 92.9% |
| Accountability | 80% |
| Safety | 66.7% |

#### 📋 Validated Against

- AIAAIC1886: Japanese AI anime posters (Safety)
- AIAAIC1049: Secret Invasion AI titles (Employment, Transparency)
- AIAAIC0131: Google Photos panorama fail (Accuracy)
- AIAAIC1312: Takaful poverty targeting (Fairness, Accuracy, Transparency)
- AIAAIC1876: AI robotic sentry rifle (Safety)
- AIAAIC0768: Amazon Ring privacy (Accountability, Privacy)
- AIAAIC069: Tesla autopilot collision (Safety, Accountability, Accuracy)
- AIAAIC0504: Deliveroo discrimination (Fairness, Employment, Accountability)
- AIAAIC1970: Sweden fraud prediction (Fairness, Privacy, Accountability)
- AIAAIC1745: Starship robot incident (Safety, Accountability)

---

## [0.37.2] - 2025-11-22

### 🔗 UNIFIED NAMESPACE

- Consolidated all concepts from gpai:, ctx:, iso: merged into ai:
- All 14 GPAI concepts now under ai: (ai:GeneralPurposeAIModel, etc.)
- All 15 contextual criteria now under ai: (ai:ChildrenAndMinorsContext, etc.)
- All 9 ISO 42001 concepts now under ai: (ai:ISO42001SecurityRequirement, etc.)
- Fixed ai:DocumentationRequirement and ai:DataGovernanceRequirement class definitions
- Total: 100+ concepts unified in single namespace

---

## [0.37.1] - 2025-11-22

### 🎯 PHASE 1: CRITICAL IMPROVEMENTS

#### ✅ Added

- **WorkforceEvaluationPurpose** for Annex III point 2
  - Addresses critical gap in coverage of "Evaluation of Workers" systems
  - Includes WorkforceEvaluationCriterion with high-risk requirements
  - Activates non-discrimination, human oversight, auditability, documentation

- **Spanish Language Completion**
  - Added 100+ Spanish translations for algorithms and requirements
  - Improved coverage from 56% to 80% in critical areas
  - All new concepts include bilingual labels and descriptions

- **Semantic Distinction Documentation**
  - Clarified difference between `activatesCriterion` and `triggersCriterion`
  - `activatesCriterion`: Direct activation by Purpose
  - `triggersCriterion`: Contextual activation by DeploymentContext

- **OWL Cardinality Restrictions** (PHASE 2)
  - `IntelligentSystem` must have at least 1 Purpose
  - `IntelligentSystem` must have at least 1 TrainingDataOrigin
  - `Purpose` must activate at least 1 Criterion
  - `Criterion` must assign exactly 1 RiskLevel
  - `Criterion` must activate at least 1 Requirement
  - Enables automatic validation of system completeness

- **SHACL Validation Shapes** (PHASE 2)
  - Created `ai-act-shapes.ttl` with 7 shape definitions
  - Validates IntelligentSystem, Purpose, Criterion, Requirement, RiskLevel
  - Supports multilingual documentation requirements
  - Ensures Annex III coverage

- **Extended AIRO Mappings** (PHASE 2)
  - Expanded from 6 to 30+ mapped concepts
  - Added 10 `owl:equivalentClass` mappings
  - Added 8 subclass relationships
  - Added 15+ `seeAlso` relationships
  - Improved interoperability coverage from 9% to 67% potential

- **GPAI Requirements** (PHASE 2)
  - New `gpai-requirements.ttl` file
  - 15+ GPAI-specific requirements for Articles 51-55
  - GeneralPurposeAIModel class definition
  - SystemicRiskAssessmentCriterion for GPAI models
  - Dual-use risk evaluation
  - Post-market monitoring requirements
  - Annex VIII safeguards mapping

- **Advanced Contextual Criteria** (PHASE 3)
  - Created `advanced-contextual-criteria.ttl`
  - 15+ advanced context definitions:
    - Vulnerability dimensions (3): Children, Elderly/Disabled, Socioeconomic
    - Autonomy and control (3): Autonomous, Real-time
    - Systemic impact (2): Widespread, Infrastructure interdependency
    - Accountability (3): Black box, High-stakes, Appeals
    - Fairness/Bias (2): Historical bias, Protected characteristics
    - Privacy/Security (2): Biometric data, Data retention
    - Environmental/Societal (2): Environmental impact, Misinformation

- **ISO/IEC 42001 and NIST AI RMF Integration** (PHASE 3)
  - Created `iso-nist-mappings.ttl`
  - ISO 42001 sections 8.1-8.6 coverage
  - NIST AI RMF core functions (Govern, Map, Measure, Manage)
  - NIST failure modes mapping (5+ categories)
  - Cross-framework compliance matrix
  - 15+ integrated requirements

#### 🔧 Changed

- **Version Information**
  - Updated `owl:versionIRI` to v0.37.1
  - Updated `dct:created` to 2025-11-22
  - Enhanced version comments with detailed changelog

#### 🎨 Improved

- **Documentation Quality**
  - All new concepts include English and Spanish labels
  - Comments updated for clarity
  - Version history added for traceability

---

## [0.37.0] - 2025-11-16

### Added

- Complete EU AI Act Annex I algorithm taxonomy
  - Machine Learning: 19 types (Supervised, Unsupervised, Reinforcement)
  - Knowledge-Based: 5 types
  - Statistical: 2 types
  - Coverage: 92.9% of known algorithms

- New properties for model scale and system capabilities
  - `hasFLOPS` for computational requirements
  - `hasSystemCapabilityCriteria` for capability-based evaluation

- AIRO (AI Risk Ontology) integration
  - 6 initial mappings to AIRO concepts
  - `owl:imports` AIRO ontology

- Annex III coverage improvements
  - 8/9 points covered (88.9%)
  - Only Workforce Evaluation (Point 2) missing in v0.37.0

### 📊 Statistics

| Component | v0.37.0 | v0.37.1 | v0.37.3 | v0.37.4 | Change |
|-----------|---------|---------|---------|---------|--------|
| **Clases OWL** | 46 | 46+ | 47+ | 54+ | +7 Evidence classes |
| **Object Properties** | 56 | 56+ | 56+ | 64+ | +8 DPV properties |
| **Data Properties** | 11 | 11+ | 11+ | 15+ | +4 evidence properties |
| **Mapped Concepts** | 6 | 30+ | 30+ | 44+ | +14 DPV mappings |
| **Spanish Coverage** | 56% | 80% | 80% | 85% | +5% |
| **Annex III Coverage** | 88.9% | 100% | 100% | 100% | complete |
| **Validation (SHACL)** | 0% | 70% | 70% | 70% | maintained |
| **OWL Restrictions** | 0% | 100% | 100% | 100% | maintained |
| **GPAI Support** | 0% | 95% | 95% | 95% | maintained |
| **Benchmark Coverage** | - | - | 88.2% | 88.2% | maintained |
| **DPV Integration** | - | - | - | 100% | **NEW** |
| **Evidence Types** | - | - | - | 6 | **NEW** |

---

## Version Evolution Roadmap

```
v0.37.0 (Nov 16, 2025)
    ↓ Patch Phase
v0.37.1 (Nov 22, 2025)
    └─ Phase 1: Critical fixes
       ├─ Workforce Evaluation Purpose
       ├─ Spanish completeness
       └─ Semantic clarification

v0.37.2 (Nov 22, 2025)
    └─ Unified namespace consolidation
       └─ All concepts under ai:

v0.37.3 (Dec 12, 2025)
    └─ Forensic Benchmark Optimization
       ├─ FairnessRequirement class
       ├─ Enhanced criterion activations
       └─ AIAAIC validation (88.2% coverage)

v0.37.4 (Dec 14, 2025) ← CURRENT
    └─ W3C DPV 2.2 Integration + Article 5
       ├─ dpv-integration.ttl module
       ├─ 14 requirement-to-measure mappings
       ├─ 6 evidence types (~40 items)
       ├─ DPV Browser frontend page
       ├─ Article 5 Prohibited Practices
       └─ 5 prohibition criteria + legal exceptions

v0.38.0 (Jan 2026) ← PLANNED
    └─ Phase 3: Completeness
       ├─ Advanced contextual criteria
       ├─ Extended ISO 42001 integration
       ├─ NIST AI RMF mapping expansion
       └─ Full versioning

v0.39.0 (Feb-Mar 2026)
    └─ Further refinements and standards integration
```

---

## Implementation Status

### ✅ COMPLETED

- [x] Annex III point 2 (Workforce Evaluation) - Purpose created
- [x] Spanish language coverage - 100+ terms translated
- [x] Semantic distinction documentation - activates vs triggers
- [x] OWL cardinality restrictions - 5+ key restrictions
- [x] SHACL shapes - 7 validation shapes defined
- [x] AIRO mappings - 30+ concepts mapped
- [x] GPAI requirements - 15+ articles 51-55 requirements
- [x] Advanced contextual criteria - 15+ scenarios
- [x] ISO/IEC 42001 integration - 8+ sections mapped
- [x] NIST AI RMF integration - 4 core functions + 5 failure modes
- [x] **Forensic benchmark validation** - 88.2% coverage on AIAAIC incidents
- [x] **FairnessRequirement** - New class for Article 10 compliance
- [x] **Enhanced criterion activations** - Better requirement coverage
- [x] **W3C DPV 2.2 Integration** - Full integration with Data Privacy Vocabulary
- [x] **Evidence Types** - 6 categories with ~40 evidence items
- [x] **Requirement-to-Measure Mappings** - 14 mappings to DPV measures
- [x] **DPV Browser** - Frontend page for exploring DPV taxonomy
- [x] **Article 5 Prohibited Practices** - 5 criteria with legal exceptions

### 🟡 IN PROGRESS

- [ ] Validation testing of SHACL shapes
- [ ] Integration documentation
- [ ] Backward compatibility verification
- [ ] Safety issue coverage improvements (currently 66.7%)

### 🟢 FUTURE

- [ ] GDPR alignment mappings (partial via dpv-legal-eu-gdpr)
- [ ] US AI Executive Order compliance
- [ ] UK AI Bill integration
- [ ] Additional language support (FR, DE, IT)
- [ ] Interactive validation tools
- [ ] Visualization enhancements
- [ ] Extended AIAAIC benchmark (50+ incidents)
- [ ] DPV-AI extension deep integration

---

## Versioning Scheme

This project follows Semantic Versioning:

- **MAJOR.MINOR.PATCH**
- **0.37.1**: Major=0 (pre-1.0), Minor=37 (regular releases), Patch=1 (bug fixes)
- Regular releases every 2-4 weeks
- Patch releases as needed for critical issues

---

## Documentation Files

### Core Ontology Files
- `versions/0.37.4/ontologia-v0.37.4.ttl` - Main ontology (current)
- `shacl/ai-act-shapes.ttl` - SHACL validation shapes
- `airo/airo-mappings-extended.ttl` - Extended AIRO mappings
- `gpai/gpai-requirements.ttl` - GPAI-specific requirements
- `contextual-criteria/advanced-contextual-criteria.ttl` - Advanced contexts
- `mappings/iso-42001-mappings.ttl` - ISO 42001 integration
- `mappings/nist-ai-rmf-mappings.ttl` - NIST AI RMF integration
- `mappings/dpv-integration.ttl` - **W3C DPV 2.2 integration (NEW)**

### Analysis Documents
- `ANALISIS_ONTOLOGIA_v0.37.0.md` - Detailed analysis
- `RESUMEN_ANALISIS.txt` - Executive summary
- `METRICAS_ANALISIS.md` - Metrics and charts
- `INDICE_ANALISIS.md` - Index and navigation

---

## Credits

### Contributors (v0.37.1 Phase 1-3 Implementation)
- Claude Code AI (Automated implementation)
- Analysis and recommendations (Comprehensive ontology review)

### Testing and Validation
- SHACL validation against AI Act requirements
- SPARQL query testing for consistency
- Cross-framework alignment verification

---

## Release Schedule

| Version | Date | Focus | Status |
|---------|------|-------|--------|
| 0.37.0 | Nov 16 | Algorithm taxonomy, AIRO | Released |
| 0.37.1 | Nov 22 | Critical fixes, translations | Released |
| 0.37.2 | Nov 22 | Unified namespace | Released |
| 0.37.3 | Dec 12 | Forensic benchmark optimization | Released |
| 0.37.4 | Dec 14 | W3C DPV 2.2, Article 5 Prohibited Practices | **Current** |
| 0.38.0 | Jan 2026 | Validation, GPAI, standards | Planned |
| 0.39.0 | Feb-Mar 2026 | Advanced criteria, integration | Planned |

---

## How to Use This Changelog

- Each version is marked with `[X.Y.Z]` format
- Sections are categorized: Added, Changed, Improved, Fixed, Removed, Deprecated, Security
- Use `###` headers for subheadings
- Link to issues/PRs when relevant
- Dates follow YYYY-MM-DD format

---

## Support

For questions about specific versions:
- Review the analysis documents for detailed explanations
- Check the main ontology file for definitions
- Consult the SHACL shapes for validation rules

---

**Last Updated:** 2025-12-14
**Maintained By:** Mariano Ortega de Mues
**Repository:** https://github.com/ai-act-project/
