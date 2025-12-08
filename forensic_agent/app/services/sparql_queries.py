"""SPARQL query service for forensic compliance analysis - MCP Client version"""

import os
from typing import Dict, List, Optional
from .mcp_client import MCPClient

AI_PREFIX = "http://ai-act.eu/ai#"

# Valid ontology Purpose IRIs - exact match takes precedence
VALID_PURPOSE_IRIS = {
    "BiometricIdentification",
    "LawEnforcementSupport",
    "MigrationControl",
    "EducationAccess",
    "RecruitmentOrEmployment",
    "WorkforceEvaluationPurpose",
    "CriticalInfrastructureOperation",
    "HealthCare",
    "JudicialDecisionSupport",
    "PublicServiceAllocation"
}

# Mapping from extracted purposes to ontology IRIs
# Keys are lowercase patterns, values are ontology IRI names
PURPOSE_MAPPING = {
    # Biometric identification
    "biometric": "BiometricIdentification",
    "facial recognition": "BiometricIdentification",
    "face recognition": "BiometricIdentification",
    "fingerprint": "BiometricIdentification",
    "iris scan": "BiometricIdentification",
    "voice recognition": "BiometricIdentification",
    "identity verification": "BiometricIdentification",
    # Law enforcement
    "law enforcement": "LawEnforcementSupport",
    "police": "LawEnforcementSupport",
    "criminal": "LawEnforcementSupport",
    "security surveillance": "LawEnforcementSupport",
    "predictive policing": "LawEnforcementSupport",
    # Migration and border
    "migration": "MigrationControl",
    "border": "MigrationControl",
    "asylum": "MigrationControl",
    "immigration": "MigrationControl",
    # Education
    "education": "EducationAccess",
    "student": "EducationAccess",
    "academic": "EducationAccess",
    "school": "EducationAccess",
    "university": "EducationAccess",
    "exam": "EducationAccess",
    "grading": "EducationAccess",
    # Employment and recruitment
    "recruitment": "RecruitmentOrEmployment",
    "employment": "RecruitmentOrEmployment",
    "hiring": "RecruitmentOrEmployment",
    "hr": "RecruitmentOrEmployment",
    "job": "RecruitmentOrEmployment",
    "resume": "RecruitmentOrEmployment",
    "cv screening": "RecruitmentOrEmployment",
    # Workforce evaluation
    "worker evaluation": "WorkforceEvaluationPurpose",
    "employee monitoring": "WorkforceEvaluationPurpose",
    "performance evaluation": "WorkforceEvaluationPurpose",
    "productivity": "WorkforceEvaluationPurpose",
    # Critical infrastructure
    "critical infrastructure": "CriticalInfrastructureOperation",
    "energy": "CriticalInfrastructureOperation",
    "power grid": "CriticalInfrastructureOperation",
    "water supply": "CriticalInfrastructureOperation",
    "transport": "CriticalInfrastructureOperation",
    "autonomous driving": "CriticalInfrastructureOperation",
    "self-driving": "CriticalInfrastructureOperation",
    "autonomous vehicle": "CriticalInfrastructureOperation",
    # Healthcare
    "healthcare": "HealthCare",
    "health care": "HealthCare",
    "medical": "HealthCare",
    "diagnosis": "HealthCare",
    "clinical": "HealthCare",
    "patient": "HealthCare",
    # Judicial
    "judicial": "JudicialDecisionSupport",
    "court": "JudicialDecisionSupport",
    "legal": "JudicialDecisionSupport",
    "sentencing": "JudicialDecisionSupport",
    "recidivism": "JudicialDecisionSupport",
    # Public services
    "public service": "PublicServiceAllocation",
    "social benefit": "PublicServiceAllocation",
    "welfare": "PublicServiceAllocation",
    "credit scoring": "PublicServiceAllocation",
    "insurance": "PublicServiceAllocation",
}


class ForensicSPARQLService:
    """
    SPARQL query service for forensic compliance analysis.
    Uses MCP server for all ontology queries.
    """

    def __init__(self, mcp_url: Optional[str] = None):
        """
        Initialize with MCP client.

        Args:
            mcp_url: URL of MCP SPARQL server
        """
        self.mcp = MCPClient(mcp_url)
        self._connected = False

    async def ensure_connected(self) -> bool:
        """Verify MCP server is available."""
        if not self._connected:
            self._connected = await self.mcp.health_check()
            if self._connected:
                print("✓ Connected to MCP SPARQL server")
            else:
                print("⚠ MCP server not available, will retry on queries")
        return self._connected

    async def query_mandatory_requirements(
        self,
        purpose: str,
        contexts: List[str],
        data_types: List[str]
    ) -> Dict:
        """
        Query ontology for mandatory EU AI Act requirements via MCP.

        Args:
            purpose: Primary purpose (e.g., "BiometricIdentification")
            contexts: Deployment contexts (e.g., ["PublicSpaces", "HighVolume"])
            data_types: Data types processed (e.g., ["BiometricData"])

        Returns:
            Dict with criteria, requirements, and risk level
        """
        # Build SPARQL query - map purpose to ontology IRI
        purpose_mapped = self._map_purpose_to_ontology(purpose) if purpose else ""
        purpose_uri = f"ai:{purpose_mapped}" if purpose_mapped else ""
        # Sanitize contexts too
        context_values = " ".join([f"ai:{self._sanitize_to_iri(ctx)}" for ctx in contexts if ctx])

        print(f"   → Purpose mapped: '{purpose}' → '{purpose_mapped}'")
        if context_values:
            print(f"   → Contexts: {context_values}")

        query = f"""
        PREFIX ai: <http://ai-act.eu/ai#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?requirement ?requirementLabel ?criterion ?criterionLabel
        WHERE {{
          {{
            # Purpose-based criteria
            {f"{purpose_uri} ai:activatesCriterion ?criterion ." if purpose else ""}
          }}
          {"UNION" if purpose and context_values else ""}
          {f'''{{
            # Context-based criteria
            VALUES ?context {{ {context_values} }}
            ?context ai:triggersCriterion ?criterion .
          }}''' if context_values else ""}

          # Get requirements from criteria
          ?criterion ai:activatesRequirement ?requirement .
          ?requirement rdfs:label ?requirementLabel .

          OPTIONAL {{
            ?criterion rdfs:label ?criterionLabel .
          }}
        }}
        ORDER BY ?requirementLabel
        """

        try:
            result = await self.mcp.query_ontology(query)

            if "error" in result:
                print(f"⚠ MCP query error: {result['error']}")
                return self._empty_requirements_result()

            # Parse SPARQL results
            bindings = result.get("results", {}).get("bindings", [])

            requirements = []
            criteria = set()
            seen_requirements = set()

            for row in bindings:
                req_uri = row.get("requirement", {}).get("value", "")

                if req_uri in seen_requirements:
                    continue
                seen_requirements.add(req_uri)

                requirements.append({
                    "uri": req_uri,
                    "label": row.get("requirementLabel", {}).get("value", req_uri.split("#")[-1]),
                    "criterion": row.get("criterion", {}).get("value", "")
                })

                criterion = row.get("criterion", {}).get("value")
                if criterion:
                    criteria.add(criterion)

            # Determine risk level from ontology criteria OR from input keywords
            if criteria:
                risk_level = self._determine_risk_level(list(criteria))
            else:
                # Fallback: determine from input keywords when ontology has no data
                risk_level = self._determine_risk_from_inputs(purpose, contexts, data_types)

            return {
                "criteria": list(criteria),
                "requirements": requirements,
                "risk_level": risk_level,
                "total_requirements": len(requirements)
            }

        except Exception as e:
            print(f"✗ Error querying mandatory requirements: {e}")
            return self._empty_requirements_result()

    async def query_iso_42001_mappings(self, eu_requirements: List[str]) -> Dict:
        """
        Query ISO 42001 mappings for EU AI Act requirements via MCP.

        Args:
            eu_requirements: List of EU AI Act requirement URIs

        Returns:
            Dict with ISO controls mapped to each requirement
        """
        iso_mappings = {}

        for req_uri in eu_requirements[:10]:  # Limit to avoid too many calls
            req_name = req_uri.split("#")[-1] if "#" in req_uri else req_uri

            try:
                result = await self.mcp.query_iso_mappings(req_name)

                if "error" not in result:
                    bindings = result.get("results", {}).get("bindings", [])
                    for row in bindings:
                        iso_mappings[req_uri] = {
                            "iso_control": row.get("isoControl", {}).get("value", ""),
                            "iso_section": row.get("isoSection", {}).get("value", ""),
                            "description": row.get("description", {}).get("value", ""),
                            "confidence": row.get("confidence", {}).get("value", "HIGH")
                        }
            except Exception as e:
                print(f"⚠ ISO mapping query failed for {req_name}: {e}")

        return iso_mappings

    async def query_nist_ai_rmf_mappings(
        self,
        eu_requirements: List[str],
        jurisdiction: str = "GLOBAL"
    ) -> Dict:
        """
        Query NIST AI RMF mappings for EU AI Act requirements via MCP.

        Args:
            eu_requirements: List of EU AI Act requirement URIs
            jurisdiction: "US", "GLOBAL", or "EU"

        Returns:
            Dict with NIST functions mapped to each requirement
        """
        nist_mappings = {}

        for req_uri in eu_requirements[:10]:  # Limit to avoid too many calls
            req_name = req_uri.split("#")[-1] if "#" in req_uri else req_uri

            try:
                result = await self.mcp.query_nist_mappings(req_name)

                if "error" not in result:
                    bindings = result.get("results", {}).get("bindings", [])
                    for row in bindings:
                        nist_mappings[req_uri] = {
                            "nist_function": row.get("nistFunction", {}).get("value", ""),
                            "nist_category": row.get("category", {}).get("value", ""),
                            "description": row.get("description", {}).get("value", ""),
                            "confidence": row.get("confidence", {}).get("value", "HIGH"),
                            "applicability": row.get("applicability", {}).get("value", jurisdiction)
                        }
            except Exception as e:
                print(f"⚠ NIST mapping query failed for {req_name}: {e}")

        return nist_mappings

    async def analyze_compliance_gaps(
        self,
        mandatory_requirements: List[str],
        incident_properties: Dict
    ) -> Dict:
        """
        Analyze compliance gaps based on incident properties.

        Args:
            mandatory_requirements: List of required requirement URIs
            incident_properties: Incident details

        Returns:
            Gap analysis with missing requirements
        """
        # Infer implemented requirements from incident response
        implemented = self._infer_implemented_requirements(incident_properties)

        # Compute gaps
        mandatory_set = set(mandatory_requirements)
        implemented_set = set(implemented)
        missing = mandatory_set - implemented_set

        # Categorize by severity
        critical_gaps = self._categorize_critical_gaps(list(missing))

        # Calculate compliance ratio
        compliance_ratio = len(implemented) / len(mandatory_requirements) if mandatory_requirements else 0.0

        return {
            "total_required": len(mandatory_requirements),
            "implemented": len(implemented),
            "missing": len(missing),
            "compliance_ratio": compliance_ratio,
            "missing_requirements": list(missing),
            "critical_gaps": critical_gaps,
            "severity": self._assess_gap_severity(len(missing), len(mandatory_requirements))
        }

    def _determine_risk_level(self, criteria: List[str]) -> str:
        """Determine risk level from activated criteria."""
        criteria_str = " ".join(criteria).lower()

        high_risk_keywords = [
            "biometric", "lawenforcement", "migration", "employment",
            "education", "criticalinfrastructure", "emotionrecognition",
            "socialscoring", "predictivepolicing", "healthcare", "health",
            "recruitment", "judicial", "essential"
        ]

        for keyword in high_risk_keywords:
            if keyword in criteria_str:
                return "HighRisk"

        limited_risk_keywords = ["limitedemotion", "deepfake", "contentclassification"]

        for keyword in limited_risk_keywords:
            if keyword in criteria_str:
                return "LimitedRisk"

        return "MinimalRisk"

    def _determine_risk_from_inputs(
        self,
        purpose: str,
        contexts: List[str],
        data_types: List[str]
    ) -> str:
        """
        Determine EU AI Act risk level based on input keywords.
        This is a fallback when the ontology doesn't have matching data.

        Based on EU AI Act Article 6 and Annex III high-risk categories.
        """
        # Combine all inputs for keyword matching
        all_text = " ".join([
            purpose or "",
            " ".join(contexts or []),
            " ".join(data_types or [])
        ]).lower()

        # PROHIBITED (Unacceptable Risk) - Article 5
        prohibited_keywords = [
            "social scoring", "socialscoring", "social credit",
            "subliminal", "manipulation", "exploit vulnerability",
            "predictive policing", "predictivepolicing",
            "mass surveillance", "real-time remote biometric"
        ]
        for keyword in prohibited_keywords:
            if keyword in all_text:
                return "Unacceptable"

        # HIGH RISK - Annex III categories
        high_risk_keywords = [
            # Biometric identification
            "biometric", "facial recognition", "face recognition",
            "fingerprint", "iris scan", "voice recognition",
            # Law enforcement
            "law enforcement", "lawenforcement", "police", "criminal",
            "border", "migration", "asylum",
            # Critical infrastructure
            "critical infrastructure", "criticalinfrastructure",
            "energy", "water supply", "transport",
            "autonomous", "self-driving", "autonomous vehicle",
            # Education and employment
            "education", "student", "recruitment", "employment",
            "hiring", "worker", "performance evaluation",
            # Healthcare - Annex III, point 5(a): medical devices
            "healthcare", "health care", "medical", "diagnosis",
            "clinical", "patient", "therapeutic", "health",
            # Essential services
            "credit scoring", "creditscoring", "insurance",
            "social benefit", "emergency services",
            # Justice and democracy
            "court", "judicial", "election", "voting"
        ]
        for keyword in high_risk_keywords:
            if keyword in all_text:
                return "HighRisk"

        # LIMITED RISK - Article 52 transparency obligations
        limited_risk_keywords = [
            "chatbot", "emotion recognition", "emotionrecognition",
            "deepfake", "synthetic", "generated content",
            "virtual assistant", "conversational"
        ]
        for keyword in limited_risk_keywords:
            if keyword in all_text:
                return "LimitedRisk"

        # Default to Minimal Risk
        return "MinimalRisk"

    def _infer_implemented_requirements(self, incident_properties: Dict) -> List[str]:
        """Infer implemented requirements from incident description."""
        implemented = []

        response = incident_properties.get("response", {})
        actions = response.get("actions_taken", [])
        action_str = " ".join(actions).lower()

        requirement_keywords = {
            "DocumentationRequirement": ["documentation", "record", "log"],
            "TransparencyRequirement": ["transparency", "disclosure", "inform"],
            "MonitoringRequirement": ["monitoring", "audit", "review"],
            "DataGovernanceRequirement": ["data quality", "data governance"],
            "HumanOversightRequirement": ["human oversight", "human review"],
            "AccuracyRequirement": ["test", "accuracy", "validation"]
        }

        for req, keywords in requirement_keywords.items():
            for keyword in keywords:
                if keyword in action_str:
                    implemented.append(f"{AI_PREFIX}{req}")
                    break

        return implemented

    def _categorize_critical_gaps(self, missing: List[str]) -> List[Dict]:
        """Categorize missing requirements by criticality."""
        critical_keywords = [
            ("Biometric", "Critical: Biometric data protection requirement"),
            ("Security", "Critical: Security requirement"),
            ("Safety", "Critical: Safety requirement"),
            ("HumanOversight", "Critical: Human oversight requirement"),
            ("FundamentalRights", "Critical: Fundamental rights requirement"),
            ("NonDiscrimination", "Critical: Non-discrimination requirement"),
            ("Fairness", "Critical: Fairness requirement"),
            ("Bias", "Critical: Bias detection/mitigation requirement")
        ]

        critical = []
        for req in missing:
            req_name = req.split("#")[-1] if "#" in req else req

            for keyword, reason in critical_keywords:
                if keyword.lower() in req_name.lower():
                    critical.append({"requirement": req, "reason": reason})
                    break

        return critical

    def _assess_gap_severity(self, missing_count: int, total_count: int) -> str:
        """Assess severity of compliance gaps."""
        if total_count == 0:
            return "UNKNOWN"

        ratio = missing_count / total_count

        if ratio >= 0.7:
            return "CRITICAL"
        elif ratio >= 0.4:
            return "HIGH"
        elif ratio >= 0.2:
            return "MEDIUM"
        elif ratio > 0:
            return "LOW"
        else:
            return "COMPLIANT"

    def _empty_requirements_result(self) -> Dict:
        """Return empty requirements result structure."""
        return {
            "criteria": [],
            "requirements": [],
            "risk_level": "Unknown",
            "total_requirements": 0
        }

    def _map_purpose_to_ontology(self, purpose: str) -> str:
        """
        Map an extracted purpose text to the ontology IRI name.

        Args:
            purpose: The extracted purpose (e.g., "facial recognition", "autonomous driving")
                     OR an already valid ontology IRI (e.g., "BiometricIdentification")

        Returns:
            The ontology IRI name (e.g., "BiometricIdentification") or sanitized version
        """
        if not purpose:
            return ""

        # If already a valid ontology IRI, return as-is
        if purpose in VALID_PURPOSE_IRIS:
            return purpose

        purpose_lower = purpose.lower()

        # Try to match against known patterns
        for pattern, iri_name in PURPOSE_MAPPING.items():
            if pattern in purpose_lower:
                return iri_name

        # Fallback: sanitize to IRI format
        return self._sanitize_to_iri(purpose)

    def _sanitize_to_iri(self, value: str) -> str:
        """
        Sanitize a string to be a valid IRI local name.
        Converts 'Plan violent assault' to 'PlanViolentAssault'.
        """
        if not value:
            return ""
        # Remove special characters, keep alphanumeric and spaces
        import re
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', value)
        # Convert to CamelCase
        words = cleaned.split()
        return ''.join(word.capitalize() for word in words)

    async def get_stats(self) -> Dict:
        """Get ontology statistics via MCP."""
        try:
            result = await self.mcp.get_ontology_stats()
            if "error" not in result:
                return result
        except Exception as e:
            print(f"⚠ Stats query failed: {e}")

        return {
            "total_triples": 0,
            "mcp_connected": self._connected
        }

    async def get_inference_rules(self) -> Dict:
        """
        Get all inference rules from the reasoning engine via MCP.

        Returns:
            Dict with condition_consequence_rules, navigation_rules, and metadata
        """
        try:
            result = await self.mcp.get_inference_rules()
            if "error" not in result:
                return result
        except Exception as e:
            print(f"⚠ Inference rules query failed: {e}")

        return {
            "condition_consequence_rules": [],
            "navigation_rules": [],
            "metadata": {"error": "Failed to load rules"}
        }

    async def get_applicable_rules(self, incident_properties: Dict) -> Dict:
        """
        Get inference rules that apply to a specific incident based on its properties.

        Args:
            incident_properties: Extracted incident details

        Returns:
            Dict with applicable rules and explanations
        """
        try:
            all_rules = await self.get_inference_rules()

            if "error" in all_rules.get("metadata", {}):
                return {"applicable_rules": [], "explanation": "Rules not available"}

            applicable = []
            system = incident_properties.get("system", {})

            # Check condition/consequence rules
            for rule in all_rules.get("condition_consequence_rules", []):
                applies, reason = self._check_rule_applicability(rule, system)
                if applies:
                    applicable.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "category": rule.get("category", "unknown"),
                        "reason": reason,
                        "conditions": rule.get("conditions", []),
                        "consequences": rule.get("consequences", [])
                    })

            # Navigation rules always apply for transitive inference
            nav_rules = all_rules.get("navigation_rules", [])

            return {
                "applicable_rules": applicable,
                "navigation_rules": nav_rules,
                "total_applicable": len(applicable),
                "total_navigation": len(nav_rules),
                "explanation": self._generate_rules_explanation(applicable, nav_rules)
            }

        except Exception as e:
            print(f"⚠ Applicable rules query failed: {e}")
            return {"applicable_rules": [], "explanation": f"Error: {e}"}

    def _check_rule_applicability(self, rule: Dict, system: Dict) -> tuple:
        """
        Check if a rule applies to the system based on its conditions.

        Returns:
            (applies: bool, reason: str)
        """
        rule_name = rule.get("name", rule.get("id", "unknown"))
        category = rule.get("category", "unknown")

        # Get system properties
        purpose = system.get("primary_purpose", "").lower()
        contexts = [c.lower() for c in system.get("deployment_context", [])]
        data_types = [d.lower() for d in system.get("processes_data_types", [])]
        model_scale = system.get("model_scale", "").lower()
        has_oversight = system.get("has_human_oversight", True)

        # Purpose-based rules
        if "biometric" in purpose or "biometric" in " ".join(contexts):
            if "biometric" in rule_name.lower() or category in ["base_contextual"]:
                return True, f"System purpose '{purpose}' triggers this rule"

        # Context-based rules
        if "lawenforcement" in " ".join(contexts) or "publicspaces" in " ".join(contexts):
            if category in ["base_contextual", "cascade"]:
                return True, "Deployment context triggers high-risk classification"

        # Technical rules based on model scale
        if model_scale and "foundation" in model_scale:
            if "gpai" in rule_name.lower() or "foundation" in rule_name.lower() or "scale" in rule_name.lower():
                return True, "Foundation model scale triggers GPAI rules"

        # Human oversight rules
        if not has_oversight:
            if "oversight" in rule_name.lower() or "autonomy" in rule_name.lower():
                return True, "Lack of human oversight triggers this rule"

        # Data type rules
        if "biometricdata" in " ".join(data_types):
            if "data" in rule_name.lower() or category == "base_contextual":
                return True, "Biometric data processing triggers data governance rules"

        # Emotion recognition
        if "emotion" in purpose:
            if "emotion" in rule_name.lower():
                return True, "Emotion recognition purpose triggers specific rules"

        return False, ""

    def _generate_rules_explanation(self, applicable: List[Dict], nav_rules: List[Dict]) -> str:
        """Generate human-readable explanation of applicable rules."""
        if not applicable and not nav_rules:
            return "No inference rules were determined to be applicable to this incident."

        lines = []

        if applicable:
            lines.append(f"**{len(applicable)} condition-based rules apply:**")
            for rule in applicable[:5]:  # Limit to first 5
                lines.append(f"- **{rule['rule_name']}** ({rule['category']})")
                lines.append(f"  Reason: {rule['reason']}")
            if len(applicable) > 5:
                lines.append(f"  ... and {len(applicable) - 5} more rules")

        if nav_rules:
            lines.append(f"\n**{len(nav_rules)} navigation rules for transitive inference:**")
            for rule in nav_rules[:3]:
                lines.append(f"- {rule['name']}: {rule.get('description', '')}")

        return "\n".join(lines)
