#!/usr/bin/env python3
"""
Real Compliance Gap Detection Evaluation

Evaluates the forensic agent's ability to detect compliance gaps
by calling the REAL forensic agent API (not simulation).

Usage:
    python run_real_evaluation.py --incidents 10
    python run_real_evaluation.py --all
"""

import argparse
import csv
import json
import os
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import random

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from issue_requirement_mapping import (
    get_expected_requirements,
    get_detected_gaps,
    calculate_metrics,
    get_all_mapped_issues,
)

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    import pandas as pd
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    print("WARNING: matplotlib/seaborn not available")

# Configuration
AIAAIC_CSV = Path(__file__).parent.parent.parent / "AIAAIC Repository - Incidents.csv"
OUTPUT_DIR = Path(__file__).parent / "evaluation_results_real"
FORENSIC_AGENT_URL = "http://localhost:8002"


def load_aiaaic_incidents(csv_path: Path, limit: Optional[int] = None) -> List[Dict]:
    """Load AIAAIC incidents from CSV."""
    incidents = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        next(f)  # Skip title row
        reader = csv.DictReader(f)

        for row in reader:
            if not row.get('AIAAIC ID#') or row.get('AIAAIC ID#').startswith('AIAAIC ID'):
                continue

            issues_raw = row.get('Issue(s)', '')
            issues = [i.strip() for i in issues_raw.split(';') if i.strip()]

            mapped_issues = get_all_mapped_issues()
            relevant_issues = [i for i in issues if i in mapped_issues]

            if relevant_issues:
                incidents.append({
                    'id': row.get('AIAAIC ID#', ''),
                    'headline': row.get('Headline', ''),
                    'sector': row.get('Sector(s)', ''),
                    'technology': row.get('Technology(ies)', ''),
                    'purpose': row.get('Purpose(s)', ''),
                    'issues': issues,
                    'relevant_issues': relevant_issues,
                    'deployer': row.get('Deployer(s)', ''),
                    'developer': row.get('Developer(s)', ''),
                    'country': row.get('Country(ies)', ''),
                    'external_harms': row.get('External harms', ''),
                })

    random.seed(42)
    random.shuffle(incidents)

    if limit:
        incidents = incidents[:limit]

    return incidents


def build_narrative(incident: Dict) -> str:
    """Build narrative text for forensic agent."""
    parts = [
        f"Incident: {incident['headline']}",
        f"Sector: {incident['sector']}" if incident['sector'] else "",
        f"Technology: {incident['technology']}" if incident['technology'] else "",
        f"Purpose: {incident['purpose']}" if incident['purpose'] else "",
        f"Deployer: {incident['deployer']}" if incident['deployer'] else "",
        f"Developer: {incident['developer']}" if incident['developer'] else "",
        f"Country: {incident['country']}" if incident['country'] else "",
        f"Issues identified: {'; '.join(incident['issues'])}",
        f"Harms: {incident['external_harms']}" if incident['external_harms'] else "",
    ]
    return "\n".join(p for p in parts if p)


def call_forensic_agent(narrative: str, incident_id: str, timeout: int = 120) -> Optional[Dict]:
    """Call the real forensic agent API."""
    try:
        response = requests.post(
            f"{FORENSIC_AGENT_URL}/forensic/analyze",
            json={"narrative": narrative},
            timeout=timeout
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ERROR: Status {response.status_code} for {incident_id}")
            return None

    except requests.exceptions.Timeout:
        print(f"  TIMEOUT: {incident_id} exceeded {timeout}s")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  REQUEST ERROR: {incident_id} - {e}")
        return None


def extract_missing_requirements(agent_result: Dict) -> List[str]:
    """Extract missing requirements from agent response."""
    missing = []

    # Try different possible paths in the response
    if 'compliance_gaps' in agent_result:
        gaps = agent_result['compliance_gaps']
        if isinstance(gaps, dict):
            missing = gaps.get('missing_requirements', [])

    # Also check eu_ai_act requirements
    if 'eu_ai_act' in agent_result:
        eu = agent_result['eu_ai_act']
        if isinstance(eu, dict):
            reqs = eu.get('requirements', [])
            for req in reqs:
                if isinstance(req, dict):
                    uri = req.get('uri', '')
                    if uri:
                        missing.append(uri)
                elif isinstance(req, str):
                    missing.append(req)

    return missing


def evaluate_single_incident(incident: Dict, timeout: int = 120) -> Dict:
    """Evaluate agent performance on single incident using real API."""
    narrative = build_narrative(incident)

    # Get expected requirements based on AIAAIC issues
    expected = get_expected_requirements(incident['relevant_issues'])

    # Call real forensic agent
    start_time = time.time()
    agent_result = call_forensic_agent(narrative, incident['id'], timeout)
    elapsed = time.time() - start_time

    if agent_result is None:
        return {
            'incident_id': incident['id'],
            'headline': incident['headline'][:80],
            'issues': incident['relevant_issues'],
            'expected_requirements': list(expected),
            'detected_requirements': [],
            'metrics': {
                'true_positives': 0,
                'additional_detected': 0,
                'missed': len(expected),
                'coverage': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0,
                # Legacy
                'false_positives': 0,
                'false_negatives': len(expected),
            },
            'risk_level': 'Unknown',
            'status': 'ERROR',
            'elapsed_seconds': elapsed,
        }

    # Extract detected missing requirements
    missing_reqs = extract_missing_requirements(agent_result)
    detected = get_detected_gaps(missing_reqs)

    # Calculate metrics
    metrics = calculate_metrics(expected, detected)

    # Get risk level
    risk_level = 'Unknown'
    if 'eu_ai_act' in agent_result:
        risk_level = agent_result['eu_ai_act'].get('risk_level', 'Unknown')

    return {
        'incident_id': incident['id'],
        'headline': incident['headline'][:80],
        'issues': incident['relevant_issues'],
        'expected_requirements': list(expected),
        'detected_requirements': list(detected),
        'metrics': metrics,
        'risk_level': risk_level,
        'status': agent_result.get('status', 'COMPLETED'),
        'elapsed_seconds': elapsed,
        'confidence': agent_result.get('extraction', {}).get('confidence', 0),
    }


def run_evaluation(incidents: List[Dict], timeout: int = 120) -> Dict:
    """Run full evaluation on incident set."""
    results = []
    successful = 0
    failed = 0

    print(f"\nEvaluating {len(incidents)} incidents with REAL forensic agent...")
    print("=" * 60)

    for i, incident in enumerate(incidents):
        print(f"[{i+1}/{len(incidents)}] {incident['id']}: {incident['headline'][:50]}...")

        result = evaluate_single_incident(incident, timeout)
        results.append(result)

        if result['status'] == 'ERROR':
            failed += 1
            print(f"  -> FAILED ({result['elapsed_seconds']:.1f}s)")
        else:
            successful += 1
            coverage = result['metrics'].get('coverage', result['metrics'].get('recall', 0))
            print(f"  -> OK | Risk: {result['risk_level']} | Coverage: {coverage:.0%} ({result['elapsed_seconds']:.1f}s)")

    # Filter successful results for aggregate metrics
    successful_results = [r for r in results if r['status'] != 'ERROR']

    if not successful_results:
        return {
            'timestamp': datetime.now().isoformat(),
            'total_incidents': len(incidents),
            'successful': 0,
            'failed': len(incidents),
            'aggregate_metrics': {
                'precision': 0, 'recall': 0, 'f1': 0,
                'total_true_positives': 0,
                'total_false_positives': 0,
                'total_false_negatives': 0,
            },
            'issue_metrics': {},
            'requirement_metrics': {},
            'per_incident_results': results,
        }

    # Aggregate metrics using new coverage-based approach
    total_tp = sum(r['metrics']['true_positives'] for r in successful_results)
    total_additional = sum(r['metrics'].get('additional_detected', r['metrics'].get('false_positives', 0)) for r in successful_results)
    total_missed = sum(r['metrics'].get('missed', r['metrics'].get('false_negatives', 0)) for r in successful_results)
    total_expected = sum(r['metrics'].get('total_expected', len(r.get('expected_requirements', []))) for r in successful_results)
    total_detected = sum(r['metrics'].get('total_detected', len(r.get('detected_requirements', []))) for r in successful_results)

    # Primary metric: Coverage (what % of expected requirements were detected)
    coverage = total_tp / total_expected if total_expected > 0 else 1.0

    # Legacy metrics for backwards compatibility
    precision = total_tp / total_detected if total_detected > 0 else 0
    recall = coverage  # Same as coverage
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # Average processing time
    avg_time = sum(r['elapsed_seconds'] for r in results) / len(results)

    # Per-issue metrics
    issue_metrics = calculate_per_issue_metrics(successful_results, incidents)

    # Per-requirement metrics
    requirement_metrics = calculate_per_requirement_metrics(successful_results)

    return {
        'timestamp': datetime.now().isoformat(),
        'total_incidents': len(incidents),
        'successful': successful,
        'failed': failed,
        'average_processing_time': avg_time,
        'aggregate_metrics': {
            'coverage': coverage,  # PRIMARY METRIC
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'total_true_positives': total_tp,
            'total_additional_detected': total_additional,  # Not penalized
            'total_missed': total_missed,  # This IS penalized
            'total_expected': total_expected,
            'total_detected': total_detected,
            # Legacy fields
            'total_false_positives': total_additional,
            'total_false_negatives': total_missed,
        },
        'issue_metrics': issue_metrics,
        'requirement_metrics': requirement_metrics,
        'per_incident_results': results,
    }


def calculate_per_issue_metrics(results: List[Dict], incidents: List[Dict]) -> Dict:
    """Calculate detection metrics per AIAAIC issue type."""
    issue_stats = {}

    # Build mapping from incident_id to incident
    incident_map = {inc['id']: inc for inc in incidents}

    for result in results:
        incident = incident_map.get(result['incident_id'], {})
        for issue in incident.get('relevant_issues', []):
            if issue not in issue_stats:
                issue_stats[issue] = {'tp': 0, 'additional': 0, 'missed': 0, 'expected': 0, 'detected': 0, 'count': 0}

            issue_stats[issue]['count'] += 1
            issue_stats[issue]['tp'] += result['metrics'].get('true_positives', 0)
            issue_stats[issue]['additional'] += result['metrics'].get('additional_detected', result['metrics'].get('false_positives', 0))
            issue_stats[issue]['missed'] += result['metrics'].get('missed', result['metrics'].get('false_negatives', 0))
            issue_stats[issue]['expected'] += result['metrics'].get('total_expected', len(result.get('expected_requirements', [])))
            issue_stats[issue]['detected'] += result['metrics'].get('total_detected', len(result.get('detected_requirements', [])))

    for issue, stats in issue_stats.items():
        tp = stats['tp']
        expected = stats['expected']
        detected = stats['detected']
        # Primary metric: Coverage
        stats['coverage'] = tp / expected if expected > 0 else 1.0
        # Legacy metrics
        stats['precision'] = tp / detected if detected > 0 else 0
        stats['recall'] = stats['coverage']
        stats['f1'] = 2 * stats['precision'] * stats['recall'] / (stats['precision'] + stats['recall']) if (stats['precision'] + stats['recall']) > 0 else 0

    return issue_stats


def calculate_per_requirement_metrics(results: List[Dict]) -> Dict:
    """Calculate detection rate per requirement type."""
    req_stats = {}

    for result in results:
        for req in result.get('expected_requirements', []):
            if req not in req_stats:
                req_stats[req] = {'expected': 0, 'detected': 0}
            req_stats[req]['expected'] += 1
            if req in result.get('detected_requirements', []):
                req_stats[req]['detected'] += 1

    for req, stats in req_stats.items():
        stats['detection_rate'] = stats['detected'] / stats['expected'] if stats['expected'] > 0 else 0

    return req_stats


def generate_heatmap(evaluation_results: Dict, output_path: Path):
    """Generate heatmap visualization."""
    if not HAS_VISUALIZATION:
        print("Skipping heatmap (matplotlib not available)")
        return

    issue_metrics = evaluation_results.get('issue_metrics', {})
    if not issue_metrics:
        print("No issue metrics to visualize")
        return

    issues = list(issue_metrics.keys())

    metrics_data = []
    for issue in issues:
        metrics_data.append({
            'Issue': issue,
            'Coverage': issue_metrics[issue].get('coverage', issue_metrics[issue].get('recall', 0)),
            'Precision': issue_metrics[issue]['precision'],
            'F1': issue_metrics[issue]['f1'],
            'Count': issue_metrics[issue]['count'],
        })

    df = pd.DataFrame(metrics_data)

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    agg = evaluation_results['aggregate_metrics']
    coverage_pct = agg.get('coverage', agg.get('recall', 0)) * 100
    fig.suptitle(f'REAL Compliance Gap Detection Evaluation\n{evaluation_results["total_incidents"]} Incidents | Coverage: {coverage_pct:.0f}% (Success: {evaluation_results["successful"]}, Failed: {evaluation_results["failed"]})',
                 fontsize=14, fontweight='bold')

    # 1. Issue-level metrics heatmap (Coverage as primary)
    ax1 = axes[0, 0]
    if len(df) > 0:
        pivot_metrics = df.set_index('Issue')[['Coverage', 'Precision', 'F1']]
        sns.heatmap(pivot_metrics, annot=True, fmt='.2f', cmap='RdYlGn',
                    vmin=0, vmax=1, ax=ax1, cbar_kws={'label': 'Score'})
    ax1.set_title('Detection Metrics by Issue Type (Coverage = Primary)')
    ax1.tick_params(axis='x', rotation=45)

    # 2. Requirement detection rates
    ax2 = axes[0, 1]
    req_metrics = evaluation_results.get('requirement_metrics', {})
    if req_metrics:
        req_names = list(req_metrics.keys())[:10]
        detection_rates = [req_metrics[r]['detection_rate'] for r in req_names]
        colors = ['#2ecc71' if r > 0.7 else '#f39c12' if r > 0.4 else '#e74c3c' for r in detection_rates]
        ax2.barh(req_names, detection_rates, color=colors)
        ax2.set_xlim(0, 1)
        ax2.axvline(x=0.7, color='green', linestyle='--', alpha=0.5)
        ax2.axvline(x=0.4, color='orange', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Detection Rate')
    ax2.set_title('Requirement Detection Rate')

    # 3. Aggregate metrics (Coverage as primary)
    ax3 = axes[1, 0]
    coverage_val = agg.get('coverage', agg.get('recall', 0))
    metrics_names = ['Coverage\n(PRIMARY)', 'Precision', 'F1 Score']
    metrics_values = [coverage_val, agg['precision'], agg['f1']]
    colors = ['#27ae60', '#3498db', '#9b59b6']  # Green for primary metric
    bars = ax3.bar(metrics_names, metrics_values, color=colors)
    ax3.set_ylim(0, 1)
    ax3.set_ylabel('Score')
    ax3.set_title('Aggregate Performance Metrics')
    for bar, val in zip(bars, metrics_values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.0%}', ha='center', va='bottom', fontweight='bold')

    # 4. Detection summary (not confusion matrix - over-detection is OK)
    ax4 = axes[1, 1]
    total_expected = agg.get('total_expected', agg.get('total_true_positives', 0) + agg.get('total_missed', agg.get('total_false_negatives', 0)))
    total_detected = agg.get('total_detected', agg.get('total_true_positives', 0) + agg.get('total_additional_detected', agg.get('total_false_positives', 0)))
    matched = agg['total_true_positives']
    missed = agg.get('total_missed', agg.get('total_false_negatives', 0))
    additional = agg.get('total_additional_detected', agg.get('total_false_positives', 0))

    summary_data = np.array([
        [matched, missed],
        [additional, 0]
    ])
    labels = np.array([
        [f"Matched\n{matched}", f"Missed\n{missed}"],
        [f"Additional\n(OK)\n{additional}", ""]
    ])
    # Use custom colors: green for good, red for bad, blue for neutral
    cmap = sns.color_palette(["#ffffff", "#27ae60", "#e74c3c", "#3498db"])
    sns.heatmap(summary_data, annot=labels, fmt='', cmap='RdYlGn',
                xticklabels=['Detected', 'Not Detected'],
                yticklabels=['Expected', 'Additional'],
                ax=ax4, cbar=False)
    ax4.set_title(f'Detection Summary\n(Expected: {total_expected}, Detected: {total_detected})')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Heatmap saved to: {output_path}")


def generate_report(results_10: Dict, results_20: Dict, results_50: Dict, output_path: Path):
    """Generate markdown report."""

    def get_coverage(res: Dict) -> float:
        agg = res['aggregate_metrics']
        return agg.get('coverage', agg.get('recall', 0))

    def format_metrics(res: Dict) -> str:
        agg = res['aggregate_metrics']
        coverage = get_coverage(res)
        additional = agg.get('total_additional_detected', agg.get('total_false_positives', 0))
        missed = agg.get('total_missed', agg.get('total_false_negatives', 0))
        return f"""
| Metric | Value | Description |
|--------|-------|-------------|
| **Coverage** | **{coverage:.1%}** | **PRIMARY METRIC** - % of expected requirements detected |
| True Positives | {agg['total_true_positives']} | Requirements correctly detected |
| Additional Detected | {additional} | Extra gaps found (NOT penalized) |
| Missed | {missed} | Expected requirements not detected |
| Precision | {agg['precision']:.3f} | (For reference only) |
| F1 Score | {agg['f1']:.3f} | (For reference only) |
| Success Rate | {res['successful']}/{res['total_incidents']} ({100*res['successful']/res['total_incidents']:.0f}%) | API call success rate |
| Avg Processing Time | {res.get('average_processing_time', 0):.1f}s | Per incident |
"""

    c10 = get_coverage(results_10)
    c20 = get_coverage(results_20)
    c50 = get_coverage(results_50)

    report = f"""# REAL Compliance Gap Detection Evaluation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Method:** Real Forensic Agent API calls
**Agent URL:** {FORENSIC_AGENT_URL}

## Executive Summary

This evaluation measures the **real** forensic agent's ability to detect compliance gaps
using AIAAIC Issues as ground truth.

### Key Insight: Over-detection is NOT Penalized

The agent detecting MORE compliance gaps than AIAAIC labels is acceptable behavior.
The agent may be more thorough in identifying potential compliance issues.

**Primary KPI: Coverage** = % of expected requirements that were detected

### Performance Comparison

| Incidents | Success | Coverage | Additional | Missed | Avg Time |
|-----------|---------|----------|------------|--------|----------|
| 10 | {results_10['successful']}/{results_10['total_incidents']} | **{c10:.1%}** | {results_10['aggregate_metrics'].get('total_additional_detected', results_10['aggregate_metrics'].get('total_false_positives', 0))} | {results_10['aggregate_metrics'].get('total_missed', results_10['aggregate_metrics'].get('total_false_negatives', 0))} | {results_10.get('average_processing_time', 0):.1f}s |
| 20 | {results_20['successful']}/{results_20['total_incidents']} | **{c20:.1%}** | {results_20['aggregate_metrics'].get('total_additional_detected', results_20['aggregate_metrics'].get('total_false_positives', 0))} | {results_20['aggregate_metrics'].get('total_missed', results_20['aggregate_metrics'].get('total_false_negatives', 0))} | {results_20.get('average_processing_time', 0):.1f}s |
| 50 | {results_50['successful']}/{results_50['total_incidents']} | **{c50:.1%}** | {results_50['aggregate_metrics'].get('total_additional_detected', results_50['aggregate_metrics'].get('total_false_positives', 0))} | {results_50['aggregate_metrics'].get('total_missed', results_50['aggregate_metrics'].get('total_false_negatives', 0))} | {results_50.get('average_processing_time', 0):.1f}s |

## Detailed Results

### 10 Incidents
{format_metrics(results_10)}

### 20 Incidents
{format_metrics(results_20)}

### 50 Incidents
{format_metrics(results_50)}

## Issue-Level Analysis (50 incidents)

| Issue | Coverage | Precision | F1 | Count |
|-------|----------|-----------|-----|-------|
"""

    for issue, stats in sorted(results_50.get('issue_metrics', {}).items(), key=lambda x: -x[1]['count']):
        coverage = stats.get('coverage', stats.get('recall', 0))
        report += f"| {issue} | {coverage:.0%} | {stats['precision']:.2f} | {stats['f1']:.2f} | {stats['count']} |\n"

    report += """

## Requirement Detection Analysis (50 incidents)

| Requirement | Expected | Detected | Rate |
|-------------|----------|----------|------|
"""

    for req, stats in sorted(results_50.get('requirement_metrics', {}).items(), key=lambda x: -x[1]['expected']):
        report += f"| {req} | {stats['expected']} | {stats['detected']} | {stats['detection_rate']:.1%} |\n"

    report += """

---
*Report generated by SERAMIS Forensic Agent REAL Benchmark*
"""

    with open(output_path, 'w') as f:
        f.write(report)
    print(f"Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Real forensic agent evaluation')
    parser.add_argument('--incidents', type=int, default=10, help='Number of incidents')
    parser.add_argument('--all', action='store_true', help='Run 10, 20, 50 evaluations')
    parser.add_argument('--timeout', type=int, default=180, help='Timeout per incident (seconds)')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Verify agent is accessible
    try:
        health = requests.get(f"{FORENSIC_AGENT_URL}/health", timeout=5)
        print(f"Forensic Agent: {health.json()['status']}")
    except Exception as e:
        print(f"ERROR: Cannot reach forensic agent at {FORENSIC_AGENT_URL}")
        print(f"  {e}")
        sys.exit(1)

    print(f"Loading AIAAIC incidents from: {AIAAIC_CSV}")

    if args.all:
        # Run all evaluations
        print("\n" + "="*60)
        print("Running 10-incident REAL evaluation...")
        incidents_10 = load_aiaaic_incidents(AIAAIC_CSV, limit=10)
        results_10 = run_evaluation(incidents_10, args.timeout)
        generate_heatmap(results_10, OUTPUT_DIR / "heatmap_real_10.png")

        print("\n" + "="*60)
        print("Running 20-incident REAL evaluation...")
        incidents_20 = load_aiaaic_incidents(AIAAIC_CSV, limit=20)
        results_20 = run_evaluation(incidents_20, args.timeout)
        generate_heatmap(results_20, OUTPUT_DIR / "heatmap_real_20.png")

        print("\n" + "="*60)
        print("Running 50-incident REAL evaluation...")
        incidents_50 = load_aiaaic_incidents(AIAAIC_CSV, limit=50)
        results_50 = run_evaluation(incidents_50, args.timeout)
        generate_heatmap(results_50, OUTPUT_DIR / "heatmap_real_50.png")

        generate_report(results_10, results_20, results_50, OUTPUT_DIR / "REAL_EVALUATION_REPORT.md")

        with open(OUTPUT_DIR / "results_real_all.json", 'w') as f:
            json.dump({
                '10_incidents': results_10,
                '20_incidents': results_20,
                '50_incidents': results_50,
            }, f, indent=2, default=str)

        # Print summary
        print("\n" + "="*70)
        print("REAL EVALUATION SUMMARY (Coverage = Primary KPI)")
        print("="*70)
        print(f"\n{'Incidents':<12} {'Success':<10} {'Coverage':<12} {'Additional':<12} {'Missed':<10} {'Avg Time':<10}")
        print("-"*70)
        for name, res in [('10', results_10), ('20', results_20), ('50', results_50)]:
            agg = res['aggregate_metrics']
            rate = f"{res['successful']}/{res['total_incidents']}"
            coverage = agg.get('coverage', agg.get('recall', 0))
            additional = agg.get('total_additional_detected', agg.get('total_false_positives', 0))
            missed = agg.get('total_missed', agg.get('total_false_negatives', 0))
            avg_t = f"{res.get('average_processing_time', 0):.1f}s"
            print(f"{name:<12} {rate:<10} {coverage:<12.1%} {additional:<12} {missed:<10} {avg_t:<10}")
        print("\nNote: Additional detected gaps are NOT penalized - the agent may be more thorough.")

    else:
        incidents = load_aiaaic_incidents(AIAAIC_CSV, limit=args.incidents)
        print(f"Loaded {len(incidents)} incidents")

        results = run_evaluation(incidents, args.timeout)
        generate_heatmap(results, OUTPUT_DIR / f"heatmap_real_{args.incidents}.png")

        with open(OUTPUT_DIR / f"results_real_{args.incidents}.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)

        agg = results['aggregate_metrics']
        coverage = agg.get('coverage', agg.get('recall', 0))
        additional = agg.get('total_additional_detected', agg.get('total_false_positives', 0))
        missed = agg.get('total_missed', agg.get('total_false_negatives', 0))
        print("\n" + "="*60)
        print(f"REAL EVALUATION RESULTS ({args.incidents} incidents)")
        print("="*60)
        print(f"Success Rate: {results['successful']}/{results['total_incidents']}")
        print(f"COVERAGE (PRIMARY):  {coverage:.1%}")
        print(f"Additional detected: {additional} (not penalized)")
        print(f"Missed:              {missed}")
        print(f"Precision:           {agg['precision']:.3f} (for reference)")
        print(f"F1 Score:            {agg['f1']:.3f} (for reference)")


if __name__ == "__main__":
    main()
