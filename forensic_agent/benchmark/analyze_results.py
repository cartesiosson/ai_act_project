#!/usr/bin/env python3
"""
Analyze benchmark results and generate detailed report
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter
import statistics


def load_latest_results():
    """Load most recent benchmark results"""
    results_dir = Path(__file__).parent / "results"

    if not results_dir.exists():
        print(f"✗ Results directory not found: {results_dir}")
        sys.exit(1)

    results_files = sorted(results_dir.glob("benchmark_results_*.json"), reverse=True)

    if not results_files:
        print(f"✗ No results files found")
        sys.exit(1)

    results_file = results_files[0]
    print(f"✓ Loading: {results_file.name}\n")

    with open(results_file) as f:
        results = json.load(f)

    return results, results_file


def analyze_requirements(results: List[Dict]) -> Dict:
    """Analyze EU AI Act requirements distribution"""

    all_requirements = []
    all_missing = []

    for result in results:
        if result.get("status") == "COMPLETED":
            # Collect requirements
            requirements = result.get("eu_ai_act", {}).get("requirements", [])
            for req in requirements:
                all_requirements.append(req.get("label", "Unknown"))

            # Collect missing
            missing = result.get("compliance_gaps", {}).get("missing_requirements", [])
            for miss in missing:
                # Extract label from URI
                label = miss.split("#")[-1] if "#" in miss else miss
                all_missing.append(label)

    req_counts = Counter(all_requirements)
    missing_counts = Counter(all_missing)

    return {
        "requirements": dict(req_counts.most_common(15)),
        "missing": dict(missing_counts.most_common(15)),
        "total_unique_requirements": len(req_counts),
        "total_unique_missing": len(missing_counts)
    }


def analyze_organizations(results: List[Dict]) -> Dict:
    """Analyze organizations and their incidents"""

    org_incidents = {}

    for result in results:
        if result.get("status") == "COMPLETED":
            extraction = result.get("extraction", {})
            org = extraction.get("system", {}).get("organization", "Unknown")
            incident_type = extraction.get("incident", {}).get("incident_type", "unknown")
            severity = extraction.get("incident", {}).get("severity", "unknown")
            risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")

            if org not in org_incidents:
                org_incidents[org] = {
                    "count": 0,
                    "incident_types": Counter(),
                    "severities": Counter(),
                    "risk_levels": Counter()
                }

            org_incidents[org]["count"] += 1
            org_incidents[org]["incident_types"][incident_type] += 1
            org_incidents[org]["severities"][severity] += 1
            org_incidents[org]["risk_levels"][risk_level] += 1

    # Sort by count
    sorted_orgs = sorted(org_incidents.items(), key=lambda x: x[1]["count"], reverse=True)

    return {
        org: {
            "count": data["count"],
            "incident_types": dict(data["incident_types"].most_common(3)),
            "severities": dict(data["severities"]),
            "risk_levels": dict(data["risk_levels"])
        }
        for org, data in sorted_orgs[:15]
    }


def analyze_system_purposes(results: List[Dict]) -> Dict:
    """Analyze AI system purposes"""

    purposes = Counter()
    purpose_risks = {}

    for result in results:
        if result.get("status") == "COMPLETED":
            extraction = result.get("extraction", {})
            purpose = extraction.get("system", {}).get("primary_purpose", "Unknown")
            risk_level = result.get("eu_ai_act", {}).get("risk_level", "Unknown")

            purposes[purpose] += 1

            if purpose not in purpose_risks:
                purpose_risks[purpose] = Counter()
            purpose_risks[purpose][risk_level] += 1

    return {
        "purposes": dict(purposes.most_common(15)),
        "purpose_risk_mapping": {
            purpose: dict(risks)
            for purpose, risks in purpose_risks.items()
        }
    }


def analyze_data_types(results: List[Dict]) -> Dict:
    """Analyze data types processed"""

    data_types = Counter()

    for result in results:
        if result.get("status") == "COMPLETED":
            extraction = result.get("extraction", {})
            types = extraction.get("system", {}).get("processes_data_types", [])
            for dt in types:
                data_types[dt] += 1

    return dict(data_types.most_common(10))


def analyze_affected_populations(results: List[Dict]) -> Dict:
    """Analyze affected populations"""

    populations = Counter()

    for result in results:
        if result.get("status") == "COMPLETED":
            extraction = result.get("extraction", {})
            pops = extraction.get("incident", {}).get("affected_populations", [])
            for pop in pops:
                populations[pop] += 1

    return dict(populations.most_common(15))


def generate_detailed_report(results: List[Dict], output_file: Path):
    """Generate detailed markdown report"""

    # Compute all analyses
    requirements_analysis = analyze_requirements(results)
    org_analysis = analyze_organizations(results)
    purpose_analysis = analyze_system_purposes(results)
    data_types = analyze_data_types(results)
    populations = analyze_affected_populations(results)

    # Load stats
    stats_files = sorted(output_file.parent.glob("benchmark_stats_*.json"), reverse=True)
    if stats_files:
        with open(stats_files[0]) as f:
            stats = json.load(f)
    else:
        stats = {}

    # Generate report
    report = []
    report.append("# Forensic Agent - Benchmark Analysis Report\n")
    report.append(f"**Generated:** {Path(output_file).name}\n")
    report.append("---\n\n")

    # Executive Summary
    report.append("## Executive Summary\n\n")
    summary = stats.get("summary", {})
    report.append(f"- **Total Incidents Analyzed:** {summary.get('total_incidents', 0)}\n")
    report.append(f"- **Successful:** {summary.get('successful', 0)} ({summary.get('success_rate', 0):.1f}%)\n")
    report.append(f"- **Low Confidence:** {summary.get('low_confidence', 0)}\n")
    report.append(f"- **Failed:** {summary.get('failed', 0)}\n\n")

    # Performance Metrics
    report.append("## Performance Metrics\n\n")
    perf = stats.get("performance", {})
    if perf:
        report.append(f"- **Mean Processing Time:** {perf.get('mean_time', 0):.2f}s\n")
        report.append(f"- **Median Processing Time:** {perf.get('median_time', 0):.2f}s\n")
        report.append(f"- **Min/Max Time:** {perf.get('min_time', 0):.2f}s / {perf.get('max_time', 0):.2f}s\n")
        report.append(f"- **Standard Deviation:** {perf.get('stdev_time', 0):.2f}s\n")
        report.append(f"- **Estimated Throughput:** {3600 / perf.get('mean_time', 1):.1f} incidents/hour\n\n")

    # Quality Metrics
    report.append("## Extraction Quality\n\n")
    qual = stats.get("quality", {})
    if qual:
        report.append(f"- **Mean Confidence:** {qual.get('mean_confidence', 0):.3f}\n")
        report.append(f"- **Median Confidence:** {qual.get('median_confidence', 0):.3f}\n")
        report.append(f"- **Min/Max Confidence:** {qual.get('min_confidence', 0):.3f} / {qual.get('max_confidence', 0):.3f}\n")
        report.append(f"- **Standard Deviation:** {qual.get('stdev_confidence', 0):.3f}\n\n")

    # Risk Distribution
    report.append("## Risk Level Distribution\n\n")
    risk_dist = stats.get("risk_distribution", {})
    if risk_dist:
        total = sum(risk_dist.values())
        report.append("| Risk Level | Count | Percentage |\n")
        report.append("|------------|-------|------------|\n")
        for risk, count in sorted(risk_dist.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100 if total > 0 else 0
            report.append(f"| {risk} | {count} | {pct:.1f}% |\n")
        report.append("\n")

    # Incident Type Distribution
    report.append("## Incident Type Distribution\n\n")
    incident_dist = stats.get("incident_distribution", {})
    if incident_dist:
        total = sum(incident_dist.values())
        report.append("| Incident Type | Count | Percentage |\n")
        report.append("|---------------|-------|------------|\n")
        for itype, count in sorted(incident_dist.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100 if total > 0 else 0
            report.append(f"| {itype} | {count} | {pct:.1f}% |\n")
        report.append("\n")

    # Requirements Analysis
    report.append("## EU AI Act Requirements Analysis\n\n")
    report.append(f"**Total Unique Requirements:** {requirements_analysis['total_unique_requirements']}\n\n")
    report.append("### Most Frequent Requirements\n\n")
    report.append("| Requirement | Occurrences |\n")
    report.append("|-------------|-------------|\n")
    for req, count in list(requirements_analysis['requirements'].items())[:10]:
        report.append(f"| {req} | {count} |\n")
    report.append("\n")

    report.append("### Most Frequent Missing Requirements (Compliance Gaps)\n\n")
    report.append("| Missing Requirement | Occurrences |\n")
    report.append("|---------------------|-------------|\n")
    for req, count in list(requirements_analysis['missing'].items())[:10]:
        report.append(f"| {req} | {count} |\n")
    report.append("\n")

    # Organization Analysis
    report.append("## Organization Analysis\n\n")
    report.append("### Top Organizations by Incident Count\n\n")
    for org, data in list(org_analysis.items())[:10]:
        report.append(f"**{org}** ({data['count']} incidents)\n")
        report.append(f"- Incident types: {', '.join(f'{k}({v})' for k, v in data['incident_types'].items())}\n")
        report.append(f"- Risk levels: {', '.join(f'{k}({v})' for k, v in data['risk_levels'].items())}\n\n")

    # System Purposes
    report.append("## AI System Purposes\n\n")
    report.append("| Purpose | Count |\n")
    report.append("|---------|-------|\n")
    for purpose, count in list(purpose_analysis['purposes'].items())[:10]:
        report.append(f"| {purpose} | {count} |\n")
    report.append("\n")

    # Data Types
    report.append("## Data Types Processed\n\n")
    report.append("| Data Type | Count |\n")
    report.append("|-----------|-------|\n")
    for dtype, count in list(data_types.items())[:10]:
        report.append(f"| {dtype} | {count} |\n")
    report.append("\n")

    # Affected Populations
    report.append("## Affected Populations\n\n")
    report.append("| Population | Count |\n")
    report.append("|------------|-------|\n")
    for pop, count in list(populations.items())[:10]:
        report.append(f"| {pop} | {count} |\n")
    report.append("\n")

    # Key Insights
    report.append("## Key Insights\n\n")

    # Insight 1: Most common risk level
    if risk_dist:
        most_common_risk = max(risk_dist.items(), key=lambda x: x[1])
        report.append(f"1. **Most Common Risk Level:** {most_common_risk[0]} ({most_common_risk[1]} systems, {most_common_risk[1]/sum(risk_dist.values())*100:.1f}%)\n")

    # Insight 2: Most vulnerable purpose
    if purpose_analysis['purposes']:
        most_common_purpose = max(purpose_analysis['purposes'].items(), key=lambda x: x[1])
        report.append(f"2. **Most Common System Purpose:** {most_common_purpose[0]} ({most_common_purpose[1]} systems)\n")

    # Insight 3: Most common gap
    if requirements_analysis['missing']:
        most_common_gap = max(requirements_analysis['missing'].items(), key=lambda x: x[1])
        report.append(f"3. **Most Common Compliance Gap:** {most_common_gap[0]} (missing in {most_common_gap[1]} systems)\n")

    # Insight 4: Most affected population
    if populations:
        most_affected = max(populations.items(), key=lambda x: x[1])
        report.append(f"4. **Most Affected Population:** {most_affected[0]} ({most_affected[1]} incidents)\n")

    report.append("\n")

    # Recommendations
    report.append("## Recommendations\n\n")
    report.append("1. **Focus on HighRisk systems** - Majority of analyzed systems fall into HighRisk category, requiring comprehensive compliance measures\n")
    report.append("2. **Address common gaps** - Prioritize implementing the most frequently missing requirements across all systems\n")
    report.append("3. **Bias monitoring** - Given the prevalence of discrimination and bias incidents, implement continuous fairness monitoring\n")
    report.append("4. **Vulnerable populations** - Establish special safeguards for the most frequently affected demographic groups\n")
    report.append("5. **Data governance** - Strengthen data governance practices, particularly for biometric and personal data\n\n")

    # Write report
    report_text = "".join(report)
    with open(output_file, 'w') as f:
        f.write(report_text)

    return report_text


def main():
    results, results_file = load_latest_results()

    print(f"Analyzing {len(results)} results...\n")

    # Generate detailed report
    report_file = results_file.parent / results_file.name.replace("results", "analysis").replace(".json", ".md")
    report_text = generate_detailed_report(results, report_file)

    print(f"✓ Detailed analysis saved: {report_file}\n")
    print("="*70)
    print(report_text)
    print("="*70)


if __name__ == "__main__":
    main()
