#!/usr/bin/env python3
"""
Synthetic Benchmark Classification Evaluation

Evaluates incident type and risk level classification using ground truth
from synthetic benchmark templates.

Date: December 2025
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_recall_fscore_support,
    accuracy_score
)

# Paths
BENCHMARK_DIR = Path(__file__).parent
RESULTS_DIR = BENCHMARK_DIR / "results"


def load_synthetic_results(results_file: Path) -> Tuple[List[Dict], List[Dict]]:
    """
    Load synthetic benchmark results with ground truth.

    Returns:
        Tuple of (incident_type_data, risk_level_data)
        Each contains dicts with 'expected' and 'predicted' keys
    """
    with open(results_file) as f:
        data = json.load(f)

    incident_data = []
    risk_data = []

    for r in data:
        if r.get('status') != 'COMPLETED':
            continue

        # Ground truth
        exp_type = r.get('expected_incident_type') or r.get('metadata', {}).get('template_type')
        exp_risk = r.get('expected_risk_level') or r.get('metadata', {}).get('expected_risk_level')

        # Predictions
        pred_type = r.get('extraction', {}).get('incident', {}).get('incident_type')
        pred_risk = r.get('eu_ai_act', {}).get('risk_level')

        incident_id = r.get('incident_id', 'unknown')

        if exp_type and pred_type:
            incident_data.append({
                'id': incident_id,
                'expected': exp_type,
                'predicted': pred_type,
                'match': exp_type == pred_type
            })

        if exp_risk and pred_risk:
            risk_data.append({
                'id': incident_id,
                'expected': exp_risk,
                'predicted': pred_risk,
                'match': exp_risk == pred_risk
            })

    return incident_data, risk_data


def generate_confusion_matrix_plot(
    y_true: List[str],
    y_pred: List[str],
    title: str,
    output_path: Path
) -> np.ndarray:
    """Generate and save confusion matrix visualization."""

    # Get all unique labels
    all_labels = sorted(set(y_true) | set(y_pred))

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=all_labels)

    # Create visualization
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=all_labels,
        yticklabels=all_labels
    )
    plt.xlabel('Predicted')
    plt.ylabel('Expected (Ground Truth)')
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    plt.savefig(output_path, dpi=150)
    print(f"  Saved: {output_path.name}")
    plt.close()

    return cm


def compute_metrics(y_true: List[str], y_pred: List[str]) -> Dict:
    """Compute classification metrics."""

    labels = sorted(set(y_true) | set(y_pred))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )

    accuracy = accuracy_score(y_true, y_pred)

    report = {
        "accuracy": accuracy,
        "macro_avg": {
            "precision": float(np.mean(precision)),
            "recall": float(np.mean(recall)),
            "f1": float(np.mean(f1))
        },
        "weighted_avg": {
            "precision": float(np.average(precision, weights=support)) if sum(support) > 0 else 0,
            "recall": float(np.average(recall, weights=support)) if sum(support) > 0 else 0,
            "f1": float(np.average(f1, weights=support)) if sum(support) > 0 else 0
        },
        "per_class": {}
    }

    for i, label in enumerate(labels):
        report["per_class"][label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i])
        }

    return report


def print_metrics_table(report: Dict, title: str):
    """Print metrics in a formatted table."""

    print(f"\n{title}")
    print("=" * 70)

    print(f"\nOverall Accuracy: {report['accuracy']:.1%}")

    print(f"\nMacro Average:")
    print(f"  Precision: {report['macro_avg']['precision']:.3f}")
    print(f"  Recall:    {report['macro_avg']['recall']:.3f}")
    print(f"  F1-Score:  {report['macro_avg']['f1']:.3f}")

    print(f"\nWeighted Average:")
    print(f"  Precision: {report['weighted_avg']['precision']:.3f}")
    print(f"  Recall:    {report['weighted_avg']['recall']:.3f}")
    print(f"  F1-Score:  {report['weighted_avg']['f1']:.3f}")

    print(f"\nPer-Class Metrics:")
    print(f"  {'Class':<22} {'Prec':>8} {'Recall':>8} {'F1':>8} {'Support':>8}")
    print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    # Sort by support (descending)
    sorted_classes = sorted(
        report["per_class"].items(),
        key=lambda x: -x[1]['support']
    )

    for label, metrics in sorted_classes:
        print(f"  {label:<22} {metrics['precision']:>8.3f} {metrics['recall']:>8.3f} {metrics['f1']:>8.3f} {metrics['support']:>8}")


def analyze_misclassifications(data: List[Dict], label: str = "incident type"):
    """Analyze patterns in misclassifications."""

    mismatches = [d for d in data if not d['match']]

    if not mismatches:
        print(f"\n  No misclassifications for {label}!")
        return

    print(f"\n  Misclassifications ({len(mismatches)}):")

    # Group by expected -> predicted
    patterns = Counter((d['expected'], d['predicted']) for d in mismatches)

    print(f"  {'Expected':<22} → {'Predicted':<22} {'Count':>6}")
    print(f"  {'-'*22}   {'-'*22} {'-'*6}")

    for (exp, pred), count in patterns.most_common(10):
        print(f"  {exp:<22} → {pred:<22} {count:>6}")


def evaluate_synthetic_benchmark(results_file: Path, output_dir: Path = None):
    """
    Full evaluation of synthetic benchmark results.
    """
    print("=" * 70)
    print("SYNTHETIC BENCHMARK CLASSIFICATION EVALUATION")
    print("=" * 70)

    if output_dir is None:
        output_dir = RESULTS_DIR
    output_dir.mkdir(exist_ok=True)

    # Load data
    print(f"\nLoading results from: {results_file.name}")
    incident_data, risk_data = load_synthetic_results(results_file)

    print(f"  Incidents with type ground truth: {len(incident_data)}")
    print(f"  Incidents with risk ground truth: {len(risk_data)}")

    # Extract timestamp for output files
    timestamp = results_file.stem.split('_')[-1] if '_' in results_file.stem else 'latest'

    # =========================================================================
    # 1. INCIDENT TYPE CLASSIFICATION
    # =========================================================================
    print("\n" + "-" * 70)
    print("1. INCIDENT TYPE CLASSIFICATION")
    print("-" * 70)

    y_true_type = [d['expected'] for d in incident_data]
    y_pred_type = [d['predicted'] for d in incident_data]

    # Metrics
    type_metrics = compute_metrics(y_true_type, y_pred_type)
    print_metrics_table(type_metrics, "Incident Type Classification Metrics")

    # Confusion matrix
    print("\nGenerating confusion matrix...")
    cm_type_path = output_dir / f"confusion_matrix_incident_type_{timestamp}.png"
    generate_confusion_matrix_plot(
        y_true_type, y_pred_type,
        "Confusion Matrix: Incident Type Classification\n(Synthetic Benchmark - Ground Truth vs Predictions)",
        cm_type_path
    )

    # Misclassification analysis
    analyze_misclassifications(incident_data, "incident type")

    # =========================================================================
    # 2. RISK LEVEL CLASSIFICATION
    # =========================================================================
    print("\n" + "-" * 70)
    print("2. RISK LEVEL CLASSIFICATION (EU AI Act)")
    print("-" * 70)

    y_true_risk = [d['expected'] for d in risk_data]
    y_pred_risk = [d['predicted'] for d in risk_data]

    # Metrics
    risk_metrics = compute_metrics(y_true_risk, y_pred_risk)
    print_metrics_table(risk_metrics, "Risk Level Classification Metrics")

    # Confusion matrix
    print("\nGenerating confusion matrix...")
    cm_risk_path = output_dir / f"confusion_matrix_risk_level_{timestamp}.png"
    generate_confusion_matrix_plot(
        y_true_risk, y_pred_risk,
        "Confusion Matrix: EU AI Act Risk Level Classification\n(Synthetic Benchmark - Ground Truth vs Predictions)",
        cm_risk_path
    )

    # Misclassification analysis
    analyze_misclassifications(risk_data, "risk level")

    # =========================================================================
    # 3. SAVE FULL REPORT
    # =========================================================================
    full_report = {
        "results_file": str(results_file),
        "n_incidents_type": len(incident_data),
        "n_incidents_risk": len(risk_data),
        "incident_type_classification": {
            "accuracy": type_metrics["accuracy"],
            "metrics": type_metrics
        },
        "risk_level_classification": {
            "accuracy": risk_metrics["accuracy"],
            "metrics": risk_metrics
        },
        "ground_truth_distribution": {
            "incident_types": dict(Counter(y_true_type)),
            "risk_levels": dict(Counter(y_true_risk))
        },
        "prediction_distribution": {
            "incident_types": dict(Counter(y_pred_type)),
            "risk_levels": dict(Counter(y_pred_risk))
        }
    }

    report_path = output_dir / f"synthetic_classification_report_{timestamp}.json"
    with open(report_path, 'w') as f:
        json.dump(full_report, f, indent=2)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n  Incident Type Accuracy:  {type_metrics['accuracy']:.1%}")
    print(f"  Risk Level Accuracy:     {risk_metrics['accuracy']:.1%}")
    print(f"\n  Full report saved to: {report_path.name}")
    print("=" * 70)

    return full_report


def main():
    """Main entry point."""
    import sys

    # Find latest results file or use argument
    if len(sys.argv) > 1:
        results_file = Path(sys.argv[1])
    else:
        # Find latest synthetic benchmark results (not real)
        results_files = list(RESULTS_DIR.glob("benchmark_results_v1_*.json"))
        # Exclude real benchmark files
        results_files = [f for f in results_files if not f.name.startswith("real_")]

        if not results_files:
            print("No synthetic benchmark results found in:", RESULTS_DIR)
            sys.exit(1)

        results_file = max(results_files, key=lambda p: p.stat().st_mtime)
        print(f"Using latest results: {results_file.name}")

    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        sys.exit(1)

    evaluate_synthetic_benchmark(results_file)


if __name__ == "__main__":
    main()
