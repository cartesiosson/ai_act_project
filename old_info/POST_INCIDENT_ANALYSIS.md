# Post-Incident Analysis: Using the EU AI Act Ontology for Forensic Compliance Auditing

## Overview

The EU AI Act Unified Ontology (v0.37.2) can be leveraged for **post-incident forensic analysis** to identify what compliance requirements a system should have met when an incident occurs. This enables regulators, auditors, and security teams to:

1. **Reverse-engineer** the system's classification at time of incident
2. **Identify applicable requirements** that should have been implemented
3. **Compare actual implementation** against mandated requirements
4. **Generate compliance audit reports** for enforcement actions
5. **Support SML-based reasoning** for automated incident analysis

## Use Case: Security Incident Analysis

### Scenario

A biometric identification system deployed in a European airport is discovered to have had a data breach affecting 50,000 travelers. The system was classified as "minimal risk" but the incident reveals unexpected vulnerabilities.

**Questions to answer:**
- What risk classification should this system have had?
- What compliance requirements were mandatory?
- What security controls should have been in place?
- Was the classification adequate for deployment?

## How the Ontology Enables Post-Incident Analysis

### Step 1: Reconstruct System Classification

Given an incident context, an SML agent can query the ontology to determine proper classification:

```sparql
# Query: What criteria should activate for a biometric system in airport context?
PREFIX ai: <http://ai-act.eu/ai#>

SELECT ?criterion ?label ?requirement
WHERE {
  # System purpose: Biometric Identification
  ai:BiometricIdentification ai:activatesCriterion ?criterion .

  # System context: Border/Migration Control (airports)
  ai:MigrationControl ai:activatesCriterion ?criterion2 .

  # What requirements do these criteria activate?
  ?criterion ai:activatesRequirement ?requirement .
  ?requirement rdfs:label ?label .
}
```

### Step 2: Identify Mandatory Requirements

Once criteria are identified, traverse to requirements:

```
System Input:
- hasPurpose: BiometricIdentification
- hasDeploymentContext: MigrationControl

↓ Ontology Traversal:

BiometricIdentification.activatesCriterion → BiometricIdentificationCriterion
BiometricIdentificationCriterion.activatesRequirement → [
  DataGovernanceRequirement,
  FundamentalRightsAssessmentRequirement,
  HumanOversightRequirement,
  TransparencyRequirement,
  BiometricSecurityRequirement
]

MigrationControl.activatesCriterion → MigrationBorderCriterion
MigrationBorderCriterion.activatesRequirement → [
  RiskAssessmentRequirement,
  LegalFrameworkRequirement,
  HumanOversightRequirement
]

↓ Merged Requirements (Union):
- DataGovernanceRequirement ✓
- FundamentalRightsAssessmentRequirement ✓
- HumanOversightRequirement ✓
- TransparencyRequirement ✓
- BiometricSecurityRequirement ✓
- RiskAssessmentRequirement ✓
- LegalFrameworkRequirement ✓
```

### Step 3: Article 6(3) Residual Risk Assessment

The ontology also supports Article 6(3) expert evaluation after incidents:

```
Post-Incident Finding:
"System exhibited unexpected data leakage patterns suggesting inadequate access controls"

↓ Expert Evaluation (Article 6(3)):

Additional Manual Criteria:
- AccessControlRiskCriterion
- DataProtectionRiskCriterion

↓ Derive Additional Requirements:

AccessControlRiskCriterion.activatesRequirement → [
  AccessControlRequirement,
  EncryptionRequirement,
  AuditTrailRequirement
]

DataProtectionRiskCriterion.activatesRequirement → [
  DataMinimizationRequirement,
  DataRetentionPolicyRequirement
]

↓ Total Compliance Gap:
These requirements were NOT identified in original classification
but SHOULD have been based on system architecture
```

### Step 4: Generate Compliance Report

The ontology enables structured audit reports:

```
FORENSIC COMPLIANCE AUDIT REPORT
System: Biometric Border Control System
Incident Date: 2025-11-23
Analysis Date: 2025-11-24

═══════════════════════════════════════════════════════════

1. CLASSIFICATION RECONSTRUCTION

   Proper Classification (per EU AI Act):
   ├─ Annex III Category: Biometric Identification + Migration Control
   ├─ Risk Level: HIGH RISK
   └─ Basis: Multiple high-risk indicators

2. MANDATORY REQUIREMENTS (per Ontology)

   ✓ DataGovernanceRequirement
     └─ Status: [IMPLEMENTED|MISSING|PARTIAL]

   ✓ FundamentalRightsAssessmentRequirement
     └─ Status: [IMPLEMENTED|MISSING|PARTIAL]

   ✓ HumanOversightRequirement
     └─ Status: [IMPLEMENTED|MISSING|PARTIAL]

   ✓ TransparencyRequirement
     └─ Status: [IMPLEMENTED|MISSING|PARTIAL]

   ✓ BiometricSecurityRequirement
     └─ Status: MISSING ← ROOT CAUSE OF INCIDENT

   ✓ RiskAssessmentRequirement
     └─ Status: INCOMPLETE

3. ARTICLE 6(3) RESIDUAL RISK (Post-Incident)

   Expert Finding: Incident reveals inadequate access controls

   Additional Criteria: DataProtectionRiskCriterion
   Additional Requirements: AccessControlRequirement, EncryptionRequirement

4. COMPLIANCE GAP ANALYSIS

   Total Required Requirements: 9
   Implemented Requirements: 5
   Missing/Incomplete: 4

   Critical Gaps:
   - BiometricSecurityRequirement (MISSING) - directly related to incident
   - AccessControlRequirement (MISSING) - enabled data breach
   - EncryptionRequirement (MISSING) - would have prevented leakage
   - AuditTrailRequirement (MISSING) - insufficient incident detection

5. ENFORCEMENT RECOMMENDATION

   Violations Found:
   - Inadequate risk classification (classified as minimal, should be high-risk)
   - Non-compliance with Annex III high-risk obligations
   - Failure to implement Article 6(3) mandatory controls

   Recommended Actions:
   - Immediate system deactivation pending remediation
   - €X,XXX,XXX administrative fine (per Article 84)
   - Mandatory security audit before redeployment
```

## Ontology Structure for Forensic Analysis

### Key Properties for Post-Incident Use

```turtle
# Criteria Definition
ai:BiometricIdentificationCriterion
  a ai:Criterion ;
  ai:activatesRequirement ai:BiometricSecurityRequirement ;
  ai:activatesRequirement ai:FundamentalRightsAssessmentRequirement ;
  ai:activatesRequirement ai:DataGovernanceRequirement ;
  ai:activatesRequirement ai:TransparencyRequirement .

# Requirement Definitions (showing dependencies)
ai:BiometricSecurityRequirement
  a ai:SecurityRequirement ;
  rdfs:label "Biometric Security Requirement"@en ;
  ai:requiresImplementation [
    ai:controlType "AccessControl" ;
    ai:controlType "Encryption" ;
    ai:controlType "BiometricTemplateProtection"
  ] .

ai:DataGovernanceRequirement
  a ai:ComplianceRequirement ;
  ai:impliesRequirement ai:DataMinimizationRequirement ;
  ai:impliesRequirement ai:DataRetentionPolicyRequirement ;
  ai:impliesRequirement ai:AuditTrailRequirement .
```

### SML/Machine Learning Integration

The ontology structure enables SML-based reasoning:

```python
# Pseudo-code for SML-based incident analysis

class IncidentAnalyzer:
    def analyze_incident(self, incident_report):
        """
        Given an incident report with system details,
        use SML reasoning to identify violated requirements
        """

        # Step 1: Extract system properties from incident
        system_purpose = incident_report.extract("purpose")
        system_context = incident_report.extract("deployment_context")
        incident_type = incident_report.extract("incident_type")

        # Step 2: Query ontology for proper classification
        proper_criteria = self.ontology.query(
            f"CRITERIA_ACTIVATED_BY({system_purpose}, {system_context})"
        )

        # Step 3: Get all mandatory requirements
        required_requirements = set()
        for criterion in proper_criteria:
            requirements = self.ontology.query(
                f"REQUIREMENTS_ACTIVATED_BY({criterion})"
            )
            required_requirements.update(requirements)

        # Step 4: Identify incident-specific requirements
        incident_requirements = self.ontology.query(
            f"REQUIREMENTS_FOR_INCIDENT_TYPE({incident_type})"
        )
        required_requirements.update(incident_requirements)

        # Step 5: Compare with actual implementation
        actual_requirements = incident_report.extract("implemented_controls")

        compliance_gaps = required_requirements - actual_requirements

        # Step 6: Generate audit finding
        return {
            "classification": proper_criteria,
            "required_requirements": required_requirements,
            "implemented": actual_requirements,
            "gaps": compliance_gaps,
            "severity": self.assess_severity(compliance_gaps, incident_type)
        }
```

## Advanced Forensic Queries

### Query 1: Find All High-Risk Systems That Failed Security Controls

```sparql
PREFIX ai: <http://ai-act.eu/ai#>

SELECT ?system ?purpose ?missingRequirement
WHERE {
  # Find systems classified as high-risk
  ?system ai:hasRiskLevel ai:HighRisk ;
           ai:hasPurpose ?purpose .

  # What security requirements should they have?
  ?purpose ai:activatesCriterion ?criterion .
  ?criterion ai:activatesRequirement ?requirement .
  ?requirement a ai:SecurityRequirement .

  # Which systems are missing these security requirements?
  MINUS {
    ?system ai:hasComplianceRequirement ?requirement .
  }

  BIND(?requirement AS ?missingRequirement)
}
ORDER BY ?system
```

### Query 2: Identify Systems Vulnerable to Data Breaches

```sparql
PREFIX ai: <http://ai-act.eu/ai#>

SELECT ?system ?label ?riskGap
WHERE {
  # Systems processing personal data
  ?system ai:processesDataType ai:PersonalData ;
          ai:hasRiskLevel ?riskLevel .

  # Get data governance requirements
  ?purpose ai:activatesCriterion ?criterion .
  ?criterion ai:activatesRequirement ai:DataGovernanceRequirement ;
             ai:activatesRequirement ai:EncryptionRequirement .

  # Which systems are missing encryption?
  MINUS {
    ?system ai:hasComplianceRequirement ai:EncryptionRequirement .
  }

  BIND(concat("Missing encryption for ", ?riskLevel) AS ?riskGap)
}
```

### Query 3: Article 6(3) Residual Risk Identification

```sparql
PREFIX ai: <http://ai-act.eu/ai#>

# Find systems where Annex III classification alone is insufficient
SELECT ?system ?manualCriterion ?additionalRequirements
WHERE {
  # Systems with manual criteria (Article 6(3))
  ?system ai:hasManuallyIdentifiedCriterion ?manualCriterion .

  # What requirements do these add?
  ?manualCriterion ai:activatesRequirement ?additionalRequirements .

  # Were these requirements already activated by Annex III?
  MINUS {
    ?system ai:hasActivatedCriterion ?criterion .
    ?criterion ai:activatesRequirement ?additionalRequirements .
  }

  # So these are "hidden" requirements that Annex III missed
}
```

## Implementation Roadmap

### Phase 1: Basic Forensic Queries (Current)
- [x] Ontology structure supports requirement tracing
- [x] SPARQL queries can identify mandatory requirements
- [ ] Create forensic query library in separate module
- [ ] Build query helper functions

### Phase 2: SML-Based Analysis (Future)
- [ ] Integrate with SML engines (e.g., Apache Jena, Pellet)
- [ ] Implement incident-to-classification mapping
- [ ] Build automated compliance gap detection
- [ ] Create forensic report generation

### Phase 3: Regulatory Integration (Future)
- [ ] API endpoint for forensic analysis
- [ ] Integration with incident reporting systems
- [ ] Automated fine calculation based on gaps
- [ ] Timeline reconstruction (what SHOULD have been done)

## Key Advantages of This Approach

| Aspect | Benefit |
|--------|---------|
| **Objectivity** | Classification is deterministic based on EU AI Act rules |
| **Completeness** | All mandatory requirements automatically identified |
| **Traceability** | Every compliance gap can be traced to specific EU regulation |
| **Consistency** | Same rules applied to all systems regardless of owner |
| **Automation** | SML can identify violations without human interpretation |
| **Evidence** | Ontology serves as authoritative compliance standard |
| **Prevention** | Can identify similar risks in other systems |

## Limitations & Considerations

1. **Factual Accuracy**: Ontology assumes correct system classification input
   - Real-world incidents may reveal intentional misclassification
   - Requires verification of system properties

2. **Emerging Risks**: Article 6(3) criteria must be evaluated by experts
   - Ontology captures known residual risks, not novel threats
   - New incident types may reveal gaps in ontology

3. **Implementation Details**: Ontology specifies WHAT requirements apply, not HOW
   - Compliance auditing still requires technical assessment
   - Requirements must be translated to concrete controls

4. **Legal Interpretation**: EU AI Act interpretation may evolve
   - Ontology reflects current understanding
   - Regular updates needed as guidance evolves

## Next Steps

1. **Create forensic query library** with common incident analysis patterns
2. **Build SML integration** for automated analysis
3. **Develop API endpoint** for post-incident analysis
4. **Establish feedback loop** between incident findings and ontology updates
5. **Integrate with regulatory systems** for enforcement actions

---

**Document Purpose**: Guide for using EU AI Act Unified Ontology in forensic compliance auditing and post-incident analysis.

**Last Updated**: 2025-11-23 | **Status**: Proposed Framework
