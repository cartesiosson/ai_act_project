# EU AI Act Compliance Platform

> Automated semantic compliance evaluation system for AI systems under the EU AI Act framework

## 🎯 Overview

This platform implements an **automated semantic compliance evaluation system** for AI systems regulated by the EU AI Act. It combines a formal OWL ontology (v0.37.2) with SWRL inference rules to automatically derive compliance requirements, risk assessments, and regulatory obligations from system specifications.

**Key Innovation**: The system uses **hybrid semantic reasoning** (SWRL + SHACL validation) to automatically:
- ✅ Derive applicable criteria from system purpose and deployment context
- ✅ Activate compliance requirements based on identified criteria
- ✅ Assign risk levels according to EU AI Act classifications
- ✅ Validate system specifications against regulatory constraints
- ✅ Support forensic post-incident analysis (planned)

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [System Architecture](#️-system-architecture)
3. [Ontology Structure](#-ontology-structure)
4. [EU AI Act Compliance](#️-eu-ai-act-compliance)
5. [API Reference](#-api-reference)
6. [Project Structure](#-project-structure)
7. [Roadmap](#-roadmap)

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose**
- **Git**
- Available ports: 5173 (frontend), 8000 (backend), 8001 (reasoner), 3030 (Fuseki), 27017 (MongoDB), 80 (ontology docs)

### Installation

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
| **Frontend** | http://localhost:5173 | Web interface for system management |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation (Swagger) |
| **SPARQL Endpoint** | http://localhost:3030 | RDF/semantic queries (Fuseki) |
| **Ontology Docs** | http://localhost/docs | Formal ontology documentation |

---

## 🏗️ System Architecture

### Overview

```
┌─────────────────────────────────────────────────────────┐
│              React Frontend (5173)                       │
│      Interactive System Management Interface            │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTP/REST
┌───────────────────▼─────────────────────────────────────┐
│           FastAPI Backend (8000)                         │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ Core Logic       │  │ Routers                      │ │
│  │ - Derivation     │  │ - /systems                   │ │
│  │ - Requirements   │  │ - /reasoning (SHACL)         │ │
│  │ - Risk mapping   │  │ - /systems_fuseki            │ │
│  └──────────────────┘  └──────────────────────────────┘ │
└────────┬────────────┬──────────────┬────────────────────┘
         │            │              │
    MongoDB      Fuseki (3030)   Reasoner (8001)
    (27017)      RDF Store       SWRL Inference
    Documents    SPARQL          OwlReady2
```

### Core Services

| Service | Technology | Role |
|---------|-----------|------|
| **Frontend** | React 19, TypeScript, Vite | User interface for system registration |
| **Backend** | FastAPI, Python 3.11, RDFLib | Main API, derivation logic, SHACL validation |
| **Reasoner** | OwlReady2, Pellet | SWRL inference, semantic reasoning |
| **Fuseki** | Apache Jena Fuseki | RDF triplestore, SPARQL endpoint |
| **MongoDB** | MongoDB 6 | Document storage for systems |

---

## 🧠 Ontology Structure

### Current Version: v0.37.2

**Release Date:** 2025-11-22
**Namespace:** `http://ai-act.eu/ai#`
**Format:** Turtle (.ttl)

### File Organization

```
ontologias/
├── versions/
│   ├── 0.36.0/
│   │   └── ontologia-v0.36.0.ttl (82K) - Baseline with AIRO integration
│   ├── 0.37.0/
│   │   └── ontologia-v0.37.0.ttl (98K) - Algorithm taxonomy
│   ├── 0.37.1/
│   │   └── ontologia-v0.37.1.ttl (103K) - Critical improvements
│   └── 0.37.2/
│       └── ontologia-v0.37.2.ttl (92K) - ✅ ACTIVE (Unified namespace)
├── rules/
│   └── swrl-base-rules.ttl (9.8K) - ✅ ACTIVE SWRL rules
├── shacl/
│   └── ai-act-shapes.ttl (6.3K) - ✅ ACTIVE validation shapes
└── docs/
    ├── ontology.ttl (104K) - Widoco documentation
    └── provenance/ - Provenance metadata
```

### Key Concepts

#### 1. Central Entity: IntelligentSystem

```turtle
ai:IntelligentSystem
  ├─ hasName: string
  ├─ hasUrn: string (URN identifier)
  ├─ hasVersion: string
  ├─ hasPurpose → Purpose (primary function)
  ├─ hasDeploymentContext → DeploymentContext
  ├─ hasSystemCapabilityCriteria → Criterion (technical indicators)
  ├─ hasTrainingDataOrigin → TrainingDataOrigin
  ├─ hasAlgorithmType → AlgorithmType
  ├─ hasModelScale → ModelScale (Small/Regular/Foundation)
  └─ hasRiskLevel → RiskLevel (inferred)
```

#### 2. Semantic Derivation Chain

```
Purpose/Context
    ↓ activatesCriterion / triggersCriterion
Criterion
    ↓ assignsRiskLevel → RiskLevel
    ↓ activatesRequirement
ComplianceRequirement
```

#### 3. Risk Levels

| Level | Trigger | Requirements |
|-------|---------|--------------|
| **UnacceptableRisk** | Prohibited systems (social scoring) | ⛔ Banned |
| **HighRisk** | Annex III categories | 👤 Human oversight, 📊 Data governance, 🔒 Security |
| **LimitedRisk** | Transparency obligations | 👁️ User disclosure |
| **MinimalRisk** | General AI systems | ✅ Basic compliance |

#### 4. Compliance Requirements

Automatically derived categories:
- 🎯 **Accuracy Requirements** - Model performance validation
- 📝 **Documentation Requirements** - Traceability
- 👤 **Human Oversight Requirements** - Human-in-the-loop
- 🛡️ **Robustness Requirements** - System reliability
- 📊 **Data Governance** - Data quality & protection
- ⚖️ **Fundamental Rights** - Human dignity safeguards
- 🔒 **Security Requirements** - Cybersecurity measures
- 🌍 **Transparency Requirements** - Explainability

### Ontology Statistics (v0.37.2)

```
Classes: 50+
Object Properties: 30+
Data Properties: 15+
Named Individuals: 100+
Total Triples: ~1,800

Coverage:
✅ EU AI Act Annex III (8/8 high-risk categories)
✅ Articles 51-55 (GPAI requirements)
✅ Algorithm taxonomy (Annex I)
✅ Data governance framework
✅ SHACL validation shapes (7 shapes)
✅ SWRL inference rules (6 generic + domain-specific)
```

---

## ⚖️ EU AI Act Compliance

### Three Regulatory Mechanisms

The platform implements three distinct EU AI Act compliance mechanisms:

#### 1. **Annex III High-Risk Activities** → Automatic Classification

**Basis:** EU AI Act Annex III defines 8 high-risk AI categories based on purpose and context.

**Implementation:**
- SWRL rules in [rules/swrl-base-rules.ttl](ontologias/rules/swrl-base-rules.ttl)
- Automatic derivation via reasoner service
- Property: `hasActivatedCriterion`

**Example:**
```json
{
  "hasPurpose": ["ai:BiometricIdentification"],
  "hasDeploymentContext": ["ai:PublicSpaces"],
  "→ hasActivatedCriterion": ["ai:BiometricIdentificationCriterion"],
  "→ hasRiskLevel": "ai:HighRisk"
}
```

**Coverage:**
- ✅ Biometric identification
- ✅ Education/training evaluation
- ✅ Employment/recruitment
- ✅ Essential services access
- ✅ Law enforcement
- ✅ Migration/border control
- ✅ Administration of justice
- ✅ Critical infrastructure

#### 2. **Article 6(3) Residual Risk** → Expert Evaluation

**Basis:** EU AI Act Article 6(3) allows expert designation of high-risk systems not covered by Annex III.

**Implementation:**
- Backend endpoint: `PUT /systems/{urn}/manually-identified-criteria`
- Manual expert assessment
- Property: `hasManuallyIdentifiedCriterion`

**Example:**
```bash
curl -X PUT http://localhost:8000/systems/urn:uuid:abc/manually-identified-criteria \
  -H "Content-Type: application/json" \
  -d '{
    "hasManuallyIdentifiedCriterion": ["ai:DiscriminationRiskCriterion"]
  }'
```

#### 3. **Articles 51-55 GPAI** → Capability-Based Classification

**Basis:** EU AI Act Articles 51-55 define General Purpose AI (GPAI) models with systemic risk.

**Implementation:**
- Property: `hasModelScale` → FoundationModelScale
- Property: `hasGPAIClassification` → GeneralPurposeAI
- GPAI-specific requirements activated

**Example:**
```json
{
  "hasModelScale": ["ai:FoundationModelScale"],
  "→ hasGPAIClassification": ["ai:GeneralPurposeAI"],
  "→ hasComplianceRequirement": [
    "ai:GPAIProviderObligationRequirement",
    "ai:GPAITransparencyRequirement",
    "ai:SystemicRiskAssessmentRequirement"
  ]
}
```

---

## 🔧 API Reference

### Core Endpoints

#### Systems Management

```http
GET    /systems              # List all systems
POST   /systems              # Register new system
GET    /systems/{urn}        # Get system by URN
PUT    /systems/{urn}        # Update system
DELETE /systems/{urn}        # Delete system
```

#### Reasoning & Compliance

```http
POST   /reasoning/system/{system_id}  # Execute SWRL reasoning
GET    /reasoning/rules                # Get available SWRL rules
GET    /reasoning/status               # Check reasoner service status
GET    /reasoning/shacl/status         # Check SHACL validation status
```

#### Vocabulary

```http
GET /vocab/purposes           # Get available purposes
GET /vocab/contexts          # Get deployment contexts
GET /vocab/risks             # Get risk levels
GET /vocab/algorithmtypes    # Get algorithm types
GET /vocab/modelscales       # Get model scales
GET /vocab/gpai              # Get GPAI classifications
```

### Request Example

```bash
# Register a new AI system
curl -X POST http://localhost:8000/systems \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "FacialRecognitionSystem",
    "hasVersion": "1.0.0",
    "hasPurpose": ["ai:BiometricIdentification"],
    "hasDeploymentContext": ["ai:PublicSpaces"],
    "hasTrainingDataOrigin": ["ai:SyntheticDataset"],
    "hasAlgorithmType": ["ai:DeepLearning"]
  }'
```

### Response Example

```json
{
  "urn": "urn:uuid:550e8400-e29b-41d4-a716-446655440000",
  "hasName": "FacialRecognitionSystem",
  "hasRiskLevel": "ai:HighRisk",
  "hasActivatedCriterion": [
    "ai:BiometricIdentificationCriterion"
  ],
  "hasComplianceRequirement": [
    "ai:DataGovernanceRequirement",
    "ai:FundamentalRightsAssessmentRequirement",
    "ai:HumanOversightRequirement",
    "ai:TransparencyRequirement",
    "ai:BiometricSecurityRequirement"
  ]
}
```

---

## 📁 Project Structure

```
ai_act_project/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main API endpoints
│   ├── derivation.py          # Compliance derivation logic
│   ├── routers/
│   │   ├── systems.py         # Systems CRUD
│   │   ├── systems_fuseki.py  # Fuseki integration
│   │   └── reasoning.py       # SWRL reasoning + SHACL
│   ├── models/
│   │   └── system.py          # Pydantic models
│   └── swrl_rules.py          # SWRL rule definitions
├── frontend/                   # React + TypeScript UI
│   ├── src/
│   │   ├── pages/
│   │   │   └── SystemsPage.tsx
│   │   └── components/
│   └── vite.config.ts
├── reasoner_service/          # SWRL reasoning microservice
│   └── app/
│       └── main.py            # OwlReady2 reasoning
├── init_fuseki/               # Fuseki initialization
│   └── load_to_fuseki.py     # Load ontology to triplestore
├── ontologias/                # Ontology files
│   ├── versions/
│   │   └── 0.37.2/
│   │       └── ontologia-v0.37.2.ttl  # ✅ ACTIVE
│   ├── rules/
│   │   └── swrl-base-rules.ttl        # ✅ ACTIVE
│   ├── shacl/
│   │   └── ai-act-shapes.ttl          # ✅ ACTIVE
│   ├── docs/                  # Widoco documentation
│   └── CHANGELOG.md           # Version history
├── docker-compose.yml         # Service orchestration
├── .env                       # Configuration
└── README.md                  # This file
```

---

## 🗺️ Roadmap

### ✅ Completed (v0.37.2)

- [x] Unified ontology namespace (`ai:`)
- [x] GPAI classification (Articles 51-55)
- [x] SHACL validation (pre/post reasoning)
- [x] SWRL inference rules (6 generic rules)
- [x] Algorithm taxonomy (Annex I)
- [x] Spanish language support (80% coverage)
- [x] REST API with OpenAPI docs
- [x] React frontend for system registration
- [x] MongoDB + Fuseki dual storage
- [x] Docker containerization

### 🚧 In Progress

- [ ] **Forensic Analysis Agent** (Post-incident compliance auditing)
  - [ ] Incident extraction service (LLM-based)
  - [ ] SPARQL forensic queries
  - [ ] Compliance gap analyzer
  - [ ] Report generation

### 📅 Planned

- [ ] Advanced SHACL shapes (100% coverage)
- [ ] MCP (Model Context Protocol) integration
- [ ] AIRO ontology export/import
- [ ] ISO 42001 mappings
- [ ] NIST AI RMF alignment
- [ ] Automated penalty calculation
- [ ] Multi-language support (French, German)

---

## 📊 Key Features

### Current Capabilities

✅ **Automated Compliance Derivation**
- Automatic risk classification from system properties
- Inference of mandatory requirements via SWRL rules
- Support for Annex III + Article 6(3) + GPAI

✅ **Semantic Validation**
- Pre-reasoning SHACL validation
- Post-reasoning compliance checks
- Ontology constraint enforcement

✅ **Dual Storage Architecture**
- MongoDB for operational data
- Fuseki for semantic queries
- Automatic synchronization

✅ **Developer-Friendly API**
- OpenAPI/Swagger documentation
- RESTful endpoints
- JSON-LD support

✅ **Web Interface**
- System registration forms
- Compliance visualization
- Requirement tracking

### Technology Stack

**Backend:**
- Python 3.11
- FastAPI
- RDFLib (RDF/OWL processing)
- OwlReady2 (OWL reasoning)
- Motor (async MongoDB)

**Frontend:**
- React 19
- TypeScript
- Vite
- TailwindCSS

**Infrastructure:**
- Docker & Docker Compose
- Apache Jena Fuseki
- MongoDB 6
- NGINX

---

## 📝 Documentation

- **Ontology Changelog:** [ontologias/CHANGELOG.md](ontologias/CHANGELOG.md)
- **API Documentation:** http://localhost:8000/docs (when running)
- **Ontology Documentation:** http://localhost/docs (when running)
- **Forensic Analysis Design:** [old_info/FORENSIC_AGENT_ARCHITECTURE.md](old_info/FORENSIC_AGENT_ARCHITECTURE.md)
- **Post-Incident Analysis:** [old_info/POST_INCIDENT_ANALYSIS.md](old_info/POST_INCIDENT_ANALYSIS.md)

---

## 🤝 Contributing

This is a research/compliance platform under active development. Key areas for contribution:

1. **Ontology Enhancement:** Additional EU AI Act concepts, multilingual labels
2. **SWRL Rules:** New inference rules for compliance derivation
3. **SHACL Shapes:** Additional validation constraints
4. **Frontend:** UI/UX improvements, visualizations
5. **Forensic Agent:** LLM integration, incident analysis

---

## 📄 License

This project uses the EU AI Act ontology licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).

---

## 🔗 Related Resources

- **EU AI Act Official Text:** https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206
- **AIRO Ontology:** https://w3id.org/airo
- **Apache Jena Fuseki:** https://jena.apache.org/documentation/fuseki2/
- **OWL 2 Web Ontology Language:** https://www.w3.org/TR/owl2-overview/
- **SHACL (Shapes Constraint Language):** https://www.w3.org/TR/shacl/

---

## 📧 Contact

For questions about this platform or collaboration opportunities, please open an issue in the repository.

---

**Last Updated:** 2025-12-05
**Ontology Version:** 0.37.2
**Platform Status:** Active Development
