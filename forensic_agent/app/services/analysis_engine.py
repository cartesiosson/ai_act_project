"""Multi-framework forensic analysis engine"""

from typing import Dict, Optional, List
from datetime import datetime

from ..models.incident import ExtractedIncident
from ..models.forensic_report import (
    EUAIActAnalysis,
    EUAIActRequirement,
    ISO42001Analysis,
    ISOMapping,
    NISTAIRMFAnalysis,
    NISTMapping,
    ComplianceGaps,
    CriticalGap,
    ForensicAnalysisResult
)
from .incident_extractor import IncidentExtractorService
from .sparql_queries import ForensicSPARQLService


class ForensicAnalysisEngine:
    """
    Orchestrates multi-framework forensic analysis of AI incidents
    """

    def __init__(self,
                 extractor: IncidentExtractorService,
                 sparql: ForensicSPARQLService):
        """
        Initialize with extractor and SPARQL services

        Args:
            extractor: Incident extraction service
            sparql: SPARQL query service
        """
        self.extractor = extractor
        self.sparql = sparql

    async def analyze_incident(self, narrative: str) -> Dict:
        """
        Complete multi-framework forensic analysis

        Args:
            narrative: Raw incident narrative text

        Returns:
            Comprehensive forensic analysis report
        """

        print("=" * 80)
        print("FORENSIC COMPLIANCE ANALYSIS")
        print("=" * 80)

        # Step 1: Extract incident properties
        print("\n[1/6] Extracting incident properties from narrative...")
        try:
            incident = await self.extractor.extract_incident(narrative)
        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            return {
                "status": "ERROR",
                "message": f"Extraction failed: {str(e)}",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

        # Check confidence threshold
        if incident.confidence.overall < 0.6:
            print(f"⚠ Low confidence: {incident.confidence.overall:.2%}")
            return {
                "status": "LOW_CONFIDENCE",
                "message": "Insufficient detail in narrative for reliable analysis",
                "confidence": incident.confidence.overall,
                "extraction": incident.dict(),
                "requires_human_review": True,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

        print(f"   ✓ Extraction confidence: {incident.confidence.overall:.1%}")
        print(f"   ✓ System: {incident.system.system_name}")
        print(f"   ✓ Organization: {incident.system.organization}")
        print(f"   ✓ Incident type: {incident.incident.incident_type}")
        print(f"   ✓ Jurisdiction: {incident.system.jurisdiction}")
        print(f"   ✓ Discovery date: {incident.timeline.discovery_date}")

        # Step 2: Query EU AI Act mandatory requirements
        print("\n[2/6] Querying EU AI Act ontology for mandatory requirements...")
        try:
            eu_requirements = await self.sparql.query_mandatory_requirements(
                purpose=incident.system.primary_purpose,
                contexts=incident.system.deployment_context,
                data_types=incident.system.processes_data_types
            )

            print(f"   ✓ Risk level: {eu_requirements['risk_level']}")
            print(f"   ✓ Criteria activated: {len(eu_requirements['criteria'])}")
            print(f"   ✓ Mandatory requirements: {eu_requirements['total_requirements']}")

        except Exception as e:
            print(f"   ✗ EU AI Act query failed: {e}")
            eu_requirements = {
                "criteria": [],
                "requirements": [],
                "risk_level": "Unknown",
                "total_requirements": 0
            }

        # Step 3: Query ISO 42001 mappings
        print("\n[3/6] Querying ISO 42001 mappings...")
        try:
            eu_req_uris = [req["uri"] for req in eu_requirements["requirements"]]
            iso_mappings = await self.sparql.query_iso_42001_mappings(eu_req_uris)

            print(f"   ✓ ISO 42001 controls mapped: {len(iso_mappings)}")

        except Exception as e:
            print(f"   ✗ ISO mapping query failed: {e}")
            iso_mappings = {}

        # Step 4: Query NIST AI RMF mappings (if applicable)
        print("\n[4/6] Querying NIST AI RMF mappings...")
        try:
            jurisdiction = incident.system.jurisdiction.upper()
            # Map jurisdiction to NIST applicability
            if jurisdiction == "US":
                nist_jurisdiction = "US"
            elif jurisdiction in ["GLOBAL", "EU"]:
                nist_jurisdiction = "GLOBAL"
            else:
                nist_jurisdiction = "GLOBAL"  # Default to global

            nist_mappings = await self.sparql.query_nist_ai_rmf_mappings(
                eu_req_uris,
                jurisdiction=nist_jurisdiction
            )

            print(f"   ✓ NIST AI RMF functions mapped: {len(nist_mappings)}")
            print(f"   ✓ Jurisdiction context: {nist_jurisdiction}")

        except Exception as e:
            print(f"   ✗ NIST mapping query failed: {e}")
            nist_mappings = {}

        # Step 5: Analyze compliance gaps
        print("\n[5/7] Analyzing compliance gaps...")
        try:
            gaps = await self.sparql.analyze_compliance_gaps(
                mandatory_requirements=eu_req_uris,
                incident_properties=incident.dict()
            )

            print(f"   ✓ Compliance ratio: {gaps['compliance_ratio']:.1%}")
            print(f"   ✓ Missing requirements: {gaps['missing']}/{gaps['total_required']}")
            print(f"   ✓ Gap severity: {gaps['severity']}")
            print(f"   ✓ Critical gaps: {len(gaps['critical_gaps'])}")

        except Exception as e:
            print(f"   ✗ Gap analysis failed: {e}")
            gaps = {
                "total_required": len(eu_req_uris),
                "implemented": 0,
                "missing": len(eu_req_uris),
                "compliance_ratio": 0.0,
                "missing_requirements": eu_req_uris,
                "critical_gaps": [],
                "severity": "UNKNOWN"
            }

        # Step 6: Query applicable inference rules
        print("\n[6/7] Querying applicable inference rules...")
        try:
            inference_rules = await self.sparql.get_applicable_rules(incident.dict())

            print(f"   ✓ Applicable rules: {inference_rules.get('total_applicable', 0)}")
            print(f"   ✓ Navigation rules: {inference_rules.get('total_navigation', 0)}")

        except Exception as e:
            print(f"   ✗ Inference rules query failed: {e}")
            inference_rules = {
                "applicable_rules": [],
                "navigation_rules": [],
                "total_applicable": 0,
                "total_navigation": 0,
                "explanation": f"Rules not available: {e}"
            }

        # Step 7: Generate multi-framework report
        print("\n[7/7] Generating multi-framework forensic report...")
        try:
            report = self._generate_report(
                incident=incident,
                eu_requirements=eu_requirements,
                iso_mappings=iso_mappings,
                nist_mappings=nist_mappings,
                gaps=gaps,
                inference_rules=inference_rules
            )

            print(f"   ✓ Report generated ({len(report)} characters)")

        except Exception as e:
            print(f"   ✗ Report generation failed: {e}")
            report = f"ERROR: Report generation failed - {str(e)}"

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

        # Build structured result
        result = self._build_structured_result(
            incident=incident,
            eu_requirements=eu_requirements,
            iso_mappings=iso_mappings,
            nist_mappings=nist_mappings,
            gaps=gaps,
            report=report
        )

        return result

    def _build_structured_result(self,
                                 incident: ExtractedIncident,
                                 eu_requirements: Dict,
                                 iso_mappings: Dict,
                                 nist_mappings: Dict,
                                 gaps: Dict,
                                 report: str) -> Dict:
        """Build structured analysis result"""

        # Convert EU requirements
        eu_reqs = [
            EUAIActRequirement(
                uri=req["uri"],
                label=req["label"],
                criterion=req["criterion"]
            )
            for req in eu_requirements["requirements"]
        ]

        eu_analysis = EUAIActAnalysis(
            risk_level=eu_requirements["risk_level"],
            criteria=eu_requirements["criteria"],
            requirements=eu_reqs,
            total_requirements=eu_requirements["total_requirements"]
        )

        # Convert ISO mappings
        iso_maps = {
            uri: ISOMapping(**mapping)
            for uri, mapping in iso_mappings.items()
        }

        iso_analysis = ISO42001Analysis(
            mappings=iso_maps,
            total_mapped=len(iso_mappings),
            certification_gap_detected=(len(iso_mappings) > 0 and gaps["missing"] > 0)
        )

        # Convert NIST mappings
        nist_maps = {
            uri: NISTMapping(**mapping)
            for uri, mapping in nist_mappings.items()
        }

        nist_analysis = NISTAIRMFAnalysis(
            mappings=nist_maps,
            total_mapped=len(nist_mappings),
            jurisdiction_applicable=(incident.system.jurisdiction in ["US", "Global"]),
            voluntary_guidance_ignored=(len(nist_mappings) > 0 and gaps["missing"] > 0)
        )

        # Convert gaps
        critical_gaps_list = [
            CriticalGap(**gap)
            for gap in gaps["critical_gaps"]
        ]

        compliance_gaps = ComplianceGaps(
            total_required=gaps["total_required"],
            implemented=gaps["implemented"],
            missing=gaps["missing"],
            compliance_ratio=gaps["compliance_ratio"],
            missing_requirements=gaps["missing_requirements"],
            critical_gaps=critical_gaps_list,
            severity=gaps["severity"]
        )

        # Build final result
        result = ForensicAnalysisResult(
            status="COMPLETED",
            analysis_timestamp=datetime.utcnow().isoformat(),
            extraction=incident.dict(),
            eu_ai_act=eu_analysis,
            iso_42001=iso_analysis,
            nist_ai_rmf=nist_analysis,
            compliance_gaps=compliance_gaps,
            report=report,
            requires_expert_review=True  # Always require expert review
        )

        return result.dict()

    def _generate_report(self,
                        incident: ExtractedIncident,
                        eu_requirements: Dict,
                        iso_mappings: Dict,
                        nist_mappings: Dict,
                        gaps: Dict,
                        inference_rules: Dict = None) -> str:
        """
        Generate human-readable multi-framework forensic report
        """
        inference_rules = inference_rules or {}

        # Temporal applicability check
        is_pre_regulation = incident.timeline.discovery_date < "2024"
        temporal_status = "PRE-REGULATION" if is_pre_regulation else "POST-REGULATION"

        report = f"""![UNIR Logo](/logo-unir.png) ![SERAMIS Logo](/seramis-logo.svg)

# FORENSIC COMPLIANCE AUDIT REPORT

**SEMANTIC REGULATION INTELLIGENCE SYSTEM (SERAMIS)** | *Master's Thesis Project - UNIR*

**Report ID:** FCA-{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}
**Analysis Date:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
**Status:** PRELIMINARY - REQUIRES EXPERT REVIEW

---

## 1. EXECUTIVE SUMMARY

**System:** {incident.system.system_name}
**Organization:** {incident.system.organization}
**Incident Type:** {incident.incident.incident_type.upper()}
**Incident Date:** {incident.timeline.discovery_date}
**Jurisdiction:** {incident.system.jurisdiction}
**Temporal Status:** {temporal_status}

**Severity Assessment:** {gaps["severity"]}
**Compliance Ratio:** {gaps["compliance_ratio"]:.1%} ({gaps["implemented"]}/{gaps["total_required"]} requirements)
**Extraction Confidence:** {incident.confidence.overall:.1%}

---

## 2. SYSTEM CLASSIFICATION

### 2.1 System Properties
- **Type:** {incident.system.system_type}
- **Purpose:** {incident.system.primary_purpose}
- **Processes Data:** {", ".join(incident.system.processes_data_types) if incident.system.processes_data_types else "Not specified"}
- **Deployment Context:** {", ".join(incident.system.deployment_context) if incident.system.deployment_context else "Not specified"}
- **Automated Decision:** {"Yes" if incident.system.is_automated_decision else "No"}
- **Human Oversight:** {incident.system.has_human_oversight if incident.system.has_human_oversight is not None else "Unknown"}
- **Model Scale:** {incident.system.model_scale}

### 2.2 EU AI Act Risk Classification
**Proper Risk Level:** {eu_requirements["risk_level"]}

**Basis:**
- Activated Criteria: {len(eu_requirements["criteria"])}
- Mandatory Requirements: {eu_requirements["total_requirements"]}

---

## 3. EU AI ACT COMPLIANCE ANALYSIS

### 3.1 Mandatory Requirements
Total Requirements: {eu_requirements["total_requirements"]}

{self._format_requirements_list(eu_requirements["requirements"])}

### 3.2 Compliance Gaps
**Missing:** {gaps["missing"]} requirements (**{gaps["severity"]}** severity)
**Compliance Ratio:** {gaps["compliance_ratio"]:.1%}

{self._format_critical_gaps(gaps["critical_gaps"])}

---

## 4. ISO 42001 CROSS-FRAMEWORK ANALYSIS

### 4.1 Certification Status
**Note:** ISO 42001 certification status unknown from incident narrative.

### 4.2 Failed ISO Controls
{len(iso_mappings)} ISO 42001 controls map to the missing requirements:

{self._format_iso_mappings(iso_mappings)}

**Forensic Conclusion:**
{"If the organization holds ISO 42001 certification, this incident suggests inadequate implementation of certified controls. Recommend reviewing certification validity." if len(iso_mappings) > 0 and gaps["missing"] > 0 else "No ISO 42001 mapping issues detected."}

---

## 5. NIST AI RMF VOLUNTARY GUIDANCE ANALYSIS

### 5.1 Applicability
**Jurisdiction:** {incident.system.jurisdiction}
**NIST AI RMF Published:** January 2023
**Incident Date:** {incident.timeline.discovery_date}
**Guidance Available:** {"No - Incident predates NIST AI RMF" if incident.timeline.discovery_date < "2023" else "Yes - NIST AI RMF was available"}

### 5.2 NIST Functions Analysis
{len(nist_mappings)} NIST AI RMF functions map to the requirements:

{self._format_nist_mappings(nist_mappings)}

**Forensic Conclusion:**
{self._generate_nist_conclusion(incident, nist_mappings, gaps)}

---

## 6. INFERENCE RULES ANALYSIS

This section explains the reasoning rules that were applied to determine the system's
risk classification, compliance requirements, and regulatory obligations.

### 6.1 Applicable Condition-Based Rules
{self._format_inference_rules(inference_rules)}

### 6.2 Transitive Navigation Rules
{self._format_navigation_rules(inference_rules)}

### 6.3 Reasoning Chain Explanation
{inference_rules.get('explanation', 'No explanation available')}

---

## 7. ROOT CAUSE ANALYSIS

### 7.1 Primary Failure Points
{self._infer_root_causes(incident, gaps)}

### 7.2 Incident Impact
- **Affected Populations:** {", ".join(incident.incident.affected_populations) if incident.incident.affected_populations else "Not specified"}
- **Affected Count:** {incident.incident.affected_count if incident.incident.affected_count else "Unknown"}
- **Public Disclosure:** {"Yes" if incident.incident.public_disclosure else "No"}
- **Severity:** {incident.incident.severity}

---

## 8. ENFORCEMENT RECOMMENDATION

### 8.1 Temporal Applicability
**Incident Date:** {incident.timeline.discovery_date}
**EU AI Act Enforcement:** August 2, 2024

{self._generate_temporal_analysis(incident)}

### 8.2 Violation Assessment
{self._assess_violations(incident, gaps)}

### 8.3 Recommended Actions
{self._generate_recommendations(incident, gaps)}

---

## 9. ORGANIZATION RESPONSE EVALUATION

### 9.1 Actions Taken
{self._format_organization_response(incident.response)}

### 9.2 Adequacy Assessment
{self._assess_response_adequacy(incident.response, gaps)}

---

## 10. EXPERT REVIEW REQUIREMENTS

**This report requires expert validation for:**
- [ ] Verify extraction accuracy from narrative
- [ ] Assess temporal applicability of EU AI Act
- [ ] Evaluate compliance gap severity
- [ ] Determine appropriate enforcement action
- [ ] Validate multi-framework analysis (ISO/NIST)
- [ ] Calculate fine amount (if applicable)
- [ ] Identify additional systemic risks

---

**Report Generated:** {datetime.utcnow().isoformat()}
**Generated By:** Forensic AI Agent v1.0 | **System:** Semantic Regulation Intelligence System (SERAMIS)
**Extraction Confidence:** {incident.confidence.overall:.1%}
**Status:** PRELIMINARY - NOT FOR ENFORCEMENT USE WITHOUT EXPERT REVIEW

---

*Authors: David Fernández González and Mariano Ortega de Mues* | *Directors: Xiomara Patricia Blanco Valencia and Sergio Castillo* | *Universidad Internacional de La Rioja (UNIR)*
"""

        return report

    def _format_requirements_list(self, requirements: List[Dict]) -> str:
        """Format requirements list for report"""
        if not requirements:
            return "*No requirements identified*"

        lines = []
        for i, req in enumerate(requirements[:10], 1):  # Limit to first 10
            lines.append(f"{i}. **{req['label']}**")
        if len(requirements) > 10:
            lines.append(f"... and {len(requirements) - 10} more")
        return "\n".join(lines)

    def _format_critical_gaps(self, critical_gaps: List[Dict]) -> str:
        """Format critical gaps for report"""
        if not critical_gaps:
            return "*No critical gaps identified*"

        lines = ["**Critical Missing Requirements:**"]
        for gap in critical_gaps[:5]:  # Limit to first 5
            req_name = gap['requirement'].split("#")[-1]
            lines.append(f"- **{req_name}** - {gap['reason']}")
        if len(critical_gaps) > 5:
            lines.append(f"... and {len(critical_gaps) - 5} more critical gaps")
        return "\n".join(lines)

    def _format_iso_mappings(self, iso_mappings: Dict) -> str:
        """Format ISO 42001 mappings for report"""
        if not iso_mappings:
            return "*No ISO 42001 mappings available*"

        lines = []
        for req_uri, mapping in list(iso_mappings.items())[:5]:  # Limit to first 5
            req_name = req_uri.split("#")[-1]
            lines.append(f"**{req_name}** → ISO {mapping['iso_section']}")
            lines.append(f"  - {mapping['description']}")
            lines.append("")
        if len(iso_mappings) > 5:
            lines.append(f"... and {len(iso_mappings) - 5} more mappings")
        return "\n".join(lines)

    def _format_nist_mappings(self, nist_mappings: Dict) -> str:
        """Format NIST AI RMF mappings for report"""
        if not nist_mappings:
            return "*No NIST AI RMF mappings available*"

        lines = []
        for req_uri, mapping in list(nist_mappings.items())[:5]:  # Limit to first 5
            req_name = req_uri.split("#")[-1]
            lines.append(f"**{req_name}** → NIST {mapping['nist_category']}")
            lines.append(f"  - {mapping['description']}")
            lines.append("")
        if len(nist_mappings) > 5:
            lines.append(f"... and {len(nist_mappings) - 5} more mappings")
        return "\n".join(lines)

    def _generate_nist_conclusion(self, incident: ExtractedIncident,
                                  nist_mappings: Dict, gaps: Dict) -> str:
        """Generate NIST-specific forensic conclusion"""
        if incident.timeline.discovery_date < "2023":
            return "**Incident occurred BEFORE NIST AI RMF publication (January 2023).** Voluntary guidance was not available at the time."

        if len(nist_mappings) > 0 and gaps["missing"] > 0:
            return f"""**VOLUNTARY GUIDANCE IGNORED:** NIST AI RMF was publicly available but appears to have been ignored. This demonstrates negligence - the organization had access to best practices but failed to implement them.

**Implication:** Strengthens case for enforcement action. The failure was preventable using voluntary industry guidance."""

        return "System appears to have followed available NIST guidance."

    def _infer_root_causes(self, incident: ExtractedIncident, gaps: Dict) -> str:
        """Infer root causes from incident and gaps"""
        causes = []

        # Primary cause from incident type
        causes.append(f"1. **Primary:** {incident.incident.incident_type.capitalize()} incident due to inadequate compliance measures")

        # Secondary from critical gaps
        if gaps["critical_gaps"]:
            critical = gaps["critical_gaps"][0]
            req_name = critical['requirement'].split("#")[-1]
            causes.append(f"2. **Secondary:** Missing {req_name}")

        # Tertiary from system properties
        if not incident.system.has_human_oversight:
            causes.append("3. **Tertiary:** Lack of human oversight mechanisms")

        return "\n".join(causes)

    def _generate_temporal_analysis(self, incident: ExtractedIncident) -> str:
        """Generate temporal applicability analysis"""
        if incident.timeline.discovery_date < "2024":
            return """⚠️ **PRE-REGULATION INCIDENT**

The EU AI Act was not in force at the time of this incident (enforcement began August 2, 2024).

**Status:** Not subject to EU AI Act penalties (retroactive application prohibited).

**Note:** This analysis demonstrates what WOULD constitute a violation if the incident occurred post-August 2024. Use as case study for similar systems currently deployed."""

        return """✅ **POST-REGULATION INCIDENT**

The EU AI Act is in force. This system is subject to EU AI Act requirements.

**Status:** Subject to enforcement action if violations are confirmed."""

    def _assess_violations(self, incident: ExtractedIncident, gaps: Dict) -> str:
        """Assess violations and penalties"""
        if incident.timeline.discovery_date < "2024":
            return "**Not applicable** - Incident predates EU AI Act enforcement."

        severity = gaps["severity"]
        if severity in ["CRITICAL", "HIGH"]:
            return f"""**VIOLATION LIKELY CONFIRMED**

**Severity:** {severity}
**Missing Requirements:** {gaps["missing"]} of {gaps["total_required"]}

**Enforcement Recommendation:** Proceed with formal investigation and potential penalties."""

        return f"""**Assessment:** {severity} severity

Further investigation recommended to determine enforcement action."""

    def _generate_recommendations(self, incident: ExtractedIncident, gaps: Dict) -> str:
        """Generate recommendations"""
        recs = ["1. **Immediate:** Comprehensive compliance audit"]

        if gaps["missing"] > 0:
            recs.append(f"2. **Short-term:** Implement {gaps['missing']} missing requirements")

        if gaps["critical_gaps"]:
            recs.append(f"3. **Priority:** Address {len(gaps['critical_gaps'])} critical gaps first")

        recs.append("4. **Long-term:** Establish ongoing compliance monitoring")

        return "\n".join(recs)

    def _format_organization_response(self, response: "OrganizationResponse") -> str:
        """Format organization response"""
        lines = [
            f"- **Acknowledged:** {'Yes' if response.acknowledged else 'No'}",
            f"- **Public Apology:** {'Yes' if response.public_apology else 'No'}",
            f"- **Compensation:** {'Yes' if response.compensation_provided else 'No'}"
        ]

        if response.actions_taken:
            lines.append(f"- **Actions Taken:** {len(response.actions_taken)} actions")
            for action in response.actions_taken[:3]:
                lines.append(f"  - {action}")
            if len(response.actions_taken) > 3:
                lines.append(f"  - ... and {len(response.actions_taken) - 3} more")

        return "\n".join(lines)

    def _assess_response_adequacy(self, response: "OrganizationResponse",
                                  gaps: Dict) -> str:
        """Assess adequacy of organization response"""
        if len(response.actions_taken) == 0:
            return "**Inadequate:** No documented actions taken."

        if gaps["severity"] in ["CRITICAL", "HIGH"] and len(response.actions_taken) < 3:
            return f"**Inadequate:** Only {len(response.actions_taken)} action(s) taken for {gaps['severity']} severity incident."

        if response.systemic_improvements:
            return f"**Adequate:** {len(response.actions_taken)} actions taken including systemic improvements."

        return f"**Partial:** {len(response.actions_taken)} actions taken but systemic improvements not clearly documented."

    def _format_inference_rules(self, inference_rules: Dict) -> str:
        """Format applicable inference rules for the report"""
        applicable = inference_rules.get("applicable_rules", [])

        if not applicable:
            return "*No specific condition-based rules were identified as applicable to this incident.*"

        lines = [f"**{len(applicable)} rules applied:**\n"]

        for rule in applicable[:8]:  # Limit to first 8
            lines.append(f"**{rule['rule_name']}** ({rule['category']})")
            lines.append(f"- Trigger: {rule['reason']}")

            # Show conditions
            conditions = rule.get('conditions', [])
            if conditions:
                cond_str = ", ".join([
                    f"{c['property'].replace('ai:', '')} {c['operator']} {c['value']}"
                    for c in conditions[:2]
                ])
                lines.append(f"- Conditions: {cond_str}")

            # Show consequences
            consequences = rule.get('consequences', [])
            if consequences:
                cons_str = ", ".join([
                    f"{c['property'].replace('ai:', '')} = {c['value'].replace('ai:', '')}"
                    for c in consequences[:2]
                ])
                lines.append(f"- Effect: {cons_str}")

            lines.append("")

        if len(applicable) > 8:
            lines.append(f"... and {len(applicable) - 8} more rules")

        return "\n".join(lines)

    def _format_navigation_rules(self, inference_rules: Dict) -> str:
        """Format navigation rules for the report"""
        nav_rules = inference_rules.get("navigation_rules", [])

        if not nav_rules:
            return "*No navigation rules available.*"

        lines = [f"**{len(nav_rules)} transitive inference rules active:**\n"]

        for rule in nav_rules:
            nav_type = rule.get("navigation_type", "transitive")
            source = rule.get("source_property", "").replace("ai:", "")
            link = rule.get("link_property", "").replace("ai:", "")
            target = rule.get("target_property", "").replace("ai:", "")

            if nav_type == "transitive":
                lines.append(f"- **{rule['name']}**")
                lines.append(f"  Chain: {source} → {link} → {target}")
            else:
                lines.append(f"- **{rule['name']}**")
                lines.append(f"  Direct: {source} → {target}")

        lines.append("")
        lines.append("*These rules enable transitive reasoning: if a system has a purpose that activates a criterion, and that criterion activates requirements, the system inherits those requirements.*")

        return "\n".join(lines)
