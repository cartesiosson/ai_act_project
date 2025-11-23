# NIST AI Risk Management Framework (RMF) - Requirements Analysis

## 📋 Overview

The project integrates **NIST AI Risk Management Framework (AI RMF)** as a complementary compliance mechanism alongside the EU AI Act. This document analyzes:

1. **What NIST concepts are loaded** in the ontology
2. **How they are triggered/activated** (automatically or manually)
3. **What criteria or requirements they activate**
4. **Current activation status** and gaps

---

## 🔍 NIST Concepts in Ontology (v0.37.2)

### A. NIST Core Functions (4 concepts)

These represent the four main functions of NIST AI RMF:

| Concept | Type | Triggers | Current Activation |
|---------|------|----------|-------------------|
| `ai:NISTGovernanceFunction` | ComplianceRequirement | None (static) | 🔴 Manual/None |
| `ai:NISTMapFunction` | TechnicalRequirement | None (static) | 🔴 Manual/None |
| `ai:NISTMeasureFunction` | TechnicalRequirement | None (static) | 🔴 Manual/None |
| `ai:NISTManageFunction` | ComplianceRequirement | None (static) | 🔴 Manual/None |

**Status**: These are defined but have **NO automatic activation rules**. They are static reference concepts.

---

### B. NIST Risk Categories (5 concepts)

These represent failure modes and risk areas per NIST framework:

| Concept | Type | Risk Level | Triggers | Current Activation |
|---------|------|-----------|----------|-------------------|
| `ai:NISTBiasesFairnessRisk` | NormativeCriterion | HighRisk | None (static) | 🔴 Manual/None |
| `ai:NISTDataAndPrivacyRisk` | NormativeCriterion | HighRisk | None (static) | 🔴 Manual/None |
| `ai:NISTDataBiasInjectionRisk` | NormativeCriterion | HighRisk | None (static) | 🔴 Manual/None |
| `ai:NISTCybersecurityRisk` | NormativeCriterion | HighRisk | None (static) | 🔴 Manual/None |
| `ai:NISTIOAccessibilityRisk` | NormativeCriterion | MediumRisk | None (static) | 🔴 Manual/None |

**Status**: These are criteria that assign risk levels, but have **NO automatic activation rules**. Must be manually set via Article 6(3) mechanism.

---

### C. NIST Requirements (4 concepts)

These represent specific requirement categories derived from NIST functions:

| Concept | Type | Derived From | Current Activation |
|---------|------|--------------|-------------------|
| `ai:NISTGovernanceRequirement` | NISTRequirement | (static) | 🔴 Manual/None |
| `ai:NISTMapRequirement` | NISTRequirement | (static) | 🔴 Manual/None |
| `ai:NISTMeasureRequirement` | NISTRequirement | (static) | 🔴 Manual/None |
| `ai:NISTManageRequirement` | NISTRequirement | (static) | 🔴 Manual/None |

**Status**: These are output/requirement nodes with **NO automatic derivation**.

---

### D. Technical Metrics (1 concept)

| Concept | Type | Purpose | Current Activation |
|---------|------|---------|-------------------|
| `ai:NISTPerformanceMetrics` | TechnicalCriterion | Measure performance per NIST | 🔴 Manual/None |

**Status**: Technical evaluation criterion, **not automatically derived**.

---

## 🔄 Current Activation Mechanisms

### ❌ NO Automatic SWRL Rules

**Finding**: There are **ZERO SWRL rules** that trigger any NIST concepts.

```bash
$ grep -i "nist" ontologias/rules/swrl-base-rules.ttl
# (no results)
```

### ❌ NO Automatic Backend Derivation

**Finding**: There is **NO Python logic** in `derivation.py` that generates NIST requirements.

```bash
$ grep -i "nist" backend/derivation.py
# (no results)
```

### ❌ NO Automatic API Activation

**Finding**: NIST requirements are **NOT automatically populated** when creating systems.

---

## 📊 Comparison with Other Regulatory Mechanisms

### EU AI Act Annex III (Automatic via SWRL)

```
Purpose (e.g., "RecruitmentOrEmployment")
    ↓ [SWRL Rule: RecruitmentOrEmployment.activatesCriterion]
    ↓
hasActivatedCriterion = NonDiscriminationCriterion
    ↓
Automatically populate: hasComplianceRequirement, hasRiskLevel
```

**Status**: ✅ Fully implemented with 12 SWRL rules

---

### NIST AI RMF (Currently: MANUAL)

```
User manually selects NIST criterion via Article 6(3) endpoint
    ↓ [Manual API call: PUT /systems/{id}/manually-identified-criteria]
    ↓
hasManuallyIdentifiedCriterion = NISTBiasesFairnessRisk
    ↓
Risk level assigned: HighRisk (from criterion definition)
```

**Status**: 🔴 Partially implemented (only via manual override, no automatic trigger)

---

## 🔧 How NIST Could Be Activated (Current Options)

### Option 1: Manual Selection via Article 6(3) Endpoint (Already Works)

Domain experts can manually designate NIST criteria:

```bash
curl -X PUT http://localhost:8000/systems/urn:uuid:system-1/manually-identified-criteria \
  -H "Content-Type: application/json" \
  -d '{
    "hasManuallyIdentifiedCriterion": [
      "ai:NISTBiasesFairnessRisk",
      "ai:NISTDataAndPrivacyRisk"
    ]
  }'
```

**Result**:
- Criterion: HighRisk (from `ai:assignsRiskLevel ai:HighRisk`)
- Risk Level updated to: HighRisk
- No other requirements automatically activated

**Limitation**: This is **residual/expert evaluation**, not **capability-based** like NIST intends.

---

### Option 2: Automatic Activation Based on Technical Characteristics (NOT IMPLEMENTED)

NIST RMF is fundamentally about **capability-based risk assessment**. It could be triggered by:

1. **Model Size + Autonomy** → Governance/Measure functions
2. **Data Volume + Scope** → Data & Privacy Risk
3. **Real-time Processing** → Cybersecurity Risk
4. **Multi-domain Applicability** → IO Accessibility Risk

**Example Rule** (not currently implemented):

```python
# Pseudo-code: what could be implemented
if system.parameterCount > 10B and system.isGenerallyApplicable:
    activate = [
        "ai:NISTGovernanceFunction",     # Need governance for large models
        "ai:NISTMapFunction",             # Need to map risks
        "ai:NISTMeasureFunction",         # Need performance metrics
        "ai:NISTBiasesFairnessRisk"      # Large models prone to bias
    ]
```

**Current Status**: 🔴 NOT implemented

---

### Option 3: Automatic via NIST AI RMF Profile Detection (NOT IMPLEMENTED)

NIST RMF has "Profiles" for different risk scenarios. Could create SWRL rules:

```turtle
# NOT CURRENTLY IN CODEBASE
[ rdf:type swrl:Imp ;
  rdfs:label "Large Language Model triggers NIST Governance" ;
  swrl:body (
    [ swrl:classPredicate ai:IntelligentSystem ; swrl:argument1 ?system ]
    [ swrl:propertyPredicate ai:hasModelScale ; swrl:argument1 ?system ; swrl:argument2 ai:FoundationModelScale ]
    [ swrl:propertyPredicate ai:parameterCount ; swrl:argument1 ?system ; swrl:argument2 ?count ]
    swrl:greaterThan(?count, 10000000000)  # > 10B
  ) ;
  swrl:head (
    [ swrl:propertyPredicate ai:hasActivatedCriterion ;
      swrl:argument1 ?system ;
      swrl:argument2 ai:NISTGovernanceFunction ]
  ) ] .
```

**Current Status**: 🔴 NOT implemented

---

## 📈 NIST Concepts Usage Summary

### In Ontology

```
✅ Defined (14 concepts):
   - 4 Core Functions
   - 5 Risk Categories
   - 4 Requirements
   - 1 Metrics criterion

❌ Automatic Activation:
   - 0 SWRL rules
   - 0 Backend derivation functions
   - 0 Capability-based triggers

🟡 Manual Activation:
   - Via Article 6(3) endpoint (hasManuallyIdentifiedCriterion)
   - Domain expert judgment only
```

### In API

```
✅ Frontend Form:
   - Section 6: "Expert Evaluation - Additional Risk Criteria"
   - Shows system_capability_criteria vocabulary (shared with Article 6(3))

❌ Automatic API Response:
   - No hasNISTRequirement field in system response
   - No auto-population of NIST concepts
```

### In Frontend

```
✅ Form Field:
   - Multi-select in "Expert Evaluation" section
   - NIST criteria available via shared vocabulary

❌ Display:
   - No dedicated NIST visualization
   - No indication which criteria are NIST vs. EU AI Act
```

---

## 🎯 Recommended Implementation Options

### **Option A: Accept Current State (Minimal)**

**Rationale**: NIST is complex and intentionally flexible. Manual selection via Article 6(3) is appropriate for expert judgment.

**Pros**:
- Simple, low risk
- Respects NIST's flexibility
- Works for compliance scenarios

**Cons**:
- No automatic GPAI → NIST triggering
- Requires expert knowledge
- Underutilizes NIST framework

---

### **Option B: Automatic NIST via Capability Metrics (Recommended)**

**Rationale**: Map NIST framework to existing capability-based indicators (parameter count, autonomy, general applicability).

**Implementation**:

1. **Add to `derive_capability_metrics()` in backend**:

```python
def derive_nist_activation(data: Dict) -> Dict[str, List[str]]:
    """
    Derive NIST RMF activation based on system capabilities and characteristics.

    Returns: {
        'nist_functions': ['ai:NISTGovernanceFunction', ...],
        'nist_risks': ['ai:NISTBiasesFairnessRisk', ...],
        'nist_requirements': ['ai:NISTGovernanceRequirement', ...]
    }
    """
    nist_profile = {
        'functions': [],
        'risks': [],
        'requirements': []
    }

    # Rule 1: GPAI Systems → Governance + Mapping
    if is_gpai_system(data):
        nist_profile['functions'].extend(['ai:NISTGovernanceFunction', 'ai:NISTMapFunction'])
        nist_profile['risks'].append('ai:NISTBiasesFairnessRisk')
        nist_profile['requirements'].append('ai:NISTGovernanceRequirement')

    # Rule 2: Data-Heavy Systems → Data & Privacy Risk
    if data.get('parameterCount', 0) > 1_000_000_000:  # > 1B params
        nist_profile['risks'].append('ai:NISTDataAndPrivacyRisk')
        nist_profile['functions'].append('ai:NISTMeasureFunction')

    # Rule 3: Real-time Deployment → Cybersecurity Risk
    if 'RealTimeProcessing' in data.get('hasDeploymentContext', []):
        nist_profile['risks'].append('ai:NISTCybersecurityRisk')
        nist_profile['functions'].append('ai:NISTManageFunction')

    # Rule 4: High-Risk Category → Fairness Risk
    if data.get('hasRiskLevel') == 'ai:HighRisk':
        if 'ai:NISTBiasesFairnessRisk' not in nist_profile['risks']:
            nist_profile['risks'].append('ai:NISTBiasesFairnessRisk')

    # Rule 5: Accessibility Concerns → IO Accessibility Risk
    if 'PublicFacing' in data.get('hasDeploymentContext', []):
        nist_profile['risks'].append('ai:NISTIOAccessibilityRisk')

    return nist_profile
```

2. **Update System endpoint**:

```json
{
  "@id": "urn:uuid:system-1",
  "hasName": "LLM-Hiring-Assistant",

  // ... existing fields ...

  "hasActivatedCriterion": ["ai:NonDiscriminationCriterion"],
  "hasCapabilityMetric": ["ai:HighParameterCount", "ai:GenerallyApplicableCapability"],

  // NEW: NIST RMF activation (from capability-based derivation)
  "hasNISTFunction": ["ai:NISTGovernanceFunction", "ai:NISTMeasureFunction"],
  "hasNISTRisk": ["ai:NISTBiasesFairnessRisk", "ai:NISTDataAndPrivacyRisk"],
  "hasNISTRequirement": ["ai:NISTGovernanceRequirement", "ai:NISTMeasureRequirement"]
}
```

3. **Add to frontend display**:
   - New section: "NIST AI RMF Profile"
   - Shows: Functions, Risk Areas, Requirements
   - Links to NIST documentation

**Pros**:
- Automatic and intelligent
- Maps to NIST framework intent
- Complements EU AI Act coverage
- Captures systemic risk assessment

**Cons**:
- Additional complexity in backend
- Need to define activation rules
- NIST concepts become "populated" rather than "selected"

---

### **Option C: NIST SWRL Rules (Most Formal)**

**Rationale**: Implement NIST triggering via SWRL rules like EU AI Act Annex III.

**Example**:

```turtle
# SWRL Rules for NIST AI RMF Activation

# Rule 1: FoundationModel -> Governance + Map Functions
[ rdf:type swrl:Imp ;
  rdfs:label "Foundation Model triggers NIST Governance and Mapping" ;
  swrl:body (
    [ rdf:type swrl:ClassAtom ;
      swrl:classPredicate ai:IntelligentSystem ;
      swrl:argument1 ?system ]
    [ rdf:type swrl:DatavaluedPropertyAtom ;
      swrl:propertyPredicate ai:hasModelScale ;
      swrl:argument1 ?system ;
      swrl:argument2 ai:FoundationModelScale ]
  ) ;
  swrl:head (
    [ rdf:type swrl:IndividualPropertyAtom ;
      swrl:propertyPredicate ai:hasActivatedCriterion ;
      swrl:argument1 ?system ;
      swrl:argument2 ai:NISTGovernanceFunction ]
    [ rdf:type swrl:IndividualPropertyAtom ;
      swrl:propertyPredicate ai:hasActivatedCriterion ;
      swrl:argument1 ?system ;
      swrl:argument2 ai:NISTMapFunction ]
  ) ] .

# Rule 2: General Purpose + High Volume -> Fairness Risk
[ rdf:type swrl:Imp ;
  rdfs:label "General Purpose High-Volume systems trigger Biases/Fairness Risk" ;
  swrl:body (
    [ rdf:type swrl:ClassAtom ;
      swrl:classPredicate ai:IntelligentSystem ;
      swrl:argument1 ?system ]
    [ rdf:type swrl:DatavaluedPropertyAtom ;
      swrl:propertyPredicate ai:isGenerallyApplicable ;
      swrl:argument1 ?system ;
      swrl:argument2 "true"^^xsd:boolean ]
    [ rdf:type swrl:DatavaluedPropertyAtom ;
      swrl:propertyPredicate ai:hasDeploymentContext ;
      swrl:argument1 ?system ;
      swrl:argument2 ai:HighVolumeProcessing ]
  ) ;
  swrl:head (
    [ rdf:type swrl:IndividualPropertyAtom ;
      swrl:propertyPredicate ai:hasActivatedCriterion ;
      swrl:argument1 ?system ;
      swrl:argument2 ai:NISTBiasesFairnessRisk ]
  ) ] .
```

**Pros**:
- Formal semantic web approach
- Executable by SPARQL-enabled triplestore (Fuseki)
- Consistent with EU AI Act SWRL implementation
- Fully auditable derivation

**Cons**:
- Requires SWRL reasoning capability in Fuseki
- SWRL is complex to maintain
- NIST framework flexibility lost in rigid rules

---

## 📝 Current State Summary

| Aspect | Status | Trigger Method | Gap |
|--------|--------|----------------|-----|
| **Concepts Defined** | ✅ 14 NIST concepts | (N/A) | None |
| **Auto Activation** | ❌ Not Implemented | None | Major |
| **Manual Selection** | ✅ Possible | Article 6(3) endpoint | None |
| **Frontend Display** | 🟡 Partial | Shared vocabulary | Needs NIST-specific UI |
| **Risk Assignment** | ✅ Automatic | Via criterion definition | None |
| **Requirements Derivation** | ❌ Not Implemented | None | Major |

---

## 🚀 Next Steps

**Priority 1**: Decide activation approach (Options A, B, or C above)

**Priority 2**: If pursuing automatic activation:
- Define NIST activation triggers
- Implement backend logic
- Add NIST requirements derivation
- Update frontend visualization

**Priority 3**: Document NIST-specific compliance mappings

---

**Document Version**: 1.0
**Last Updated**: 2025-11-23
**Related Files**:
- [ontologia-v0.37.2.ttl](../ontologias/versions/0.37.2/ontologia-v0.37.2.ttl) - NIST concept definitions
- [iso-nist-mappings.ttl](../ontologias/standards/iso-nist-mappings.ttl) - Integration mappings
- [derivation.py](../backend/derivation.py) - Automatic derivation logic
