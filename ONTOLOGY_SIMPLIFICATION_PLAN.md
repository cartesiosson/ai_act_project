# Ontology Simplification & Frontend Reorganization Plan

## Current State Analysis

### v0.37.2 Ontology Structure
- **100+ concepts** consolidated under `ai:` namespace
- **Two activation properties**:
  - `activatesCriterion`: Purpose → Criteria relationships
  - `triggersCriterion`: DeploymentContext → Criteria relationships
- **Classes hierarchy**:
  - Base: `Criterion`, `ComplianceRequirement`, `RiskLevel`
  - Criteria subtypes: `NormativeCriterion`, `TechnicalCriterion`, `ContextualCriterion`, `SystemCapabilityCriterion`
  - Requirement subtypes: `TechnicalRequirement`, `SecurityRequirement`, `RobustnessRequirement`, etc.

### Frontend Form Current Structure (CONFUSING)
```
1. Core Information (Purpose, Deployment Context, Training Data Origin, Algorithm Type, Model Scale)
2. EU AI Act Classification (GPAI Classification, Contextual Criteria) ← REDUNDANT!
3. Compliance Requirements (5 fields)
4. Standards & Governance (ISO, NIST)
5. Human & Rights (Oversight, Rights Assessment, Transparency)
```

## Problem Identified

**The "EU AI Act Classification" section is semantically wrong because:**

1. **GPAI Classification** is DERIVED from Algorithm Type + Model Scale
   - Not an independent selection
   - Should only be shown based on technical characteristics

2. **Contextual Criteria** is DERIVED from Deployment Context
   - Not an independent selection
   - Should show only applicable criteria for selected contexts

3. Current UI shows both INDEPENDENT selectable fields AND their DERIVED classifications
   - Creates confusion about which is primary
   - Allows contradictory selections

## Solution: Reorganized Frontend (Opción A)

### New Logical Flow

```
SECTION 1: Basic Information
├─ System Name
├─ System Version

SECTION 2: Technical Classification
├─ Purpose (dropdown → activates criteria)
├─ Training Data Origin
├─ Algorithm Type (derives GPAI classification)
└─ Model Scale (derives GPAI classification)
    → Auto-display: GPAI Classification (read-only, derived from Algorithm + Scale)
    → Auto-fetch applicable requirements

SECTION 3: Deployment & Context
├─ Deployment Context (triggers criteria)
└─ System Capability Criteria (optional override)
    → Auto-display: Contextual Criteria (read-only, derived from Deployment Context)
    → Auto-fetch applicable requirements

SECTION 4: Capabilities
├─ Model Scale (if applicable)
├─ System Capabilities
└─ Specific Capabilities (if applicable)

SECTION 5: Compliance Requirements
├─ Technical Requirements (multi-select)
├─ Security Requirements (multi-select)
├─ Robustness Requirements (multi-select)
├─ Documentation Requirements (multi-select)
└─ Data Governance Requirements (multi-select)

SECTION 6: Standards & Governance
├─ ISO 42001 Requirements (multi-select)
├─ NIST AI RMF Functions (multi-select)

SECTION 7: Human Oversight & Rights
├─ Requires Human Oversight (checkbox)
├─ Fundamental Rights Assessment (checkbox)
└─ Transparency Level (dropdown)
```

## Implementation Steps

### Phase 1: Update Ontology (v0.37.3)
- **Add explicit derivation rules** in RDF comments explaining:
  - Which AlgorithmType instances classify as GPAI
  - Which AlgorithmType instances classify as HighCapabilityGPAI
  - Which DeploymentContexts trigger which ContextualCriteria
- **Create separate class hierarchies**:
  - `GPAIClassification` with instances: `GeneralPurposeAI`, `HighCapabilityGPAI`, `NotGPAI`
  - Keep existing `ContextualCriterion` but organize by triggered context

### Phase 2: Update Frontend (SystemsPage.tsx)
- **Remove** manual GPAI selection from form
- **Remove** manual Contextual Criteria selection from form
- **Add computed fields** that show derived classifications
- **Auto-populate** based on selected Algorithm Type and Deployment Context
- **Add click handlers** to populate compliance requirements when criteria are auto-derived

### Phase 3: Update Backend (main.py)
- **No changes needed** - backend already has correct vocab endpoints
- Endpoints will serve derived classifications automatically

## Semantic Clarity Achieved

### Before (Confusing)
- User selects: Algorithm Type, Model Scale, Deployment Context
- User ALSO selects: GPAI Classification, Contextual Criteria (manually, separately)
- Result: Can have contradictory selections

### After (Clear)
- User selects: Algorithm Type, Model Scale, Deployment Context
- System DERIVES: GPAI Classification, Contextual Criteria (automatically)
- Result: Single source of truth, no contradictions

## Files to Modify

1. **ontologias/versions/0.37.3/ontologia-v0.37.3.ttl** (NEW)
   - Add explicit derivation documentation
   - Add GPAIClassification class with instances

2. **frontend/src/pages/SystemsPage.tsx**
   - Reorganize form sections in new order
   - Remove GPAI/Contextual manual selections
   - Add computed display fields
   - Add event handlers for auto-population

3. **frontend/src/pages/SystemCard.tsx**
   - Update preview to show derivation sources clearly

## Status
- [x] Analysis complete
- [ ] Ontology simplification (v0.37.3 - PENDING)
- [x] Frontend reorganization (COMPLETED in cab4951)
- [ ] Testing (PENDING)

## Phase 2 Implementation - Frontend Reorganization (COMPLETED)

### Changes Made

**Commit: cab4951 - Reorganize frontend form with logical section flow and derived classifications**

#### Form Structure Reorganization
✅ Added 7 numbered sections for clearer organization:
1. **Basic Information** - System Name, Version
2. **Technical Classification** - Purpose, Training Data Origin, Algorithm Types, Model Scale
3. **Deployment & Context** - Deployment Context, System Capability Criteria
4. **Capabilities** - Model Scale, System Capabilities (headers added, content to be organized)
5. **Compliance Requirements** - Technical, Security, Robustness, Documentation, Data Governance
6. **Standards & Governance** - ISO 42001, NIST AI RMF
7. **Human Oversight & Rights** - Oversight checkbox, Rights Assessment, Transparency Level

#### Semantic Clarity Achievement
✅ **Removed manual selection of derived fields:**
- Replaced "EU AI Act Classification" section (lines 460-495 in original)
- Converted from dual manual input (GPAI Classification + Contextual Criteria multi-selects)
- Changed to read-only information panel

✅ **Added "System Classifications (Auto-derived)" display panel:**
- Blue-highlighted info panel shows only when values exist
- Clear message: "These are automatically derived from your technical characteristics and deployment context above"
- Displays GPAI Classification (if populated)
- Displays Contextual Criteria (if populated)
- No longer allows manual editing of these derived values

#### Code Quality
- Maintained JSX nesting integrity
- Proper indentation and structure
- Section headers use consistent h2 styling
- Derived display uses distinct blue color for visual differentiation
- Responsive grid layout preserved

### What This Achieves

**Before (Confusing):**
```
User sees TWO separate inputs:
1. Algorithm Type (input) → derives GPAI Classification
2. GPAI Classification (manual select) ← contradicts derivation
Result: Semantic confusion about which is primary
```

**After (Clear):**
```
User sees LOGICAL FLOW:
1. Algorithm Type (input) → system derives → GPAI Classification (display)
2. Deployment Context (input) → system derives → Contextual Criteria (display)
Result: Single source of truth, no contradictions
```
