# Frontend Reorganization Testing Guide

## Overview
This document provides comprehensive testing procedures for the frontend reorganization completed in commit cab4951.

**Reorganization Goal:** Convert the confusing "EU AI Act Classification" manual input section into a clear logical form flow with auto-derived classifications.

## Key Changes to Test

### 1. Form Structure Organization
✅ **7 Numbered Sections** now clearly guide the user through the form:

```
1. Basic Information
   └─ System Name, Version

2. Technical Classification
   └─ Purpose, Training Data Origin, Algorithm Types, Model Scale
   └─ Determines GPAI Classification

3. Deployment & Context
   └─ Deployment Context, System Capability Criteria
   └─ Determines Contextual Criteria

4. Capabilities
   └─ Model Scale, System Capabilities

5. Compliance Requirements
   └─ Technical, Security, Robustness, Documentation, Data Governance

6. Standards & Governance
   └─ ISO 42001, NIST AI RMF

7. Human Oversight & Rights
   └─ Human Oversight, Fundamental Rights Assessment, Transparency Level
```

### 2. Derived Classifications Display (CRITICAL)
✅ **Read-only Info Panel** replaces manual input:

**What Changed:**
- **Before:** Users could manually select GPAI Classification and Contextual Criteria (contradicting the derivation logic)
- **After:** These fields are now read-only display panels that show derived values

**Visual Design:**
- Blue background (`bg-blue-50 dark:bg-blue-900`)
- Clear label: "System Classifications (Auto-derived)"
- Descriptive text: "These are automatically derived from your technical characteristics and deployment context above"
- Only appears when values exist (conditional rendering)

## Testing Procedures

### Test 1: Form Section Organization

**Objective:** Verify all 7 sections are properly labeled and organized.

**Steps:**
1. Navigate to "Intelligent Systems" page
2. Scroll through the form
3. Verify you see numbered section headers:
   - "1. Basic Information"
   - "2. Technical Classification"
   - "3. Deployment & Context"
   - "4. Capabilities"
   - "5. Compliance Requirements"
   - "6. Standards & Governance"
   - "7. Human Oversight & Rights"

**Expected Result:** ✅ All 7 sections visible with clear numbering and borders

---

### Test 2: Derived Classifications Panel Display

**Objective:** Verify the auto-derived classifications panel appears/disappears correctly.

**Steps:**
1. Start with empty form (new entry)
2. **Should NOT see** "System Classifications (Auto-derived)" panel initially
3. Select values in Section 2:
   - Select any "Purpose(s)" value
   - Select any "Algorithm Type(s)" value
4. **Should STILL NOT see** derived panel (Algorithm Type doesn't populate GPAI yet - awaiting backend logic)
5. In browser console, manually set form values to test:
   ```javascript
   // This will be done by backend in future phase
   // For now, verify the panel HTML exists in DOM
   ```

**Expected Result:** ✅ Panel appears/disappears based on form.hasGPAIClassification.length > 0

---

### Test 3: Read-only Display Formatting

**Objective:** Verify derived fields are displayed as read-only information, not input controls.

**Steps:**
1. Look for the derived classifications panel (if values were populated by backend)
2. Verify the content shows:
   - GPAI Classification label and values (if any)
   - Contextual Criteria label and values (if any)
3. Verify these are **NOT** multi-select dropdowns
4. Verify text displays with proper formatting and no "ai:" prefix

**Expected Result:** ✅ Information displayed as text paragraphs, not input fields

---

### Test 4: No Longer See Old GPAI/Contextual Selects

**Objective:** Verify the old manual selection dropdowns are GONE.

**Steps:**
1. Look for "EU AI Act Classification" section
2. Look for "GPAI Classification (if applicable)" multi-select dropdown
3. Look for "Contextual Criteria" multi-select dropdown

**Expected Result:** ✅ These elements are completely removed (not hidden, but deleted from code)

---

### Test 5: Form Submission with New Structure

**Objective:** Verify form submissions still work with the new structure.

**Steps:**
1. Fill out complete form:
   - Section 1: System Name, Version
   - Section 2: Purpose, Training Data Origin, Algorithm Type
   - Section 3: Deployment Context
   - Section 4: (leave empty - optional)
   - Section 5: Select a few compliance requirements
   - Section 6: Select ISO/NIST requirements
   - Section 7: Check Human Oversight, select Transparency Level
2. Click "Submit" button
3. Verify system is created in list below

**Expected Result:** ✅ Form submits successfully, system appears in list

---

### Test 6: SystemCard Display

**Objective:** Verify the system preview card displays all sections correctly.

**Steps:**
1. After creating a system, look at the SystemCard display
2. Verify sections appear in order:
   - Header with name and URN
   - Risk Level and GPAI Classification (if populated)
   - Core properties (Purpose, Deployment Context, Training Data)
   - Algorithm Type and Model Scale
   - Contextual Criteria (if populated)
   - Compliance Requirements section
   - Standards & Governance
   - Human Oversight info

**Expected Result:** ✅ Card shows all properties with clear section organization

---

### Test 7: Responsive Design

**Objective:** Verify form layout works on different screen sizes.

**Steps:**
1. Open form on desktop (md breakpoint and above)
   - Verify grid columns are properly laid out (grid-cols-1 md:grid-cols-2)
   - Verify spacing is appropriate
2. Resize browser to mobile width
   - Verify grid collapses to single column
   - Verify all content remains readable
   - Verify buttons/selects are still accessible

**Expected Result:** ✅ Form is responsive and readable on all screen sizes

---

### Test 8: Dark Mode Support

**Objective:** Verify dark mode styling works for all new sections.

**Steps:**
1. Toggle dark mode in application
2. Verify:
   - Section headers are visible
   - Blue derived classifications panel adjusts to dark mode (`dark:bg-blue-900 dark:text-blue-100`)
   - All text is readable in dark mode
   - Form inputs are styled for dark mode

**Expected Result:** ✅ All elements properly styled in dark mode

---

## Known Limitations & Future Work

### Currently NOT Implemented (Awaiting Backend Phase 3)
- ❌ Automatic derivation of GPAI Classification based on Algorithm Type
- ❌ Automatic derivation of Contextual Criteria based on Deployment Context
- ❌ Logic to populate GPAI Classification and Contextual Criteria fields based on selections

### What This Phase DID Implement
- ✅ Frontend form structure reorganization
- ✅ Removed confusing manual GPAI/Contextual selects
- ✅ Added placeholders for derived classifications display
- ✅ Semantic clarity: fields show as read-only derived values (when populated)

### What Phase 3 Will Implement
- 🔄 Ontology v0.37.3 with explicit derivation rules
- 🔄 Backend logic to compute GPAI Classification from Algorithm Type
- 🔄 Backend logic to compute Contextual Criteria from Deployment Context
- 🔄 Frontend hooks to call backend derivation endpoints
- 🔄 Update form state when derived values change

---

## Regression Testing

### Critical Regressions to Check
- [ ] Form submission still creates systems correctly
- [ ] All 19 vocabulary endpoints still load (no broken dependencies)
- [ ] SystemCard displays all properties
- [ ] No JavaScript errors in console
- [ ] Form validation still works
- [ ] Pagination for system list works
- [ ] Filter/search functionality works

---

## Acceptance Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| 7 numbered sections visible | ✅ | Commit cab4951 |
| GPAI/Contextual manual selects removed | ✅ | Commit cab4951 |
| Derived classifications panel appears in code | ✅ | Commit cab4951 |
| No syntax/compilation errors | ⏳ | Awaiting npm install |
| Form submissions work | ⏳ | Awaiting docker-compose up |
| SystemCard renders correctly | ⏳ | Awaiting full app test |
| All vocab endpoints functional | ⏳ | Awaiting full app test |
| Dark mode works for all elements | ⏳ | Awaiting full app test |

---

## Test Environment Setup

### Required
1. Docker environment with both backend and frontend running
2. Node.js dependencies installed: `npm install` in frontend/
3. ONTOLOGY_PATH environment variable pointing to ontology file
4. MongoDB running (or Docker compose setup)

### Commands to Run Tests
```bash
# Start full environment
cd /home/cartesio/workspace/ai_act_public/ai_act_project
docker-compose up -d

# Run frontend build check
cd frontend
npm run build

# Run any tests (if configured)
npm run test

# View frontend in browser
# Open http://localhost:5173 (Vite dev server)
```

---

## Documentation Reference

- [ONTOLOGY_SIMPLIFICATION_PLAN.md](./ONTOLOGY_SIMPLIFICATION_PLAN.md) - Overall strategy
- [SystemsPage.tsx](./frontend/src/pages/SystemsPage.tsx) - Form implementation
- [SystemCard.tsx](./frontend/src/pages/SystemCard.tsx) - Card display component

---

## Sign-off

**Phase 2 Frontend Reorganization:** ✅ COMPLETE

**Phase 3 Backend Derivation:** 🔄 PENDING

**Commit:** cab4951 - Reorganize frontend form with logical section flow and derived classifications
