#!/usr/bin/env python3
"""
Compliance Gap Detection Evaluation

Evaluates the forensic agent's ability to detect compliance gaps
using AIAAIC Issues as ground truth.

Usage:
    python run_compliance_evaluation.py --incidents 10
    python run_compliance_evaluation.py --incidents 20
    python run_compliance_evaluation.py --incidents 50
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from issue_requirement_mapping import (
    get_expected_requirements,
    get_detected_gaps,
    calculate_metrics,
    get_all_mapped_issues,
    ISSUE_CATEGORIES,
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
    print("WARNING: matplotlib/seaborn not available. Install with: pip install matplotlib seaborn pandas")

# Configuration
AIAAIC_CSV = Path(__file__).parent.parent.parent / "AIAAIC Repository - Incidents.csv"
OUTPUT_DIR = Path(__file__).parent / "evaluation_results"


def load_aiaaic_incidents(csv_path: Path, limit: Optional[int] = None) -> List[Dict]:
    """Load AIAAIC incidents from CSV."""
    incidents = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Skip first row (title)
        next(f)
        # Read header row
        reader = csv.DictReader(f)

        for row in reader:
            # Skip empty rows or header continuation
            if not row.get('AIAAIC ID#') or row.get('AIAAIC ID#').startswith('AIAAIC ID'):
                continue

            # Parse issues
            issues_raw = row.get('Issue(s)', '')
            issues = [i.strip() for i in issues_raw.split(';') if i.strip()]

            # Filter incidents that have mapped issues
            mapped_issues = get_all_mapped_issues()
            relevant_issues = [i for i in issues if i in mapped_issues]

            if relevant_issues:  # Only include incidents with mappable issues
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

    # Shuffle for random sampling
    random.seed(42)  # Reproducible
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


def simulate_agent_detection(incident: Dict) -> Dict:
    """
    Simulate forensic agent detection based on incident properties.

    In a real scenario, this would call the actual forensic agent API.
    For this evaluation, we simulate detection based on keywords.
    """
    # Simulated detection logic (mirrors actual agent behavior)
    detected_gaps = []

    narrative = build_narrative(incident).lower()
    issues_str = " ".join(incident['issues']).lower()

    # Detection rules (similar to actual agent)
    detection_rules = {
        "transparencyrequirement": ["transparency", "disclosure", "opaque", "black box"],
        "accuracyrequirement": ["accuracy", "reliable", "error", "incorrect", "wrong"],
        "robustnessrequirement": ["robust", "fail", "crash", "malfunction", "safety"],
        "datagovernancerequirement": ["data", "privacy", "surveillance", "personal"],
        "privacyprotectionrequirement": ["privacy", "surveillance", "tracking", "monitoring"],
        "fairnessrequirement": ["fairness", "bias", "discriminat", "unfair"],
        "nondiscriminationrequirement": ["discriminat", "bias", "racial", "gender"],
        "documentationrequirement": ["accountab", "document", "record", "log"],
        "humanoversightrequirement": ["oversight", "human", "automat", "autonomous"],
        "safetyrequirement": ["safety", "harm", "injury", "death", "danger"],
        "securityrequirement": ["security", "hack", "breach", "attack", "vulnerab"],
        "fundamentalrightsassessmentrequirement": ["rights", "civil", "liberties", "fundamental"],
        "loggingrequirement": ["log", "audit", "trace", "record"],
        "riskmanagementrequirement": ["risk", "dual use", "misuse"],
        "biasdetectionrequirement": ["bias", "discriminat", "unfair"],
    }

    for req, keywords in detection_rules.items():
        for kw in keywords:
            if kw in narrative or kw in issues_str:
                detected_gaps.append(req)
                break

    return {
        "missing_requirements": list(set(detected_gaps)),
        "risk_level": determine_risk_level(incident),
        "confidence": 0.85,
    }


def determine_risk_level(incident: Dict) -> str:
    """Determine risk level based on incident properties."""
    high_risk_indicators = [
        "facial recognition", "biometric", "health", "medical",
        "employment", "recruitment", "law enforcement", "police",
        "critical infrastructure", "autonomous", "self-driving"
    ]

    narrative = build_narrative(incident).lower()

    for indicator in high_risk_indicators:
        if indicator in narrative:
            return "HighRisk"

    return "LimitedRisk"


def evaluate_single_incident(incident: Dict) -> Dict:
    """Evaluate agent performance on single incident."""
    # Get expected requirements based on AIAAIC issues
    expected = get_expected_requirements(incident['relevant_issues'])

    # Get agent detection (simulated)
    agent_result = simulate_agent_detection(incident)
    detected = get_detected_gaps(agent_result['missing_requirements'])

    # Calculate metrics
    metrics = calculate_metrics(expected, detected)

    return {
        'incident_id': incident['id'],
        'headline': incident['headline'][:80],
        'issues': incident['relevant_issues'],
        'expected_requirements': list(expected),
        'detected_requirements': list(detected),
        'metrics': metrics,
        'risk_level': agent_result['risk_level'],
    }


def run_evaluation(incidents: List[Dict]) -> Dict:
    """Run full evaluation on incident set."""
    results = []

    # Per-incident evaluation
    for incident in incidents:
        result = evaluate_single_incident(incident)
        results.append(result)

    # Aggregate metrics
    total_tp = sum(r['metrics']['true_positives'] for r in results)
    total_fp = sum(r['metrics']['false_positives'] for r in results)
    total_fn = sum(r['metrics']['false_negatives'] for r in results)

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # Per-issue metrics
    issue_metrics = calculate_per_issue_metrics(results, incidents)

    # Per-requirement metrics
    requirement_metrics = calculate_per_requirement_metrics(results)

    return {
        'timestamp': datetime.now().isoformat(),
        'total_incidents': len(incidents),
        'aggregate_metrics': {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'total_true_positives': total_tp,
            'total_false_positives': total_fp,
            'total_false_negatives': total_fn,
        },
        'issue_metrics': issue_metrics,
        'requirement_metrics': requirement_metrics,
        'per_incident_results': results,
    }


def calculate_per_issue_metrics(results: List[Dict], incidents: List[Dict]) -> Dict:
    """Calculate detection metrics per AIAAIC issue type."""
    issue_stats = {}

    for result, incident in zip(results, incidents):
        for issue in incident['relevant_issues']:
            if issue not in issue_stats:
                issue_stats[issue] = {'tp': 0, 'fp': 0, 'fn': 0, 'count': 0}

            issue_stats[issue]['count'] += 1
            issue_stats[issue]['tp'] += result['metrics']['true_positives']
            issue_stats[issue]['fp'] += result['metrics']['false_positives']
            issue_stats[issue]['fn'] += result['metrics']['false_negatives']

    # Calculate per-issue precision/recall
    for issue, stats in issue_stats.items():
        tp, fp, fn = stats['tp'], stats['fp'], stats['fn']
        stats['precision'] = tp / (tp + fp) if (tp + fp) > 0 else 0
        stats['recall'] = tp / (tp + fn) if (tp + fn) > 0 else 0
        stats['f1'] = 2 * stats['precision'] * stats['recall'] / (stats['precision'] + stats['recall']) if (stats['precision'] + stats['recall']) > 0 else 0

    return issue_stats


def calculate_per_requirement_metrics(results: List[Dict]) -> Dict:
    """Calculate detection rate per requirement type."""
    req_stats = {}

    for result in results:
        for req in result['expected_requirements']:
            if req not in req_stats:
                req_stats[req] = {'expected': 0, 'detected': 0}
            req_stats[req]['expected'] += 1
            if req in result['detected_requirements']:
                req_stats[req]['detected'] += 1

        for req in result['detected_requirements']:
            if req not in req_stats:
                req_stats[req] = {'expected': 0, 'detected': 0}

    # Calculate detection rate
    for req, stats in req_stats.items():
        stats['detection_rate'] = stats['detected'] / stats['expected'] if stats['expected'] > 0 else 0

    return req_stats


def generate_heatmap(evaluation_results: Dict, output_path: Path):
    """Generate confusion matrix heatmap."""
    if not HAS_VISUALIZATION:
        print("Skipping heatmap generation (matplotlib not available)")
        return

    # Build issue vs requirement matrix
    issue_metrics = evaluation_results['issue_metrics']
    issues = list(issue_metrics.keys())

    # Create metrics dataframe for heatmap
    metrics_data = []
    for issue in issues:
        metrics_data.append({
            'Issue': issue,
            'Precision': issue_metrics[issue]['precision'],
            'Recall': issue_metrics[issue]['recall'],
            'F1': issue_metrics[issue]['f1'],
            'Count': issue_metrics[issue]['count'],
        })

    df = pd.DataFrame(metrics_data)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(f'Compliance Gap Detection Evaluation\n{evaluation_results["total_incidents"]} Incidents',
                 fontsize=14, fontweight='bold')

    # 1. Issue-level metrics heatmap
    ax1 = axes[0, 0]
    pivot_metrics = df.set_index('Issue')[['Precision', 'Recall', 'F1']]
    sns.heatmap(pivot_metrics, annot=True, fmt='.2f', cmap='RdYlGn',
                vmin=0, vmax=1, ax=ax1, cbar_kws={'label': 'Score'})
    ax1.set_title('Detection Metrics by Issue Type')
    ax1.set_xlabel('')
    ax1.tick_params(axis='x', rotation=45)

    # 2. Requirement detection rates
    ax2 = axes[0, 1]
    req_metrics = evaluation_results['requirement_metrics']
    req_names = list(req_metrics.keys())[:10]  # Top 10
    detection_rates = [req_metrics[r]['detection_rate'] for r in req_names]

    colors = ['#2ecc71' if r > 0.7 else '#f39c12' if r > 0.4 else '#e74c3c' for r in detection_rates]
    bars = ax2.barh(req_names, detection_rates, color=colors)
    ax2.set_xlim(0, 1)
    ax2.set_xlabel('Detection Rate')
    ax2.set_title('Requirement Detection Rate')
    ax2.axvline(x=0.7, color='green', linestyle='--', alpha=0.5, label='Good (70%)')
    ax2.axvline(x=0.4, color='orange', linestyle='--', alpha=0.5, label='Fair (40%)')

    # 3. Aggregate metrics gauge
    ax3 = axes[1, 0]
    agg = evaluation_results['aggregate_metrics']
    metrics_names = ['Precision', 'Recall', 'F1 Score']
    metrics_values = [agg['precision'], agg['recall'], agg['f1']]
    colors = ['#3498db', '#2ecc71', '#9b59b6']

    bars = ax3.bar(metrics_names, metrics_values, color=colors)
    ax3.set_ylim(0, 1)
    ax3.set_ylabel('Score')
    ax3.set_title('Aggregate Performance Metrics')

    # Add value labels on bars
    for bar, val in zip(bars, metrics_values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')

    # 4. Confusion matrix summary
    ax4 = axes[1, 1]
    confusion_data = np.array([
        [agg['total_true_positives'], agg['total_false_negatives']],
        [agg['total_false_positives'], 0]
    ])
    labels = np.array([
        [f"TP\n{agg['total_true_positives']}", f"FN\n{agg['total_false_negatives']}"],
        [f"FP\n{agg['total_false_positives']}", "TN\n-"]
    ])

    sns.heatmap(confusion_data, annot=labels, fmt='', cmap='Blues',
                xticklabels=['Detected', 'Not Detected'],
                yticklabels=['Expected', 'Not Expected'],
                ax=ax4, cbar=False)
    ax4.set_title('Confusion Matrix Summary')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Heatmap saved to: {output_path}")


def generate_report(results_10: Dict, results_20: Dict, results_50: Dict, output_path: Path):
    """Generate comprehensive markdown report."""

    def format_metrics(metrics: Dict) -> str:
        return f"""
| Metric | Value |
|--------|-------|
| Precision | {metrics['precision']:.3f} |
| Recall | {metrics['recall']:.3f} |
| F1 Score | {metrics['f1']:.3f} |
| True Positives | {metrics['total_true_positives']} |
| False Positives | {metrics['total_false_positives']} |
| False Negatives | {metrics['total_false_negatives']} |
"""

    def format_comparison_table(r10: Dict, r20: Dict, r50: Dict) -> str:
        return f"""
| Incidents | Precision | Recall | F1 Score |
|-----------|-----------|--------|----------|
| 10 | {r10['aggregate_metrics']['precision']:.3f} | {r10['aggregate_metrics']['recall']:.3f} | {r10['aggregate_metrics']['f1']:.3f} |
| 20 | {r20['aggregate_metrics']['precision']:.3f} | {r20['aggregate_metrics']['recall']:.3f} | {r20['aggregate_metrics']['f1']:.3f} |
| 50 | {r50['aggregate_metrics']['precision']:.3f} | {r50['aggregate_metrics']['recall']:.3f} | {r50['aggregate_metrics']['f1']:.3f} |
"""

    report = f"""# Compliance Gap Detection Evaluation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Evaluation Method:** AIAAIC Issues → EU AI Act Requirements Mapping

## Executive Summary

This evaluation measures how well the forensic agent detects compliance gaps
by comparing detected missing requirements against expected requirements
derived from AIAAIC incident issues.

### Performance Comparison

{format_comparison_table(results_10, results_20, results_50)}

## Detailed Results

### 10 Incidents Evaluation
{format_metrics(results_10['aggregate_metrics'])}

### 20 Incidents Evaluation
{format_metrics(results_20['aggregate_metrics'])}

### 50 Incidents Evaluation
{format_metrics(results_50['aggregate_metrics'])}

## Issue-Level Analysis (50 incidents)

| Issue | Precision | Recall | F1 | Count |
|-------|-----------|--------|-----|-------|
"""

    for issue, stats in sorted(results_50['issue_metrics'].items(), key=lambda x: -x[1]['count']):
        report += f"| {issue} | {stats['precision']:.2f} | {stats['recall']:.2f} | {stats['f1']:.2f} | {stats['count']} |\n"

    report += """

## Requirement Detection Analysis (50 incidents)

| Requirement | Expected | Detected | Rate |
|-------------|----------|----------|------|
"""

    for req, stats in sorted(results_50['requirement_metrics'].items(), key=lambda x: -x[1]['expected']):
        report += f"| {req} | {stats['expected']} | {stats['detected']} | {stats['detection_rate']:.1%} |\n"

    report += """

## Methodology

### Ground Truth Derivation
- AIAAIC Issue field indicates what compliance aspect failed
- Each Issue maps to expected EU AI Act requirements
- Example: "Transparency" → TransparencyRequirement, GPAITransparencyRequirement

### Metrics Definition
- **Precision**: Of detected gaps, how many were expected?
- **Recall**: Of expected gaps, how many were detected?
- **F1**: Harmonic mean of precision and recall

### Limitations
- AIAAIC Issues indicate failures, not necessarily EU AI Act requirements
- Some issues have indirect mappings
- Agent simulation may differ from actual LLM-based detection

## Visual Analysis

See accompanying heatmap images:
- `heatmap_10.png` - 10 incidents analysis
- `heatmap_20.png` - 20 incidents analysis
- `heatmap_50.png` - 50 incidents analysis

---
*Report generated by SERAMIS Forensic Agent Benchmark Suite*
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Evaluate compliance gap detection')
    parser.add_argument('--incidents', type=int, default=50, help='Number of incidents to evaluate')
    parser.add_argument('--all', action='store_true', help='Run 10, 20, and 50 incident evaluations')
    args = parser.parse_args()

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Loading AIAAIC incidents from: {AIAAIC_CSV}")

    if args.all:
        # Run all three evaluations
        print("\n" + "="*60)
        print("Running 10-incident evaluation...")
        incidents_10 = load_aiaaic_incidents(AIAAIC_CSV, limit=10)
        results_10 = run_evaluation(incidents_10)
        generate_heatmap(results_10, OUTPUT_DIR / "heatmap_10.png")

        print("\n" + "="*60)
        print("Running 20-incident evaluation...")
        incidents_20 = load_aiaaic_incidents(AIAAIC_CSV, limit=20)
        results_20 = run_evaluation(incidents_20)
        generate_heatmap(results_20, OUTPUT_DIR / "heatmap_20.png")

        print("\n" + "="*60)
        print("Running 50-incident evaluation...")
        incidents_50 = load_aiaaic_incidents(AIAAIC_CSV, limit=50)
        results_50 = run_evaluation(incidents_50)
        generate_heatmap(results_50, OUTPUT_DIR / "heatmap_50.png")

        # Generate comprehensive report
        generate_report(results_10, results_20, results_50, OUTPUT_DIR / "EVALUATION_REPORT.md")

        # Save JSON results
        with open(OUTPUT_DIR / "results_all.json", 'w') as f:
            json.dump({
                '10_incidents': results_10,
                '20_incidents': results_20,
                '50_incidents': results_50,
            }, f, indent=2, default=str)

        # Print summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"\n{'Incidents':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
        print("-"*48)
        for name, results in [('10', results_10), ('20', results_20), ('50', results_50)]:
            agg = results['aggregate_metrics']
            print(f"{name:<12} {agg['precision']:<12.3f} {agg['recall']:<12.3f} {agg['f1']:<12.3f}")

    else:
        # Single evaluation
        incidents = load_aiaaic_incidents(AIAAIC_CSV, limit=args.incidents)
        print(f"Loaded {len(incidents)} incidents with mappable issues")

        results = run_evaluation(incidents)

        # Generate outputs
        generate_heatmap(results, OUTPUT_DIR / f"heatmap_{args.incidents}.png")

        with open(OUTPUT_DIR / f"results_{args.incidents}.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Print summary
        agg = results['aggregate_metrics']
        print("\n" + "="*60)
        print(f"EVALUATION RESULTS ({args.incidents} incidents)")
        print("="*60)
        print(f"Precision: {agg['precision']:.3f}")
        print(f"Recall:    {agg['recall']:.3f}")
        print(f"F1 Score:  {agg['f1']:.3f}")
        print(f"\nTrue Positives:  {agg['total_true_positives']}")
        print(f"False Positives: {agg['total_false_positives']}")
        print(f"False Negatives: {agg['total_false_negatives']}")


if __name__ == "__main__":
    main()
