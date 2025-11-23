# Post-Incident Forensic Analysis: Visual Guide

## The Problem

When an AI security incident occurs, regulators must answer:
- ❓ **What risk classification SHOULD the system have had?**
- ❓ **What compliance requirements SHOULD have been implemented?**
- ❓ **Were violations intentional or due to misclassification?**
- ❓ **What other systems have the same vulnerability?**

## The Solution: Reverse Engineering via Ontology

```
┌─────────────────────────────────────────────────────────┐
│         INCIDENT OCCURS (Data Breach)                   │
├─────────────────────────────────────────────────────────┤
│ System: Biometric Identification at Airport             │
│ Classified as: "Minimal Risk"                           │
│ Incident: 50,000 travelers' biometric data leaked      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│      QUERY ONTOLOGY FOR PROPER CLASSIFICATION           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  System Properties:                                     │
│  - hasPurpose: BiometricIdentification                 │
│  - hasDeploymentContext: MigrationControl              │
│  - hasDeploymentContext: PublicSpaces                  │
│                                                         │
│  SPARQL Query:                                          │
│  SELECT ?criterion                                      │
│  WHERE {                                                │
│    ai:BiometricIdentification                          │
│      ai:activatesCriterion ?criterion .                │
│    ai:MigrationControl                                 │
│      ai:triggersCriterion ?criterion .                 │
│  }                                                      │
│                                                         │
│  ⬇️  RESULT:                                              │
│  ✓ BiometricIdentificationCriterion (Annex III)        │
│  ✓ MigrationBorderCriterion (Annex III)                │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│   IDENTIFY MANDATORY REQUIREMENTS FROM CRITERIA          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  BiometricIdentificationCriterion.activatesRequirement:│
│  ├─ DataGovernanceRequirement                          │
│  ├─ FundamentalRightsAssessmentRequirement             │
│  ├─ HumanOversightRequirement                          │
│  ├─ TransparencyRequirement                            │
│  └─ BiometricSecurityRequirement ⚠️                    │
│                                                         │
│  MigrationBorderCriterion.activatesRequirement:        │
│  ├─ RiskAssessmentRequirement                          │
│  ├─ LegalFrameworkRequirement                          │
│  └─ HumanOversightRequirement (already counted)        │
│                                                         │
│  ⬇️  MERGED MANDATORY REQUIREMENTS:                      │
│  ✓ DataGovernanceRequirement                           │
│  ✓ FundamentalRightsAssessmentRequirement              │
│  ✓ HumanOversightRequirement                           │
│  ✓ TransparencyRequirement                             │
│  ✓ BiometricSecurityRequirement ⚠️                     │
│  ✓ RiskAssessmentRequirement                           │
│  ✓ LegalFrameworkRequirement                           │
│                                                         │
│  Total: 7 mandatory requirements                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│        DETECT COMPLIANCE GAPS (NOT IMPLEMENTED)         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Checking what was ACTUALLY implemented:               │
│                                                         │
│  ✓ Implemented:                                         │
│    ├─ DataGovernanceRequirement (basic encryption)     │
│    ├─ TransparencyRequirement (legal notice)           │
│    ├─ RiskAssessmentRequirement (documented)           │
│    └─ LegalFrameworkRequirement (within scope)         │
│                                                         │
│  ✗ MISSING:                                             │
│    ├─ BiometricSecurityRequirement ⚠️ ROOT CAUSE       │
│    ├─ HumanOversightRequirement                        │
│    ├─ FundamentalRightsAssessmentRequirement           │
│                                                         │
│  Compliance Status:                                     │
│  ✓ 4/7 requirements implemented (57%)                   │
│  ✗ 3/7 requirements missing (43%) - VIOLATION          │
│                                                         │
│  Critical Gap:                                          │
│  ❌ BiometricSecurityRequirement was MISSING            │
│     └─ This would have required:                       │
│        ├─ Encryption of biometric templates            │
│        ├─ Secure access controls                       │
│        └─ Audit trails → Would have detected breach    │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│   ARTICLE 6(3) RESIDUAL RISK ASSESSMENT                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Expert Evaluation (Post-Incident):                    │
│  "System exhibited unexpected data leakage patterns    │
│   suggesting inadequate access controls and encryption"│
│                                                         │
│  ⬇️  Expert Identifies Additional Criteria (Art. 6(3)):  │
│  ├─ AccessControlRiskCriterion                         │
│  ├─ DataProtectionRiskCriterion                        │
│  └─ EncryptionRiskCriterion                            │
│                                                         │
│  ⬇️  These Activate Additional Requirements:             │
│  ├─ AccessControlRequirement (was missing)             │
│  ├─ EncryptionRequirement (was missing)                │
│  ├─ AuditTrailRequirement (was missing)                │
│  └─ DataMinimizationRequirement (was missing)          │
│                                                         │
│  Hidden Requirements Revealed: 4 more violations       │
│  Total Violations: 7/7 critical requirements missing   │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│         FORENSIC AUDIT REPORT GENERATION                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ╔════════════════════════════════════════════════════╗│
│  ║ FORENSIC COMPLIANCE AUDIT REPORT                   ║│
│  ║ Incident: Biometric Data Breach (2025-11-23)      ║│
│  ║ System: Airport Border Control                     ║│
│  ╚════════════════════════════════════════════════════╝│
│                                                         │
│  1️⃣  CLASSIFICATION ANALYSIS                            │
│      Declared Risk Level: MINIMAL RISK ❌               │
│      Proper Risk Level:   HIGH RISK ✓                  │
│      Basis: Annex III - Biometric + Migration Control  │
│                                                         │
│  2️⃣  COMPLIANCE GAP ANALYSIS                            │
│      Required Requirements: 7                          │
│      Implemented:           4 (57%)                    │
│      Missing:               3 (43%) ❌                  │
│                                                         │
│      Critical Missing:                                 │
│      ❌ BiometricSecurityRequirement                   │
│      ❌ HumanOversightRequirement                      │
│      ❌ FundamentalRightsAssessmentRequirement         │
│                                                         │
│  3️⃣  INCIDENT ROOT CAUSE                               │
│      Primary: BiometricSecurityRequirement not met     │
│      Secondary: AccessControlRequirement not met       │
│      Tertiary: EncryptionRequirement not met           │
│                                                         │
│      Chain of Failure:                                 │
│      No BiometricSecurityRequirement                   │
│         ↓                                              │
│      No encryption of templates                        │
│         ↓                                              │
│      Templates stored plaintext                        │
│         ↓                                              │
│      Attacker accessed unencrypted data                │
│         ↓                                              │
│      50,000 biometric records leaked                   │
│                                                         │
│  4️⃣  LEGAL VIOLATIONS                                   │
│      ❌ Article 6(1) - Failure to properly classify    │
│      ❌ Annex III Obligations - Not implemented        │
│      ❌ Article 52(1) - Insufficient transparency      │
│      ❌ Article 22 - Inadequate documentation          │
│                                                         │
│  5️⃣  ENFORCEMENT RECOMMENDATION                         │
│      Violation Severity:     CRITICAL                  │
│      Estimated Fine:         €8-12 million             │
│      (Based on turnover and violation severity)        │
│      Additional Penalties:   System deactivation       │
│      Mandatory Actions:      Full security audit       │
│                                                         │
│  6️⃣  SYSTEMIC RISK ANALYSIS                            │
│      Other Systems with Similar Gap:                  │
│      - 23 other biometric systems deployed             │
│      - 12 have same missing BiometricSecurityReq       │
│      - Recommended proactive audit of all 12           │
│                                                         │
│  ╔════════════════════════════════════════════════════╗│
│  ║ CONCLUSION: Willful negligence or gross oversight?  ║║
│  ║ The missing BiometricSecurityRequirement was        ║║
│  ║ MANDATORY under Annex III. Its absence caused the   ║║
│  ║ data breach. This violation was predictable from    ║║
│  ║ system classification.                              ║║
│  ╚════════════════════════════════════════════════════╝│
│                                                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│    PROACTIVE VULNERABILITY DETECTION                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SPARQL Query finds OTHER systems at risk:             │
│                                                         │
│  Systems with BiometricIdentification purpose          │
│  AND missing BiometricSecurityRequirement:             │
│                                                         │
│  ✗ System A: Prague Airport (HIGH RISK)                │
│  ✗ System B: Vienna Station (HIGH RISK)                │
│  ✗ System C: Berlin Border (HIGH RISK)                 │
│  ✗ System D: Lyon Airport (MEDIUM RISK)                │
│  ... (12 total)                                        │
│                                                         │
│  Proactive Actions:                                    │
│  1. Immediate security audit of all 12 systems         │
│  2. Require BiometricSecurityRequirement implementation │
│  3. Review stored biometric data for exposure          │
│  4. Notify affected data subjects                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Key Innovation: Ontology as Compliance Standard

The breakthrough is that **the ontology itself IS the compliance standard**:

```
┌─────────────────────────────────────────────────────────┐
│                 TRADITIONAL APPROACH                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Incident occurs                                        │
│      ↓                                                  │
│  Regulator reads EU AI Act (274 pages)                 │
│      ↓                                                  │
│  Interprets relevant articles (ambiguous)              │
│      ↓                                                  │
│  Determines what SHOULD have been done                 │
│      ↓                                                  │
│  [Weeks of analysis]                                   │
│      ↓                                                  │
│  Enforcement decision (inconsistent across cases)      │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│            ONTOLOGY-BASED APPROACH                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Incident occurs                                        │
│      ↓                                                  │
│  Query ontology with system properties                 │
│      ↓                                                  │
│  Get AUTHORITATIVE list of requirements                │
│      ↓                                                  │
│  Compare with actual implementation                    │
│      ↓                                                  │
│  [Automated SML analysis - minutes]                    │
│      ↓                                                  │
│  Enforcement decision (consistent, transparent)        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Why This Matters for SML/AI Agents

An intelligent agent can now:

1. **Deterministically classify** systems based on their properties
2. **Exhaustively enumerate** all applicable requirements (no gaps)
3. **Objectively identify** violations (requirement is missing → violation)
4. **Explain reasoning** through ontology traversal (full audit trail)
5. **Prevent false positives** (misclassification) through systematic analysis
6. **Support defense** (system operator can show they WERE in scope)
7. **Identify systemic issues** across multiple systems
8. **Calculate penalties** based on objective violation counts

## From Incident to Enforcement Action

```
     Biometric Data Breach
           (Incident)
              │
              ▼
     Forensic Analysis
    (Ontology Queries)
              │
        ┌─────┴─────┐
        ▼           ▼
    Root Causes    Other Systems
    - Missing     at Risk
      BiometricSecurity
    - Missing
      Encryption   │
    - Missing      ▼
      Audit Trail
        │        Proactive Audit
        │        of 12 other
        ▼        systems
   Compliance
   Violations
        │
        ▼
   Enforcement
   Actions
   ├─ €8-12M Fine
   ├─ System Deactivation
   ├─ Mandatory Audit
   └─ Fix 12 other systems
```

## Technical Implementation

The ontology queries can be executed by:

1. **Python backend** (via RDFLib)
   ```python
   from rdflib import Graph
   results = graph.query(sparql_query)
   ```

2. **SML reasoning engines** (Jena, Pellet)
   ```
   Forward chaining: Purpose + Context → Criteria → Requirements
   ```

3. **Regular SPARQL endpoints** (Fuseki)
   ```
   HTTP POST to /ds/sparql
   ```

4. **Automated enforcement systems**
   ```
   Incident Event → Query Ontology → Determine Violations → Generate Fines
   ```

## Advantages Over Manual Analysis

| Aspect | Manual | Ontology-Based |
|--------|--------|-----------------|
| **Time** | Weeks | Minutes |
| **Consistency** | Varies by analyst | 100% consistent |
| **Completeness** | Might miss requirements | Exhaustive enumeration |
| **Explainability** | "Article X says..." | Full ontology trace |
| **Scalability** | Expensive for many cases | Scales to thousands |
| **Appeal-proof** | Subjective interpretation | Objective factual |
| **Preventive** | Only reactive | Identifies at-risk systems |

---

**This is why the EU AI Act Unified Ontology is not just documentation—it's an enforcement tool.**
