# EU AI Act Multi-Framework Mappings

> Bidirectional mappings between EU AI Act compliance requirements and international AI governance frameworks

## Overview

This directory contains formal RDF/OWL mappings between:
- **EU AI Act** compliance requirements (Articles 9-15, 27, 43, 72-73, Annex III)
- **ISO/IEC 42001:2023** AI Management System controls (Sections 5-10)
- **NIST AI RMF 1.0** Risk Management Framework functions and categories
- **W3C DPV 2.2** Data Privacy Vocabulary measures
- **ELI** European Legislation Identifier for EUR-Lex links

**Purpose:** Enable multi-framework compliance analysis, forensic incident investigation, corporate audit integration, and cross-jurisdictional incident analysis.

---

## Files

| File | Description | Status |
|------|-------------|--------|
| `iso-42001-mappings.ttl` | Core 15 ISO mappings (Phase 2) | ✅ Active |
| `nist-ai-rmf-mappings.ttl` | 16 NIST AI RMF mappings (Phase 3) | ✅ Active |
| `dpv-integration.ttl` | W3C DPV 2.2 integration + ELI URIs (v0.2.0) | ✅ Active |

---

## ELI Integration

All requirements in this ontology now include **European Legislation Identifier (ELI)** URIs for direct links to EUR-Lex. This enables:

- **Dereferenceable URIs**: Direct access to official legislation text
- **Persistent Identifiers**: Stable references across legislative consolidations
- **Machine-Readable References**: Semantic Web compliance

**ELI Base URI**: `http://data.europa.eu/eli/reg/2024/1689`

**Example**:
```turtle
ai:HumanOversightRequirement
    ai:articleReference "Article 14" ;
    eli:cites <http://data.europa.eu/eli/reg/2024/1689/art_14/oj> .
```

**Reference Standards**:
- Council Conclusions 2012/C 325/02
- Decision (EU) 2017/1191

---

## EU-Specific Requirements (Not Mapped)

The following EU AI Act requirements are **intentionally not mapped** to ISO 42001 or NIST AI RMF as they are EU-specific regulatory prohibitions without direct equivalents in international standards:

### Article 5: Prohibited Practices (Unacceptable Risk)

**Status:** ⚠️ Not mapped to ISO/NIST (EU-specific absolute prohibitions)

**Reason:** Article 5 prohibitions are **absolute legal bans** specific to EU law with no equivalent in ISO 42001 (management system standard) or NIST AI RMF (voluntary risk framework). These are regulatory red lines, not manageable risks.

**Prohibited Practices:**
1. **SubliminalManipulationCriterion** (Art. 5.1.a) - Subliminal manipulation
2. **VulnerabilityExploitationCriterion** (Art. 5.1.b) - Exploitation of vulnerabilities
3. **SocialScoringCriterion** (Art. 5.1.c) - Social scoring by public authorities
4. **PredictivePolicingProfilingCriterion** (Art. 5.1.d) - Predictive policing by profiling
5. **RealTimeBiometricIdentificationCriterion** (Art. 5.1.h) - Real-time biometric ID in public spaces

**Penalty:** Systems with these practices CANNOT be deployed in the EU. Maximum fines: €35M or 7% global annual turnover.

**Exception:** Only real-time biometric identification has limited exceptions under Article 5.2 (victim search, terrorist threat, serious crimes) requiring prior judicial authorization.

---

## ISO 42001 Mappings (v1.0.0)

### Coverage

**Total Mappings:** 15 essential controls
**Confidence Distribution:**
- HIGH: 13 mappings (87%)
- MEDIUM: 2 mappings (13%)

**ISO Sections Covered:**
- 5.1 - Leadership and commitment
- 8.1 - Risk assessment and treatment
- 8.2 - Performance evaluation
- 8.3 - Data governance
- 8.4 - Documentation and records
- 8.5 - Information security
- 8.6 - Human oversight
- 8.7 - Transparency and explainability
- 9.1 - Monitoring and measurement
- 9.2 - Internal audit
- 10.1 - Incident management

---

## Core Mappings Table

| EU AI Act Requirement | ISO 42001 Control | Section | Confidence |
|----------------------|-------------------|---------|------------|
| DataGovernanceRequirement | Data governance | 8.3 | HIGH |
| BiometricSecurityRequirement | Information security - Biometric | 8.5 | HIGH |
| HumanOversightRequirement | Human oversight | 8.6 | HIGH |
| TransparencyRequirement | Transparency and explainability | 8.7 | HIGH |
| AccuracyRequirement | Performance evaluation | 8.2 | HIGH |
| RiskAssessmentRequirement | Risk assessment and treatment | 8.1 | HIGH |
| DocumentationRequirement | Documentation and records | 8.4 | HIGH |
| RobustnessRequirement | Robustness testing | 8.2.2 | HIGH |
| NonDiscriminationRequirement | Bias detection and mitigation | 8.3.3 | HIGH |
| FundamentalRightsAssessmentRequirement | Leadership and commitment | 5.1 | MEDIUM |
| CybersecurityRequirement | AI system security | 8.5.1 | HIGH |
| MonitoringRequirement | Monitoring and measurement | 9.1 | HIGH |
| IncidentResponseRequirement | Incident management | 10.1 | HIGH |
| AuditTrailRequirement | Logging and traceability | 8.4.2 | HIGH |
| ConformityAssessmentRequirement | Internal audit | 9.2 | HIGH |

---

## NIST AI RMF Mappings (v1.0.0)

### Coverage

**Total Mappings:** 16 mappings (4 NIST functions, 12 categories)
**Confidence Distribution:**
- HIGH: 16 mappings (100%)
- MEDIUM: 0 mappings (0%)

**NIST Functions Covered:**
- **GOVERN** (3 mappings)
  - GOVERN-1.1 - Legal and regulatory requirements
  - GOVERN-1.2 - Accountability structures
  - GOVERN-1.3 - Transparency processes
- **MAP** (4 mappings)
  - MAP-2.1 - Context of use
  - MAP-2.2 - Risk categorization
  - MAP-2.3 - Data quality and fairness
- **MEASURE** (4 mappings)
  - MEASURE-3.1 - Performance metrics
  - MEASURE-3.2 - Testing and validation
  - MEASURE-3.3 - Bias monitoring
- **MANAGE** (5 mappings)
  - MANAGE-4.1 - Human oversight
  - MANAGE-4.2 - Monitoring and incident response
  - MANAGE-4.3 - Transparency and accountability
  - MANAGE-4.4 - Security controls

**Applicability Contexts:**
- GLOBAL_INCIDENTS: 13 mappings (81%)
- US_INCIDENTS: 8 mappings (50%)
- COMPARATIVE_ANALYSIS: 7 mappings (44%)
- VOLUNTARY_COMPLIANCE: 5 mappings (31%)

### NIST Mappings Table

| EU AI Act Requirement | NIST Function | Category | Applicability | Confidence |
|----------------------|---------------|----------|---------------|------------|
| FundamentalRightsAssessmentRequirement | GOVERN | 1.1 | US/Comparative | HIGH |
| RiskAssessmentRequirement | GOVERN/MAP | 1.2/2.2 | Global | HIGH |
| DocumentationRequirement | GOVERN | 1.3 | Global/Voluntary | HIGH |
| HighRiskClassificationCriterion | MAP | 2.1 | Global/Comparative | HIGH |
| DataGovernanceRequirement | MAP | 2.3 | Global/Voluntary | HIGH |
| NonDiscriminationRequirement | MAP/MEASURE | 2.3/3.3 | Global/US | HIGH |
| AccuracyRequirement | MEASURE | 3.1 | Global/Comparative | HIGH |
| RobustnessRequirement | MEASURE | 3.1 | Global/Voluntary | HIGH |
| ConformityAssessmentRequirement | MEASURE | 3.2 | Comparative/Voluntary | HIGH |
| HumanOversightRequirement | MANAGE | 4.1 | Global/Comparative | HIGH |
| MonitoringRequirement | MANAGE | 4.2 | Global/US | HIGH |
| IncidentResponseRequirement | MANAGE | 4.2 | Global/US | HIGH |
| TransparencyRequirement | MANAGE | 4.3 | Global/Comparative | HIGH |
| AuditTrailRequirement | MANAGE | 4.3 | Global/US | HIGH |
| CybersecurityRequirement | MANAGE | 4.4 | Global/US | HIGH |
| BiometricSecurityRequirement | MANAGE | 4.4 | Global/US | HIGH |

### Key Differences: ISO 42001 vs NIST AI RMF

| Aspect | ISO 42001 | NIST AI RMF |
|--------|-----------|-------------|
| **Nature** | Mandatory certification standard | Voluntary guidance framework |
| **Scope** | AI management system (corporate) | AI risk management (system-level) |
| **Target** | Organizations seeking certification | All AI developers/deployers |
| **Enforcement** | Third-party audits, certification | Self-assessment, no enforcement |
| **Use Case** | EU corporate compliance | US/global best practices |
| **Forensic Value** | Detect certification gaps | Baseline for voluntary adoption |

---

## Usage

### For Forensic Analysis

```sparql
PREFIX ai: <http://ai-act.eu/ai#>

# Query: Find ISO controls that should have prevented an incident
SELECT ?euRequirement ?isoControl ?isoSection
WHERE {
  # EU AI Act requirement was violated
  ?euRequirement a ai:ComplianceRequirement ;
                 ai:equivalentToISOControl ?isoControl ;
                 ai:isoSection ?isoSection .

  # Get ISO control description
  ?euRequirement ai:isoControlDescription ?description .
}
```

**Example Output:**
```
If BiometricSecurityRequirement was violated:
→ ISO 42001 Control 8.5 (Information security) should have been implemented
→ Forensic conclusion: ISO certification may be invalid
```

---

### For Gap Detection

```sparql
PREFIX ai: <http://ai-act.eu/ai#>

# Query: Systems with ISO certification but missing EU AI Act requirements
SELECT ?system ?missingRequirement ?isoControl
WHERE {
  # System claims ISO 42001 certification
  ?system ai:hasCertification ai:ISO42001Certified .

  # But is missing EU AI Act requirements
  ?system ai:hasPurpose ?purpose .
  ?purpose ai:activatesCriterion ?criterion .
  ?criterion ai:activatesRequirement ?missingRequirement .

  # Requirement was NOT implemented
  MINUS {
    ?system ai:hasComplianceRequirement ?missingRequirement .
  }

  # Map to ISO control
  ?missingRequirement ai:equivalentToISOControl ?isoControl .
}
```

**Example Output:**
```
System: urn:uuid:abc-123
Missing: ai:BiometricSecurityRequirement
ISO Control: iso:Control_8_5
→ System certified ISO 42001 but failed to implement section 8.5
→ Certification gap detected
```

---

### For Multi-Framework Reports

The mappings enable forensic reports showing both EU and ISO compliance:

```
FORENSIC COMPLIANCE AUDIT REPORT

System: FacialRecognitionAirport
Incident: Data breach (50K records)

EU AI ACT VIOLATIONS:
❌ BiometricSecurityRequirement (Article 15 + Annex III)
❌ DataGovernanceRequirement (Article 10)

ISO 42001 FAILURES:
❌ Control 8.5 - Information security (should have prevented breach)
❌ Control 8.3 - Data governance (inadequate data protection)

ROOT CAUSE ANALYSIS:
The system was certified ISO 42001 in 2023 but failed to properly
implement sections 8.3 and 8.5. This resulted in:
1. Inadequate biometric template protection
2. Weak access controls
3. Missing encryption requirements

The ISO audit did not catch these gaps, suggesting either:
- Incomplete audit scope
- Insufficient auditor expertise in biometric systems
- Certification obtained before proper implementation

ENFORCEMENT RECOMMENDATION:
1. Revoke or suspend ISO 42001 certification
2. EU AI Act fine: €8-12M (Article 15 + Annex III violations)
3. Mandatory re-audit by qualified biometric security auditor
4. System deactivation until compliance verified
```

---

### For NIST AI RMF Comparative Analysis

```sparql
PREFIX ai: <http://ai-act.eu/ai#>
PREFIX nist: <http://nist.gov/ai-rmf#>

# Query: Find NIST functions that align with violated EU AI Act requirements
SELECT ?euRequirement ?nistFunction ?nistCategory ?applicability
WHERE {
  # EU AI Act requirement was violated
  ?euRequirement a ai:ComplianceRequirement ;
                 ai:equivalentToNISTFunction ?nistFunction ;
                 ai:nistCategory ?nistCategory ;
                 ai:nistApplicabilityContext ?applicability .

  # Filter for US/Global incidents
  FILTER(CONTAINS(?applicability, "US_INCIDENTS") || CONTAINS(?applicability, "GLOBAL_INCIDENTS"))
}
```

**Example Output:**
```
If BiometricSecurityRequirement was violated in US incident:
→ NIST AI RMF Function: MANAGE-4.4 (Security controls)
→ Applicability: GLOBAL_INCIDENTS, US_INCIDENTS
→ Forensic conclusion: System failed voluntary NIST guidance AND mandatory EU requirements
→ Recommendation: System should adopt NIST security controls even if not EU-deployed
```

---

### For Cross-Jurisdictional Gap Detection

```sparql
PREFIX ai: <http://ai-act.eu/ai#>

# Query: Systems claiming NIST compliance but missing EU AI Act requirements
SELECT ?system ?missingRequirement ?nistFunction ?isoControl
WHERE {
  # System claims NIST AI RMF adoption
  ?system ai:followsFramework ai:NIST_AI_RMF .

  # But is missing EU AI Act requirements
  ?system ai:hasPurpose ?purpose .
  ?purpose ai:activatesCriterion ?criterion .
  ?criterion ai:activatesRequirement ?missingRequirement .

  # Requirement was NOT implemented
  MINUS {
    ?system ai:hasComplianceRequirement ?missingRequirement .
  }

  # Map to both NIST and ISO
  ?missingRequirement ai:equivalentToNISTFunction ?nistFunction .
  OPTIONAL { ?missingRequirement ai:equivalentToISOControl ?isoControl . }
}
```

**Example Output:**
```
System: urn:uuid:us-ai-system-456
Missing: ai:HumanOversightRequirement
NIST Function: nist:MANAGE_4_1
ISO Control: iso:Control_8_6
→ System follows NIST voluntary guidance but would fail EU AI Act if deployed in EU
→ Gap: No human oversight implementation despite NIST MANAGE-4.1 recommendation
```

---

### For Historical Incident Analysis (Pre-EU AI Act)

The NIST mappings enable retrospective analysis of incidents that occurred before the EU AI Act enforcement:

```
FORENSIC ANALYSIS: 2023 Facial Recognition Incident (Pre-EU AI Act)

Incident Date: 2023-08-15 (Before EU AI Act enforcement)
System: Airport Security Facial Recognition
Jurisdiction: Both US and EU deployments

RETROSPECTIVE EU AI ACT ANALYSIS:
❌ BiometricSecurityRequirement (Article 15 + Annex III) - NOT implemented
❌ DataGovernanceRequirement (Article 10) - Inadequate
❌ HumanOversightRequirement (Article 14) - Missing

NIST AI RMF ANALYSIS (Voluntary guidance available in 2023):
❌ MANAGE-4.4 (Security controls) - System ignored available guidance
❌ MAP-2.3 (Data quality and fairness) - Inadequate dataset documentation
❌ MANAGE-4.1 (Human oversight) - No oversight mechanisms

ISO 42001 ANALYSIS:
⚠️  Standard published October 2023 - May not have been adopted yet

FORENSIC CONCLUSIONS:
1. System would have violated EU AI Act if it were in force (now subject to penalties)
2. System ignored voluntary NIST guidance that was available
3. Failure was preventable using industry best practices (NIST) available at the time
4. Demonstrates negligence: voluntary frameworks existed but were not followed

ENFORCEMENT IMPLICATIONS:
- If system still operates: Immediate EU AI Act compliance required
- If deployed in US: Should adopt NIST AI RMF retroactively
- If ISO 42001 certified after incident: Certification may be invalid
```

---

## Properties Defined

The mappings introduce 9 new properties across both frameworks:

### ISO 42001 Properties

#### ai:equivalentToISOControl
- **Type:** owl:ObjectProperty
- **Domain:** ai:ComplianceRequirement
- **Range:** iso:Control
- **Purpose:** Links EU AI Act requirement to equivalent ISO control

#### ai:isoSection
- **Type:** owl:DatatypeProperty
- **Domain:** ai:ComplianceRequirement
- **Range:** xsd:string
- **Purpose:** ISO section number (e.g., "8.3.2")

#### ai:isoControlDescription
- **Type:** owl:DatatypeProperty
- **Purpose:** Human-readable description of ISO control

#### ai:mappingConfidence
- **Type:** owl:DatatypeProperty
- **Range:** "HIGH" | "MEDIUM" | "LOW"
- **Purpose:** Confidence level of the ISO mapping

### NIST AI RMF Properties

#### ai:equivalentToNISTFunction
- **Type:** owl:ObjectProperty
- **Domain:** ai:ComplianceRequirement
- **Range:** nist:Function
- **Purpose:** Links EU AI Act requirement to equivalent NIST AI RMF function

#### ai:nistCategory
- **Type:** owl:DatatypeProperty
- **Domain:** ai:ComplianceRequirement
- **Range:** xsd:string
- **Purpose:** NIST AI RMF category identifier (e.g., "GOVERN-1.1", "MAP-2.3")

#### ai:nistCategoryDescription
- **Type:** owl:DatatypeProperty
- **Purpose:** Human-readable description of NIST category

#### ai:nistMappingConfidence
- **Type:** owl:DatatypeProperty
- **Range:** "HIGH" | "MEDIUM" | "LOW"
- **Purpose:** Confidence level of the NIST mapping

#### ai:nistApplicabilityContext
- **Type:** owl:DatatypeProperty
- **Range:** "US_INCIDENTS" | "GLOBAL_INCIDENTS" | "COMPARATIVE_ANALYSIS" | "VOLUNTARY_COMPLIANCE"
- **Purpose:** Context where NIST mapping is most relevant

---

## Loading Mappings

### Automatic Loading (Docker)

Mappings are automatically mounted in containers via `docker-compose.yml`:

```yaml
backend:
  volumes:
    - ./ontologias/mappings:/ontologias/mappings:ro

reasoner:
  volumes:
    - ./ontologias/mappings:/ontologias/mappings:ro
```

### Manual Loading (Python)

```python
from rdflib import Graph

# Load ontology + all mappings
g = Graph()
g.parse("ontologias/versions/0.41.0/ontologia-v0.41.0.ttl", format="turtle")
g.parse("ontologias/mappings/iso-42001-mappings.ttl", format="turtle")
g.parse("ontologias/mappings/nist-ai-rmf-mappings.ttl", format="turtle")

# Query ISO mappings
iso_query = """
PREFIX ai: <http://ai-act.eu/ai#>
SELECT ?req ?iso WHERE {
  ?req ai:equivalentToISOControl ?iso .
}
"""
iso_results = g.query(iso_query)

# Query NIST mappings
nist_query = """
PREFIX ai: <http://ai-act.eu/ai#>
SELECT ?req ?nist ?category ?context WHERE {
  ?req ai:equivalentToNISTFunction ?nist ;
       ai:nistCategory ?category ;
       ai:nistApplicabilityContext ?context .
}
"""
nist_results = g.query(nist_query)
```

---

## Integration Points

### Forensic Analysis Agent (Phase 2 & 3)

The forensic agent will use these mappings to:

**ISO 42001 Integration (Phase 2):**
1. **Identify failed ISO controls** during incident analysis
2. **Generate multi-framework reports** (EU + ISO)
3. **Detect certification gaps** (ISO certified but EU non-compliant)
4. **Provide evidence trails** for enforcement actions

**NIST AI RMF Integration (Phase 3):**
1. **Analyze US/global incidents** using NIST voluntary framework
2. **Retrospective analysis** of pre-EU AI Act incidents
3. **Comparative compliance** (mandatory EU vs voluntary US)
4. **Cross-jurisdictional reports** for multinational deployments
5. **Detect negligence** (voluntary guidance ignored)

### Backend API (Future)

Planned endpoints:
```
# ISO 42001 Endpoints
GET /mappings/iso-42001                      # List all ISO mappings
GET /mappings/iso-42001/{requirement}        # Get ISO control for EU requirement
GET /systems/{id}/iso-compliance             # Compare EU vs ISO compliance
POST /forensic/analyze-with-iso              # Forensic analysis using ISO mappings

# NIST AI RMF Endpoints
GET /mappings/nist-ai-rmf                    # List all NIST mappings
GET /mappings/nist-ai-rmf/{requirement}      # Get NIST function for EU requirement
GET /systems/{id}/nist-compliance            # Compare EU vs NIST compliance
POST /forensic/analyze-with-nist             # Forensic analysis using NIST mappings

# Multi-Framework Endpoints
GET /mappings/frameworks                     # List all supported frameworks
GET /systems/{id}/multi-framework-report     # Generate report across EU/ISO/NIST
POST /forensic/analyze-cross-jurisdictional  # US+EU incident analysis
```

---

## Maintenance

### Adding New ISO 42001 Mappings

1. Edit `iso-42001-mappings.ttl`
2. Add mapping following existing pattern:

```turtle
ai:NewRequirement
    ai:equivalentToISOControl iso:Control_X_Y ;
    ai:isoSection "X.Y" ;
    ai:isoControlDescription "Description here" ;
    ai:mappingConfidence "HIGH" ;
    rdfs:comment "Explanation in English"@en,
        "Explicación en español"@es .
```

3. Update statistics at end of file
4. Restart containers to reload

### Adding New NIST AI RMF Mappings

1. Edit `nist-ai-rmf-mappings.ttl`
2. Add mapping following existing pattern:

```turtle
ai:NewRequirement
    ai:equivalentToNISTFunction nist:FUNCTION_X_Y ;
    ai:nistCategory "FUNCTION-X.Y" ;
    ai:nistCategoryDescription "Description here" ;
    ai:nistMappingConfidence "HIGH" ;
    ai:nistApplicabilityContext "GLOBAL_INCIDENTS, US_INCIDENTS" ;
    rdfs:comment "Explanation in English"@en,
        "Explicación en español"@es .
```

3. Update statistics at end of file
4. Restart containers to reload

### Validation

```bash
# Validate Turtle syntax
rapper -i turtle -o ntriples iso-42001-mappings.ttl > /dev/null
rapper -i turtle -o ntriples nist-ai-rmf-mappings.ttl > /dev/null

# Check for completeness
grep -c "ai:equivalentToISOControl" iso-42001-mappings.ttl
# Should output: 15

grep -c "ai:equivalentToNISTFunction" nist-ai-rmf-mappings.ttl
# Should output: 16
```

---

## References

- **EU AI Act:** [EUR-Lex Official Text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206)
- **ISO/IEC 42001:2023:** [ISO Official Page](https://www.iso.org/standard/81230.html)
- **NIST AI RMF 1.0:** [NIST Official Publication](https://www.nist.gov/itl/ai-risk-management-framework)
- **Mapping Methodology:** Based on comparative analysis of legal texts, technical requirements, and framework objectives

---

## Version History

| Version | Date | Framework | Changes |
|---------|------|-----------|---------|
| 1.0.0 | 2025-12-05 | ISO 42001 | Initial 15 core ISO mappings for Phase 2 |
| 1.0.0 | 2025-12-05 | NIST AI RMF | Initial 16 NIST mappings for Phase 3 |

---

## Statistics Summary

| Framework | Mappings | Confidence | Status |
|-----------|----------|------------|--------|
| **ISO 42001** | 15 | 87% HIGH, 13% MEDIUM | ✅ Active |
| **NIST AI RMF** | 16 | 100% HIGH | ✅ Active |
| **Total** | **31** | **94% HIGH, 6% MEDIUM** | **Phase 2 & 3 Complete** |

---

## License

Mappings are provided under Creative Commons Attribution 4.0 International (CC BY 4.0), consistent with the EU AI Act ontology license.

---

**Last Updated:** 2025-12-05
**Status:** Active (Phase 2 & 3 Complete)
**Next Phase:** Forensic Analysis Agent Implementation
