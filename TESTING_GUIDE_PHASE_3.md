# Phase 3 Testing Guide: Backend Derivation System

## Quick Start - Verify Implementation

### 1. Check File Structure
```bash
# Verify new files were created
ls -la backend/derivation.py               # Core derivation engine
ls -la backend/test_derivation.py          # Test suite (local, not in git)
grep -l "derive_classifications" backend/routers/systems.py  # Router integration
```

### 2. Verify Python Syntax
```bash
cd backend
python3 -c "import ast; ast.parse(open('derivation.py').read())" && echo "✓ derivation.py OK"
python3 -c "import ast; ast.parse(open('routers/systems.py').read())" && echo "✓ systems.py OK"
```

### 3. Run Unit Tests
```bash
cd backend
pytest test_derivation.py -v --tb=short
```

## API Testing

### Test 1: Derivation Preview Endpoint

**Purpose:** Test derivation without creating a system

```bash
curl -X POST http://localhost:8000/api/systems/derive-classifications \
  -H "Content-Type: application/json" \
  -d '{
    "hasPurpose": ["ai:EducationAccess"],
    "hasDeploymentContext": ["ai:Education"],
    "hasTrainingDataOrigin": ["ai:ExternalDataset"],
    "hasAlgorithmType": ["ai:TransformerModel"],
    "hasModelScale": "ai:RegularModelScale"
  }' | jq .
```

**Expected Response:**
```json
{
  "success": true,
  "derived": {
    "hasCriteria": ["ai:EducationEvaluationCriterion"],
    "hasComplianceRequirement": [
      "ai:DataGovernanceRequirement",
      "ai:TraceabilityRequirement",
      "ai:TransparencyRequirement",
      "ai:DocumentationRequirement"
    ],
    "hasRiskLevel": "ai:HighRisk",
    "hasGPAIClassification": []
  }
}
```

**What to Verify:**
- ✅ Returns `success: true`
- ✅ `hasCriteria` includes education-related criteria
- ✅ `hasComplianceRequirement` includes data governance and transparency
- ✅ `hasRiskLevel` is `ai:HighRisk` (education is high-risk per ontology)
- ✅ `hasGPAIClassification` is empty (RegularModelScale, not Foundation)

### Test 2: GPAI System Detection

**Purpose:** Verify GPAI classification triggers with FoundationModelScale

```bash
curl -X POST http://localhost:8000/api/systems/derive-classifications \
  -H "Content-Type: application/json" \
  -d '{
    "hasPurpose": ["ai:EducationAccess"],
    "hasDeploymentContext": ["ai:Education"],
    "hasTrainingDataOrigin": ["ai:InternalDataset"],
    "hasAlgorithmType": ["ai:TransformerModel"],
    "hasModelScale": "ai:FoundationModelScale"
  }' | jq '.derived.hasGPAIClassification'
```

**Expected Response:**
```json
["ai:GeneralPurposeAI"]
```

**What to Verify:**
- ✅ `hasGPAIClassification` includes `ai:GeneralPurposeAI`
- ✅ This only triggers with FoundationModelScale

### Test 3: Create System with Auto-Derivation

**Purpose:** Test that system creation automatically includes derived data

```bash
curl -X POST http://localhost:8000/api/systems \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "Education Assessment AI",
    "hasVersion": "2.0.0",
    "hasPurpose": ["ai:EducationAccess"],
    "hasDeploymentContext": ["ai:Education"],
    "hasTrainingDataOrigin": ["ai:ExternalDataset"],
    "hasAlgorithmType": ["ai:TransformerModel"],
    "hasModelScale": "ai:RegularModelScale"
  }' | jq .
```

**Expected Response:**
```json
{
  "inserted_id": "656d...",
  "urn": "urn:uuid:abc123..."
}
```

**Then Retrieve the Created System:**
```bash
curl http://localhost:8000/api/systems/urn:uuid:abc123... | jq .
```

**Expected to Include:**
```json
{
  "hasName": "Education Assessment AI",
  "hasVersion": "2.0.0",
  // USER INPUT:
  "hasPurpose": ["ai:EducationAccess"],
  "hasDeploymentContext": ["ai:Education"],
  "hasTrainingDataOrigin": ["ai:ExternalDataset"],
  // AUTOMATICALLY DERIVED:
  "hasCriteria": ["ai:EducationEvaluationCriterion"],
  "hasComplianceRequirement": ["ai:DataGovernanceRequirement", ...],
  "hasRiskLevel": "ai:HighRisk",
  "hasGPAIClassification": []
}
```

**What to Verify:**
- ✅ System creation returns URN and ID
- ✅ Retrieved system includes user input fields
- ✅ Retrieved system includes derived fields
- ✅ Derived fields match what preview endpoint returns

### Test 4: Multiple Purposes

**Purpose:** Test that derivation handles multiple purposes correctly

```bash
curl -X POST http://localhost:8000/api/systems/derive-classifications \
  -H "Content-Type: application/json" \
  -d '{
    "hasPurpose": ["ai:EducationAccess", "ai:EmploymentOrWorkCriteria"],
    "hasDeploymentContext": [],
    "hasTrainingDataOrigin": [],
    "hasAlgorithmType": [],
    "hasModelScale": ""
  }' | jq '.derived.hasCriteria | length'
```

**Expected:**
- Number > 0 (should have criteria from both purposes)

**What to Verify:**
- ✅ Multiple purposes are handled
- ✅ Criteria from all purposes are included
- ✅ No duplicates in results

### Test 5: Empty Input

**Purpose:** Test graceful handling of empty/minimal input

```bash
curl -X POST http://localhost:8000/api/systems/derive-classifications \
  -H "Content-Type: application/json" \
  -d '{
    "hasPurpose": [],
    "hasDeploymentContext": [],
    "hasTrainingDataOrigin": [],
    "hasAlgorithmType": [],
    "hasModelScale": ""
  }' | jq '.derived'
```

**Expected Response:**
```json
{
  "hasCriteria": [],
  "hasComplianceRequirement": [],
  "hasRiskLevel": "ai:MinimalRisk",
  "hasGPAIClassification": []
}
```

**What to Verify:**
- ✅ Empty input doesn't crash
- ✅ Returns valid empty structure
- ✅ Default RiskLevel is MinimalRisk
- ✅ No false positives for GPAI

## Integration Testing

### Test 6: Full Workflow

**Purpose:** Test complete flow from form submission to retrieval

```bash
#!/bin/bash

# Step 1: Create system
echo "Creating system..."
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/systems \
  -H "Content-Type: application/json" \
  -d '{
    "hasName": "Healthcare Diagnosis System",
    "hasVersion": "1.0.0",
    "hasPurpose": ["ai:HealthcareSupport"],
    "hasDeploymentContext": ["ai:Healthcare"],
    "hasTrainingDataOrigin": ["ai:ExternalDataset"],
    "hasAlgorithmType": ["ai:DeepLearningModel"],
    "hasModelScale": "ai:RegularModelScale"
  }')

URN=$(echo "$CREATE_RESPONSE" | jq -r '.urn')
echo "Created system with URN: $URN"

# Step 2: Retrieve created system
echo ""
echo "Retrieving created system..."
SYSTEM=$(curl -s "http://localhost:8000/api/systems/$URN")

# Step 3: Verify derived data
echo ""
echo "Verifying derived classifications..."
echo "Criteria: $(echo "$SYSTEM" | jq '.hasCriteria')"
echo "Risk Level: $(echo "$SYSTEM" | jq -r '.hasRiskLevel')"
echo "Requirements count: $(echo "$SYSTEM" | jq '.hasComplianceRequirement | length')"

# Step 4: Compare with preview
echo ""
echo "Comparing with preview endpoint..."
PREVIEW=$(curl -s -X POST http://localhost:8000/api/systems/derive-classifications \
  -H "Content-Type: application/json" \
  -d '{
    "hasPurpose": ["ai:HealthcareSupport"],
    "hasDeploymentContext": ["ai:Healthcare"],
    "hasTrainingDataOrigin": ["ai:ExternalDataset"],
    "hasAlgorithmType": ["ai:DeepLearningModel"],
    "hasModelScale": "ai:RegularModelScale"
  }')

PREVIEW_CRITERIA=$(echo "$PREVIEW" | jq '.derived.hasCriteria')
SYSTEM_CRITERIA=$(echo "$SYSTEM" | jq '.hasCriteria')

if [ "$PREVIEW_CRITERIA" == "$SYSTEM_CRITERIA" ]; then
  echo "✅ System criteria matches preview"
else
  echo "❌ Mismatch between system and preview"
fi
```

**Expected Output:**
- ✅ System created successfully
- ✅ System retrieved with all derived fields
- ✅ Criteria matches preview endpoint
- ✅ RiskLevel is appropriate for healthcare (typically HighRisk)
- ✅ Multiple requirements derived

## Logging and Debugging

### Enable Debug Logging

```bash
# Run backend with verbose logging
PYTHONUNBUFFERED=1 python3 -m uvicorn main:app \
  --log-level debug \
  --reload
```

### Watch Derivation Logs

When creating a system, check logs for:
```
Starting derivation with input: {...}
Processing Purpose: ai:EducationAccess
  -> activatesCriterion: {'ai:EducationEvaluationCriterion'}
Processing DeploymentContext: ai:Education
  -> triggersCriterion: {'ai:EducationEvaluationCriterion'}
...
Determined max risk level: ai:HighRisk
Derivation complete. Result: {...}
```

### Test with Debug Endpoint

```bash
# Get TTL representation of a system (if debug endpoint exists)
curl http://localhost:8000/reasoning/test-ttl/urn:uuid:... | jq .
```

## Performance Testing

### Test Derivation Speed

```bash
#!/bin/bash

echo "Measuring derivation time..."
time curl -X POST http://localhost:8000/api/systems/derive-classifications \
  -H "Content-Type: application/json" \
  -d '{
    "hasPurpose": ["ai:EducationAccess"],
    "hasDeploymentContext": ["ai:Education"],
    "hasTrainingDataOrigin": ["ai:ExternalDataset"],
    "hasAlgorithmType": ["ai:TransformerModel"],
    "hasModelScale": "ai:RegularModelScale"
  }' > /dev/null
```

**Expected:**
- Should complete in < 200ms
- Typical: 50-100ms

### Batch Performance

```bash
#!/bin/bash

echo "Testing batch system creation..."
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/api/systems \
    -H "Content-Type: application/json" \
    -d "{
      \"hasName\": \"System $i\",
      \"hasVersion\": \"1.0.0\",
      \"hasPurpose\": [\"ai:EducationAccess\"],
      \"hasDeploymentContext\": [\"ai:Education\"],
      \"hasTrainingDataOrigin\": [\"ai:ExternalDataset\"],
      \"hasAlgorithmType\": [\"ai:TransformerModel\"],
      \"hasModelScale\": \"ai:RegularModelScale\"
    }" > /dev/null && echo "✓ Created system $i"
done
```

**Expected:**
- All 10 create successfully
- Total time < 2 seconds

## Troubleshooting

### Issue: "Error deriving classifications"

**Possible Causes:**
1. Ontology not loaded - Check ONTOLOGY_PATH environment variable
2. Invalid input format - Verify JSON structure
3. Missing ontology instances - Verify v0.37.2 has all instances

**Debug:**
```bash
# Check ontology is loaded
curl http://localhost:8000/vocab/purposes | jq '.[] | select(.id == "ai:EducationAccess")'
```

### Issue: Derived fields empty

**Possible Causes:**
1. Ontology relationships not defined
2. Purpose/Context instances missing
3. Derivation logic not following relationships

**Debug:**
```bash
# Check if Purpose has activation relationships
# Use debug endpoint (if available) or check ontology directly
rdfgrep "EducationAccess" /ontologias/versions/0.37.2/ontologia-v0.37.2.ttl
```

### Issue: Wrong risk level

**Possible Causes:**
1. Criteria not being derived correctly
2. Risk hierarchy logic issue
3. Ontology relationships missing

**Debug:**
- Enable debug logging (see above)
- Check logs for "Processing Criterion"
- Verify criteria → assignsRiskLevel relationships

## Checklist for Phase 3 Verification

- [ ] Syntax validation passes
- [ ] Unit tests pass (pytest)
- [ ] Derivation preview endpoint works
- [ ] GPAI detection works
- [ ] System creation includes derived fields
- [ ] Multiple purposes handled correctly
- [ ] Empty input handled gracefully
- [ ] Full workflow integration works
- [ ] Derived data matches preview
- [ ] Performance acceptable (<200ms)
- [ ] Batch operations work
- [ ] Error handling works
- [ ] Logging shows derivation steps

## What's Next?

After verifying all tests pass:
1. Deploy backend with derivation logic
2. Test frontend form submission
3. Verify frontend displays derived data
4. Monitor logs for any issues
5. Consider caching enhancements if needed

---

**Documentation Location:** This file
**Test Files Location:** `backend/test_derivation.py`
**Implementation:** `backend/derivation.py` and `backend/routers/systems.py`
**Status:** Ready for testing
