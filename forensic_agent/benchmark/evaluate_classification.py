#!/usr/bin/env python3
"""
Classification Evaluation Module

Evaluates incident type classification using AIAAIC ground truth
with semantic mapping based on ontology alignment.

Date: December 2025
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
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
DATA_DIR = BENCHMARK_DIR / "data"
AIAAIC_CSV = DATA_DIR / "AIAAIC Repository - Incidents.csv"

# =============================================================================
# SEMANTIC MAPPING: AIAAIC Issues → Our Taxonomy
# =============================================================================
# Based on ontology alignment and EU AI Act categories

AIAAIC_TO_TAXONOMY = {
    # Direct mappings
    "Privacy/surveillance": "privacy_violation",
    "Privacy": "privacy_violation",
    "Safety": "safety_failure",
    "Transparency": "transparency_failure",
    "Copyright": "copyright",

    # Semantic mappings (based on definitions)
    "Fairness": "bias",                      # Algorithmic bias → unfair outcomes
    "Accuracy/reliability": "safety_failure", # Accuracy failures cause harm
    "Mis/disinformation": "Mis/disinformation",  # Keep as separate category
    "Security": "adversarial_attack",        # Security breaches
    "Accountability": "transparency_failure", # Lack of accountability = transparency issue
    "Human rights/civil liberties": "discrimination",  # Rights violations
    "Cheating/plagiarism": "appropriation",  # Unauthorized content use
    "Authenticity/integrity": "Mis/disinformation",  # Fake content

    # Secondary mappings
    "Employment": "discrimination",          # Employment discrimination
    "Dual use": "safety_failure",            # Dual use = safety concern
    "Dual/multi-use": "safety_failure",
    "Alignment": "safety_failure",           # AI alignment failures
    "Ethics/values": "bias",                 # Ethical issues often manifest as bias
    "Environment": "safety_failure",         # Environmental harm
    "Anthropomorphism": "transparency_failure",  # Misleading about AI nature
}

# Our taxonomy categories (for classification)
OUR_TAXONOMY = [
    "privacy_violation",
    "bias",
    "safety_failure",
    "transparency_failure",
    "discrimination",
    "copyright",
    "appropriation",
    "adversarial_attack",
    "data_leakage",
    "Mis/disinformation",
    "other"
]


def load_aiaaic_ground_truth() -> Dict[str, List[str]]:
    """
    Load AIAAIC data and extract ground truth labels.
    Returns dict mapping incident_id -> list of mapped taxonomy labels
    """
    df = pd.read_csv(AIAAIC_CSV, skiprows=1)

    ground_truth = {}

    for _, row in df.iterrows():
        incident_id = str(row.get('AIAAIC ID#', '')).strip()
        if not incident_id:
            continue

        issues_raw = str(row.get('Issue(s)', '')).strip()
        if not issues_raw or issues_raw == 'nan':
            continue

        # Split multi-value issues and map each
        issues = [i.strip() for i in issues_raw.split(';')]
        mapped_labels = []

        for issue in issues:
            if issue in AIAAIC_TO_TAXONOMY:
                mapped_labels.append(AIAAIC_TO_TAXONOMY[issue])
            # else: unmapped issues are ignored

        if mapped_labels:
            # Remove duplicates while preserving order
            seen = set()
            unique_labels = []
            for label in mapped_labels:
                if label not in seen:
                    seen.add(label)
                    unique_labels.append(label)
            ground_truth[incident_id] = unique_labels

    return ground_truth


def load_benchmark_predictions(results_file: Path) -> Dict[str, str]:
    """
    Load predictions from benchmark results JSON.
    Returns dict mapping incident_id -> predicted incident_type
    """
    with open(results_file) as f:
        data = json.load(f)

    predictions = {}

    # Handle both list format and dict with "results" key
    results_list = data if isinstance(data, list) else data.get("results", [])

    for result in results_list:
        # Get incident_id from various possible locations
        incident_id = result.get("incident_id", "")
        if not incident_id:
            metadata = result.get("metadata", {})
            incident_id = metadata.get("aiaaic_id", "")

        # Accept both SUCCESS and COMPLETED status
        if result.get("status") not in ("SUCCESS", "COMPLETED"):
            continue

        extraction = result.get("extraction", {})
        incident = extraction.get("incident", {})
        incident_type = incident.get("incident_type", "other")

        # Normalize incident_id format
        if incident_id.startswith("AIAAIC"):
            predictions[incident_id] = incident_type

    return predictions


def compute_primary_label_match(
    ground_truth: Dict[str, List[str]],
    predictions: Dict[str, str]
) -> Tuple[List[str], List[str], List[str]]:
    """
    Compare predictions against PRIMARY ground truth label.

    Returns: (y_true, y_pred, incident_ids)
    """
    y_true = []
    y_pred = []
    incident_ids = []

    for incident_id, true_labels in ground_truth.items():
        if incident_id not in predictions:
            continue

        # Use first (primary) label as ground truth
        primary_label = true_labels[0]
        predicted_label = predictions[incident_id]

        # Normalize to our taxonomy
        if predicted_label not in OUR_TAXONOMY:
            predicted_label = "other"

        y_true.append(primary_label)
        y_pred.append(predicted_label)
        incident_ids.append(incident_id)

    return y_true, y_pred, incident_ids


def compute_any_label_match(
    ground_truth: Dict[str, List[str]],
    predictions: Dict[str, str]
) -> Tuple[int, int, float]:
    """
    Check if prediction matches ANY of the ground truth labels.
    More lenient evaluation for multi-label ground truth.

    Returns: (matches, total, accuracy)
    """
    matches = 0
    total = 0

    for incident_id, true_labels in ground_truth.items():
        if incident_id not in predictions:
            continue

        total += 1
        predicted = predictions[incident_id]

        if predicted in true_labels:
            matches += 1

    accuracy = matches / total if total > 0 else 0
    return matches, total, accuracy


def generate_confusion_matrix(
    y_true: List[str],
    y_pred: List[str],
    output_path: Optional[Path] = None
) -> np.ndarray:
    """
    Generate and optionally save confusion matrix visualization.
    """
    # Get unique labels present in data
    all_labels = sorted(set(y_true) | set(y_pred))

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=all_labels)

    # Create visualization
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=all_labels,
        yticklabels=all_labels
    )
    plt.xlabel('Predicted')
    plt.ylabel('Ground Truth (AIAAIC)')
    plt.title('Confusion Matrix: Incident Type Classification\n(AIAAIC Ground Truth vs Forensic Agent Predictions)')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Confusion matrix saved to: {output_path}")

    plt.close()

    return cm


def generate_classification_report(
    y_true: List[str],
    y_pred: List[str]
) -> Dict:
    """
    Generate detailed classification metrics.
    """
    # Get labels present in data
    labels = sorted(set(y_true) | set(y_pred))

    # Compute metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )

    accuracy = accuracy_score(y_true, y_pred)

    # Build report dict
    report = {
        "accuracy": accuracy,
        "macro_avg": {
            "precision": np.mean(precision),
            "recall": np.mean(recall),
            "f1": np.mean(f1)
        },
        "weighted_avg": {},
        "per_class": {}
    }

    # Weighted averages
    total_support = sum(support)
    if total_support > 0:
        report["weighted_avg"] = {
            "precision": np.average(precision, weights=support),
            "recall": np.average(recall, weights=support),
            "f1": np.average(f1, weights=support)
        }

    # Per-class metrics
    for i, label in enumerate(labels):
        report["per_class"][label] = {
            "precision": precision[i],
            "recall": recall[i],
            "f1": f1[i],
            "support": int(support[i])
        }

    return report


def evaluate_benchmark_results(results_file: Path, output_dir: Path = None):
    """
    Full evaluation of benchmark results against AIAAIC ground truth.
    """
    print("=" * 70)
    print("CLASSIFICATION EVALUATION")
    print("=" * 70)
    print()

    # Set output directory
    if output_dir is None:
        output_dir = RESULTS_DIR
    output_dir.mkdir(exist_ok=True)

    # Load data
    print("Loading AIAAIC ground truth...")
    ground_truth = load_aiaaic_ground_truth()
    print(f"  Loaded {len(ground_truth)} incidents with mapped labels")

    print(f"\nLoading predictions from: {results_file.name}")
    predictions = load_benchmark_predictions(results_file)
    print(f"  Loaded {len(predictions)} successful predictions")

    # Find overlap
    common_ids = set(ground_truth.keys()) & set(predictions.keys())
    print(f"\n  Incidents with both GT and predictions: {len(common_ids)}")

    if len(common_ids) == 0:
        print("ERROR: No common incidents found!")
        return None

    # Compute metrics
    print("\n" + "-" * 70)
    print("EVALUATION METRICS")
    print("-" * 70)

    # 1. Primary label match (strict)
    y_true, y_pred, ids = compute_primary_label_match(ground_truth, predictions)

    print(f"\n1. PRIMARY LABEL MATCH (Strict)")
    print(f"   Comparing against first AIAAIC issue")

    accuracy = accuracy_score(y_true, y_pred)
    print(f"   Accuracy: {accuracy:.1%}")

    # 2. Any label match (lenient)
    matches, total, any_accuracy = compute_any_label_match(ground_truth, predictions)
    print(f"\n2. ANY LABEL MATCH (Lenient)")
    print(f"   Prediction matches any of the AIAAIC issues")
    print(f"   Accuracy: {any_accuracy:.1%} ({matches}/{total})")

    # 3. Classification report
    print(f"\n3. CLASSIFICATION REPORT (Primary Label)")
    report = generate_classification_report(y_true, y_pred)

    print(f"\n   Overall Accuracy: {report['accuracy']:.1%}")
    print(f"\n   Macro Average:")
    print(f"     Precision: {report['macro_avg']['precision']:.3f}")
    print(f"     Recall:    {report['macro_avg']['recall']:.3f}")
    print(f"     F1-Score:  {report['macro_avg']['f1']:.3f}")

    print(f"\n   Weighted Average:")
    print(f"     Precision: {report['weighted_avg']['precision']:.3f}")
    print(f"     Recall:    {report['weighted_avg']['recall']:.3f}")
    print(f"     F1-Score:  {report['weighted_avg']['f1']:.3f}")

    print(f"\n   Per-Class Metrics:")
    print(f"   {'Class':<25} {'Prec':>8} {'Recall':>8} {'F1':>8} {'Support':>8}")
    print(f"   {'-'*25} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    for label, metrics in sorted(report["per_class"].items(), key=lambda x: -x[1]['support']):
        print(f"   {label:<25} {metrics['precision']:>8.3f} {metrics['recall']:>8.3f} {metrics['f1']:>8.3f} {metrics['support']:>8}")

    # 4. Generate confusion matrix
    print("\n" + "-" * 70)
    print("GENERATING VISUALIZATIONS")
    print("-" * 70)

    timestamp = results_file.stem.split('_')[-1] if '_' in results_file.stem else 'latest'
    cm_path = output_dir / f"confusion_matrix_{timestamp}.png"
    generate_confusion_matrix(y_true, y_pred, cm_path)

    # 5. Save full report
    full_report = {
        "results_file": str(results_file),
        "n_ground_truth": len(ground_truth),
        "n_predictions": len(predictions),
        "n_evaluated": len(common_ids),
        "primary_label_accuracy": accuracy,
        "any_label_accuracy": any_accuracy,
        "classification_report": report,
        "mapping_used": AIAAIC_TO_TAXONOMY
    }

    report_path = output_dir / f"classification_report_{timestamp}.json"
    with open(report_path, 'w') as f:
        json.dump(full_report, f, indent=2)
    print(f"\nFull report saved to: {report_path}")

    print("\n" + "=" * 70)

    return full_report


def main():
    """Main entry point."""
    import sys

    # Find latest results file or use argument
    if len(sys.argv) > 1:
        results_file = Path(sys.argv[1])
    else:
        # Find latest real benchmark results
        results_files = list(RESULTS_DIR.glob("real_benchmark_results_v1_*.json"))
        if not results_files:
            print("No benchmark results found in:", RESULTS_DIR)
            sys.exit(1)
        results_file = max(results_files, key=lambda p: p.stat().st_mtime)
        print(f"Using latest results: {results_file.name}")

    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        sys.exit(1)

    evaluate_benchmark_results(results_file)


if __name__ == "__main__":
    main()
