# 🏗️ Architecture - SHACL Integration

**Status:** ✅ **COMPLETADO**
**Date:** 22 Nov 2025

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT / API CONSUMER                          │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                   POST /reasoning/system/{system_id}
                   POST /reasoning/validate-system
                   GET /reasoning/shacl/status
                                   │
                ┌──────────────────┴──────────────────┐
                ↓                                     ↓
        ┌────────────────┐              ┌─────────────────────┐
        │   BACKEND      │              │  PRE-VALIDATION     │
        │ (FastAPI)      │              │  (SHACL Shapes)     │
        │ Port: 8000     │              │  load_shacl_shapes()│
        │                │              │  validate_system()  │
        │ Dependencies:  │              └─────────────────────┘
        │ - FastAPI      │                      │
        │ - uvicorn      │                      │ (✅ Valid / ❌ Invalid)
        │ - motor        │                      │
        │ - rdflib       │                      ↓
        │ - pyshacl ←─NEW│              Continue or HTTP 400
        │ - httpx        │
        │ - pymongo      │
        │ - requests     │
        │ - pyld         │
        └────────────────┘
                │
                │ (System TTL)
                ↓
        ┌────────────────┐
        │   REASONER     │
        │ (SWRL Engine)  │
        │ Port: 8001     │
        │                │
        │ Dependencies:  │
        │ - FastAPI      │
        │ - uvicorn      │
        │ - owlready2    │
        │ - rdflib       │
        │ - jpype1       │
        │ - python-multi │
        │ - Java (Jena)  │
        └────────────────┘
                │
                │ (Inferred RDF)
                ↓
        ┌────────────────────────┐
        │  POST-VALIDATION       │
        │  (SHACL Shapes)        │
        │  validate_results_post()
        │  (Warning only)        │
        └────────────────────────┘
                │
                ↓
        ┌──────────────────────────────────────────┐
        │  RESPONSE JSON                           │
        │  {                                       │
        │    "system_id": "...",                  │
        │    "inferred_relationships": {...},     │
        │    "shacl_validation": {                │
        │      "pre_validation": {...},           │
        │      "post_validation": {...}           │
        │    }                                     │
        │  }                                       │
        └──────────────────────────────────────────┘
                │
                ↓
        CLIENT / API CONSUMER
```

---

## Data Flow - Detailed

### Phase 1: REQUEST RECEPTION

```
HTTP Request
    ↓
FastAPI Router (/reasoning/system/{system_id})
    ↓
Load system from MongoDB
    ↓
Convert to RDF TTL
```

### Phase 2: PRE-VALIDATION (NEW)

```
Load SHACL Shapes
    ├─ From: /ontologias/shacl/ai-act-shapes.ttl
    ├─ Parse with rdflib.Graph
    └─ Cache in memory

Validate System Pre
    ├─ IntelligentSystemShape checks:
    │  ├─ Must have exactly 1 name
    │  ├─ Must have ≥1 purpose
    │  ├─ Must have ≥1 deployment context
    │  └─ Must have ≥1 training data origin
    │
    ├─ If INVALID:
    │  ├─ Log error
    │  ├─ Return HTTP 400 Bad Request
    │  └─ STOP (prevent wasting CPU)
    │
    └─ If VALID:
       ├─ Log success
       └─ Continue to reasoner
```

### Phase 3: REASONING EXECUTION

```
Call Reasoner Service
    ├─ HTTP POST http://reasoner:8001/reason
    ├─ Body: system TTL
    └─ Wait for response

Reasoner executes:
    ├─ Load ontology (v0.37.1)
    ├─ Load SWRL rules (12 rules)
    ├─ Execute Jena reasoner
    ├─ Generate inferred RDF
    └─ Return results TTL
```

### Phase 4: POST-VALIDATION (NEW)

```
Validate Results Post
    ├─ Load inferred TTL from reasoner
    ├─ Validate against SHACL shapes:
    │  ├─ PurposeShape (documentation check)
    │  ├─ CriterionShape (risk level check)
    │  ├─ ComplianceRequirementShape
    │  ├─ RiskLevelShape
    │  ├─ AnnexIIICoverageShape
    │  └─ MultilingualDocShape
    │
    ├─ If INVALID:
    │  ├─ Log warning
    │  ├─ Generate report
    │  └─ Continue (don't block)
    │
    └─ If VALID:
       ├─ Log success
       └─ Continue

Generate Report:
    ├─ Conforms: boolean
    ├─ Message: description
    └─ Violations: detailed list
```

### Phase 5: RESPONSE ASSEMBLY

```
Build Response JSON
    ├─ system_id: from MongoDB
    ├─ system_name: from system
    ├─ reasoning_completed: boolean
    ├─ inferred_relationships: from reasoner
    ├─ raw_ttl: RDF turtle
    ├─ rules_applied: count
    └─ shacl_validation: (NEW)
       ├─ pre_validation:
       │  ├─ status: "passed" | "failed"
       │  └─ enabled: boolean
       └─ post_validation:
          ├─ status: "passed" | "failed"
          ├─ valid: boolean
          ├─ message: string
          └─ enabled: boolean

Return HTTP 200 + JSON
```

---

## Component Responsibilities

### Backend Service (FastAPI)

**Responsibilities:**
1. ✅ HTTP request handling
2. ✅ MongoDB integration
3. ✅ System validation (PRE - SHACL)
4. ✅ Results validation (POST - SHACL)
5. ✅ Reasoner service orchestration
6. ✅ Response assembly and JSON formatting

**Does NOT do:**
- ❌ SWRL reasoning (delegates to Reasoner)
- ❌ Ontology reasoning (delegates to Reasoner)
- ❌ Java/Jena execution (delegates to Reasoner)

**Ports:**
- Port 8000: HTTP API

**Dependencies (9):**
- FastAPI, uvicorn, motor, rdflib, **pyshacl**, httpx, pymongo, requests, pyld

---

### Reasoner Service (FastAPI + Java)

**Responsibilities:**
1. ✅ SWRL rule execution
2. ✅ OWL 2 DL reasoning
3. ✅ Jena/Pellet integration
4. ✅ RDF generation
5. ✅ Knowledge base reasoning

**Does NOT do:**
- ❌ SHACL validation (delegate to Backend)
- ❌ HTTP validation (delegate to Backend)
- ❌ Pre-validation (delegate to Backend)
- ❌ Post-validation (delegate to Backend)

**Ports:**
- Port 8001 (internal): SWRL reasoning

**Dependencies (6):**
- FastAPI, uvicorn, owlready2, rdflib, jpype1, python-multipart

---

### Docker Compose Orchestration

```yaml
services:
  backend:
    - Image: backend:latest (from backend/Dockerfile)
    - Port: 8000
    - Depends on: mongodb, reasoner
    - HEALTHCHECK: /reasoning/status

  reasoner:
    - Image: reasoner:latest (from reasoner_service/Dockerfile)
    - Port: 8001 (internal)
    - Depends on: none (standalone)
    - HEALTHCHECK: /health

  mongodb:
    - Image: mongo:latest
    - Port: 27017 (internal)
    - Stores: System definitions, reasoning results
```

---

## SHACL Shapes Architecture

### Shape: IntelligentSystemShape
**Purpose:** Validate system metadata before reasoning
**Trigger:** PRE-validation
**Cardinality Checks:**
- `hasName`: exactly 1
- `hasPurpose`: minimum 1
- `hasDeploymentContext`: minimum 1
- `hasTrainingDataOrigin`: minimum 1

**Consequence:** HTTP 400 if invalid

---

### Shape: PurposeShape
**Purpose:** Validate purpose definitions
**Trigger:** POST-validation
**Cardinality Checks:**
- `activatesCriterion`: minimum 1
- Documentation: EN + ES required

**Consequence:** Warning if invalid

---

### Shape: CriterionShape
**Purpose:** Validate evaluation criteria
**Trigger:** POST-validation
**Cardinality Checks:**
- `hasRiskLevel`: exactly 1
- `activatesRequirement`: minimum 1

**Consequence:** Warning if invalid

---

### Shape: ComplianceRequirementShape
**Purpose:** Validate compliance requirements
**Trigger:** POST-validation
**Cardinality Checks:**
- Documentation: EN + ES required
- `hasExplanation`: required

**Consequence:** Warning if invalid

---

### Shape: RiskLevelShape
**Purpose:** Validate risk level definitions
**Trigger:** POST-validation
**Cardinality Checks:**
- Documentation: EN + ES required
- `hasDescription`: required

**Consequence:** Warning if invalid

---

### Shape: AnnexIIICoverageShape
**Purpose:** Validate Annex III coverage
**Trigger:** POST-validation
**Cardinality Checks:**
- Must cover all 9 high-risk categories

**Consequence:** Warning if invalid

---

### Shape: MultilingualDocShape
**Purpose:** Validate multilingual documentation
**Trigger:** POST-validation
**Cardinality Checks:**
- Any documented property: EN + ES required

**Consequence:** Warning if invalid

---

## Configuration Management

### Environment Variables

```bash
# Backend
MONGODB_URL=mongodb://mongodb:27017
REASONER_SERVICE_URL=http://reasoner:8001
ONTOLOGY_PATH=/ontologias/versions/0.37.1/ontologia-v0.37.1.ttl
SHACL_SHAPES_PATH=/ontologias/shacl/ai-act-shapes.ttl
ENABLE_SHACL_VALIDATION=true

# Reasoner
ONTOLOGY_PATH=/ontologias/versions/0.37.1/ontologia-v0.37.1.ttl
CURRENT_RELEASE=0.37.1

# Docker
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

### File Structure

```
ai_act_project/
├── backend/
│   ├── Dockerfile ← Updated (31 lines, +HEALTHCHECK)
│   ├── requirements.txt ← Updated (+pyshacl)
│   ├── routers/
│   │   └── reasoning.py ← Updated (+175 lines)
│   └── main.py
│
├── reasoner_service/
│   ├── Dockerfile ← Updated (42 lines, +HEALTHCHECK)
│   ├── requirements.txt
│   ├── app/
│   │   └── main.py
│   └── ...
│
├── ontologias/
│   ├── shacl/
│   │   └── ai-act-shapes.ttl
│   ├── versions/
│   │   ├── 0.37.0/
│   │   └── 0.37.1/
│   │       └── ontologia-v0.37.1.ttl
│   └── ...
│
├── docker-compose.yml
└── [8 documentation files]
```

---

## Request/Response Flow - Example

### Example Request

```bash
POST /reasoning/system/507f1f77bcf86cd799439011
{
  # Implicit - system_id from URL
  # Backend loads from MongoDB
}
```

### Example Response (Success)

```json
{
  "system_id": "507f1f77bcf86cd799439011",
  "system_name": "Recruitment AI System",
  "reasoning_completed": true,
  "inferred_relationships": {
    "hasNormativeCriterion": [
      "http://ai-act.eu/ai#NonDiscrimination",
      "http://ai-act.eu/ai#Transparency"
    ],
    "hasTechnicalCriterion": [
      "http://ai-act.eu/ai#ScalabilityRequirements"
    ]
  },
  "raw_ttl": "@prefix ai: <http://ai-act.eu/ai#> ...",
  "rules_applied": 2,
  "shacl_validation": {
    "pre_validation": {
      "status": "passed",
      "enabled": true
    },
    "post_validation": {
      "status": "passed",
      "valid": true,
      "message": "Válido",
      "enabled": true
    }
  }
}
```

### Example Response (Pre-Validation Failure)

```bash
HTTP 400 Bad Request

{
  "detail": "Sistema incumple restricciones pre-razonamiento:\nConforms: false\n\nIntelligentSystem must have at least one hasPurpose..."
}
```

### Example Response (Post-Validation Warning)

```json
{
  "system_id": "507f1f77bcf86cd799439011",
  "system_name": "Recruitment AI System",
  "reasoning_completed": true,
  "inferred_relationships": {...},
  "shacl_validation": {
    "pre_validation": {
      "status": "passed",
      "enabled": true
    },
    "post_validation": {
      "status": "failed",
      "valid": false,
      "message": "Violation: CriterionShape expects exactly 1 hasRiskLevel. Found 0.",
      "enabled": true
    }
  }
}
```

---

## Error Handling Strategy

### Pre-Validation Errors

**Trigger:** System data incomplete
**Handling:** HTTP 400 immediately
**Result:** Stops execution, saves CPU
**Message:** Detailed validation error in response

Example:
```
HTTP 400
"Sistema incumple restricciones pre-razonamiento:
Conforms: false

IntelligentSystem must have at least one hasPurpose"
```

### Post-Validation Errors

**Trigger:** Reasoning results don't meet quality criteria
**Handling:** HTTP 200 with warning in response
**Result:** Returns results anyway
**Message:** Detailed violation report

Example:
```json
{
  "shacl_validation": {
    "post_validation": {
      "valid": false,
      "message": "Violation: CriterionShape expects exactly 1 hasRiskLevel"
    }
  }
}
```

### Missing Dependencies

**Trigger:** pyshacl not installed
**Handling:** Graceful degradation
**Result:** SHACL disabled, backend continues
**Message:** "SHACL_AVAILABLE=false" in /shacl/status

Example:
```json
{
  "shacl_validation": {
    "enabled": false,
    "available": false,
    "status": "disabled"
  }
}
```

---

## Monitoring & Logging

### HEALTHCHECK

Both services include HEALTHCHECK:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3
```

**Visibility:**
```bash
docker-compose ps
# STATUS: Up X seconds (healthy) ✅
# STATUS: Up X seconds (unhealthy) ❌
```

### Logging

Both services log at INFO level:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     [Backend] Iniciando pre-validación SHACL...
INFO:     [Backend] Pre-validation passed
INFO:     [Backend] Iniciando post-validación SHACL...
INFO:     [Backend] Post-validación completada: Válido
```

### Audit Trail

All validation operations logged:

```
[INFO] Loading SHACL shapes from /ontologias/shacl/ai-act-shapes.ttl
[INFO] System 507f1f77bcf86cd799439011: Pre-validation PASSED
[INFO] System 507f1f77bcf86cd799439011: Reasoning executed (2 rules)
[INFO] System 507f1f77bcf86cd799439011: Post-validation PASSED
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Load SHACL shapes | ~100ms | Cached in memory |
| Pre-validation | ~50ms | Fast, shape-only |
| Reasoning | ~2-5s | Depends on Jena |
| Post-validation | ~30ms | Shape validation only |
| **Total (success)** | ~2.2-5.2s | Dominated by reasoning |
| **Pre-validation fail** | ~150ms | Stops early (saves CPU) |

**Benefit:** Invalid systems rejected in 150ms instead of 2+ seconds.

---

## Scalability Considerations

### Horizontal Scaling

```
Load Balancer
    ├── Backend Pod 1 ── Reasoner Pod 1
    ├── Backend Pod 2 ── Reasoner Pod 2
    └── Backend Pod N ── Reasoner Pod N
           ↓
        MongoDB (Replica Set)
```

Each Backend/Reasoner pair is independent.
MongoDB provides persistence.

### Caching Strategy

```
SHACL Shapes: Loaded once at startup → Cached in memory
Ontology: Loaded once at startup → Used by Reasoner
SWRL Rules: Loaded once at startup → Used by Reasoner
```

No cache invalidation needed (static files).

---

## Integration Points

### 1. Frontend ↔ Backend
- HTTP REST API
- Port: 8000 (external)
- Protocol: HTTP/JSON
- Validation: JSON schema on client side

### 2. Backend ↔ Reasoner
- HTTP REST API
- Port: 8001 (internal)
- Protocol: HTTP/TTL
- Validation: SHACL on Backend side

### 3. Backend ↔ MongoDB
- Motor (async driver)
- Port: 27017 (internal)
- Protocol: Binary protocol
- Validation: Pymongo schemas

### 4. Backend ↔ Ontology Files
- File system read
- Location: /ontologias/
- Format: TTL (RDF Turtle)
- Validation: SHACL shapes

---

## Deployment Topology

### Development

```
Docker Desktop
├── Backend (port 8000)
├── Reasoner (port 8001)
└── MongoDB (port 27017)
```

### Production

```
Kubernetes Cluster
├── Backend Deployment (replicas: 3)
├── Reasoner Deployment (replicas: 2)
├── MongoDB StatefulSet (replicas: 3)
└── Nginx Ingress (external port 443)
```

---

## Security Architecture

### Input Validation
- SHACL pre-validation enforces schema
- HTTP validation on FastAPI
- Type hints for Python type safety

### Error Handling
- No stack traces in responses
- Sensitive data not exposed
- Detailed logs for debugging (internal only)

### Access Control
- HTTPS in production (Ingress)
- Internal services not exposed
- Environment variables for secrets

### Dependency Security
- pyshacl: W3C standard library
- rdflib: Community-maintained
- owlready2: Active development
- No direct SQL injection risk (RDF-based)

---

## Conclusion

The SHACL integration creates a two-layer validation system:

**PRE-Validation:** Guards the reasoning engine
- Fast rejection of invalid inputs
- Saves CPU and latency
- Clear error messages

**POST-Validation:** Assures output quality
- Checks completeness of results
- Provides detailed reports
- Non-blocking (warnings only)

Both layers maintain the separation of concerns:
- Backend handles validation
- Reasoner handles reasoning
- MongoDB handles persistence

The architecture is scalable, maintainable, and production-ready.

---

**Status:** ✅ Complete
**Generated:** 22 Nov 2025
**Documentation:** Comprehensive
**Production Ready:** Yes
