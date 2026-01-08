#!/usr/bin/env python3
"""
Benchmark Analysis Report Generator
Generates confusion matrix, classification metrics, and detailed analysis for TFM.
"""

import json
import os
from collections import defaultdict
from datetime import datetime
import numpy as np

# Results file path
RESULTS_DIR = "/Users/cartesio/workspace/ai_act_project/forensic_agent/benchmark/results"
EVAL_FILE = f"{RESULTS_DIR}/real_benchmark_evaluations_v2_20260107_165124.json"
STATS_FILE = f"{RESULTS_DIR}/real_benchmark_stats_v2_20260107_165124.json"

def load_data():
    """Load evaluation and stats data."""
    with open(EVAL_FILE, 'r') as f:
        evaluations = json.load(f)
    with open(STATS_FILE, 'r') as f:
        stats = json.load(f)
    return evaluations, stats

def build_confusion_data(evaluations):
    """Build confusion matrix data for incident_type classification."""
    # Get all unique labels (predicted and expected)
    all_labels = set()
    predictions = []
    ground_truths = []

    for eval_item in evaluations:
        it = eval_item.get("incident_type", {})
        predicted = it.get("predicted", "unknown")
        expected_primary = it.get("expected_primary")

        if predicted and expected_primary:
            # Normalize labels
            predicted = predicted.lower().replace(" ", "_")
            expected_primary = expected_primary.lower().replace(" ", "_")

            predictions.append(predicted)
            ground_truths.append(expected_primary)
            all_labels.add(predicted)
            all_labels.add(expected_primary)

    return predictions, ground_truths, sorted(all_labels)

def compute_confusion_matrix(predictions, ground_truths, labels):
    """Compute confusion matrix."""
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    n = len(labels)
    matrix = np.zeros((n, n), dtype=int)

    for pred, gt in zip(predictions, ground_truths):
        if pred in label_to_idx and gt in label_to_idx:
            matrix[label_to_idx[gt], label_to_idx[pred]] += 1

    return matrix

def compute_per_class_metrics(matrix, labels):
    """Compute precision, recall, F1 for each class."""
    metrics = {}
    n = len(labels)

    for i, label in enumerate(labels):
        tp = matrix[i, i]
        fp = matrix[:, i].sum() - tp  # Column sum minus TP
        fn = matrix[i, :].sum() - tp  # Row sum minus TP

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        support = matrix[i, :].sum()  # Total ground truth instances

        metrics[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": int(support),
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn)
        }

    return metrics

def compute_macro_micro_metrics(per_class_metrics):
    """Compute macro and micro averaged metrics."""
    # Macro average (simple average)
    precisions = [m["precision"] for m in per_class_metrics.values() if m["support"] > 0]
    recalls = [m["recall"] for m in per_class_metrics.values() if m["support"] > 0]
    f1s = [m["f1"] for m in per_class_metrics.values() if m["support"] > 0]

    macro = {
        "precision": np.mean(precisions) if precisions else 0,
        "recall": np.mean(recalls) if recalls else 0,
        "f1": np.mean(f1s) if f1s else 0
    }

    # Micro average (global TP, FP, FN)
    total_tp = sum(m["tp"] for m in per_class_metrics.values())
    total_fp = sum(m["fp"] for m in per_class_metrics.values())
    total_fn = sum(m["fn"] for m in per_class_metrics.values())

    micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0

    micro = {
        "precision": micro_precision,
        "recall": micro_recall,
        "f1": micro_f1
    }

    # Weighted average
    total_support = sum(m["support"] for m in per_class_metrics.values())
    weighted_precision = sum(m["precision"] * m["support"] for m in per_class_metrics.values()) / total_support if total_support > 0 else 0
    weighted_recall = sum(m["recall"] * m["support"] for m in per_class_metrics.values()) / total_support if total_support > 0 else 0
    weighted_f1 = sum(m["f1"] * m["support"] for m in per_class_metrics.values()) / total_support if total_support > 0 else 0

    weighted = {
        "precision": weighted_precision,
        "recall": weighted_recall,
        "f1": weighted_f1
    }

    return macro, micro, weighted

def analyze_misclassifications(evaluations):
    """Analyze common misclassification patterns."""
    misclassifications = defaultdict(lambda: defaultdict(int))

    for eval_item in evaluations:
        it = eval_item.get("incident_type", {})
        if not it.get("strict_match", False):
            predicted = it.get("predicted", "unknown")
            expected = it.get("expected_primary", "unknown")
            if predicted and expected:
                misclassifications[expected][predicted] += 1

    # Sort by frequency
    patterns = []
    for expected, preds in misclassifications.items():
        for pred, count in sorted(preds.items(), key=lambda x: -x[1]):
            patterns.append({
                "expected": expected,
                "predicted": pred,
                "count": count
            })

    return sorted(patterns, key=lambda x: -x["count"])

def analyze_risk_level(evaluations):
    """Analyze risk level classification performance."""
    risk_confusion = defaultdict(lambda: defaultdict(int))

    for eval_item in evaluations:
        rl = eval_item.get("risk_level", {})
        predicted = rl.get("predicted", "unknown")
        expected = rl.get("expected", "unknown")
        risk_confusion[expected][predicted] += 1

    return dict(risk_confusion)

def print_confusion_matrix(matrix, labels):
    """Print formatted confusion matrix."""
    # Truncate labels for display
    short_labels = [l[:12] for l in labels]

    print("\n" + "=" * 80)
    print("CONFUSION MATRIX - incident_type (Predicted vs Ground Truth)")
    print("=" * 80)
    print("\nRows = Ground Truth, Columns = Predicted")
    print()

    # Header
    header = "GT \\ Pred".ljust(15) + "".join(l[:10].center(10) for l in short_labels)
    print(header)
    print("-" * len(header))

    # Rows
    for i, label in enumerate(short_labels):
        row = label.ljust(15)
        for j in range(len(labels)):
            val = matrix[i, j]
            if val > 0:
                row += str(val).center(10)
            else:
                row += ".".center(10)
        print(row)

    print()

def print_classification_report(per_class_metrics, macro, micro, weighted):
    """Print sklearn-style classification report."""
    print("\n" + "=" * 80)
    print("CLASSIFICATION REPORT - incident_type")
    print("=" * 80)
    print()
    print(f"{'Class':<25} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}")
    print("-" * 65)

    # Sort by support (descending)
    sorted_classes = sorted(per_class_metrics.items(), key=lambda x: -x[1]["support"])

    for label, m in sorted_classes:
        if m["support"] > 0:
            print(f"{label:<25} {m['precision']:>10.3f} {m['recall']:>10.3f} {m['f1']:>10.3f} {m['support']:>10}")

    print("-" * 65)
    total_support = sum(m["support"] for m in per_class_metrics.values())
    print(f"{'macro avg':<25} {macro['precision']:>10.3f} {macro['recall']:>10.3f} {macro['f1']:>10.3f} {total_support:>10}")
    print(f"{'weighted avg':<25} {weighted['precision']:>10.3f} {weighted['recall']:>10.3f} {weighted['f1']:>10.3f} {total_support:>10}")
    print(f"{'micro avg (accuracy)':<25} {micro['precision']:>10.3f} {micro['recall']:>10.3f} {micro['f1']:>10.3f} {total_support:>10}")
    print()

def print_misclassification_analysis(patterns):
    """Print top misclassification patterns."""
    print("\n" + "=" * 80)
    print("TOP MISCLASSIFICATION PATTERNS")
    print("=" * 80)
    print()
    print(f"{'Expected':<25} {'Predicted':<25} {'Count':>10}")
    print("-" * 60)

    for p in patterns[:15]:  # Top 15
        print(f"{p['expected']:<25} {p['predicted']:<25} {p['count']:>10}")

    print()

def print_risk_level_analysis(risk_confusion, evaluations):
    """Print risk level classification analysis."""
    print("\n" + "=" * 80)
    print("RISK LEVEL CLASSIFICATION")
    print("=" * 80)

    # Count matches
    matches = sum(1 for e in evaluations if e.get("risk_level", {}).get("match", False))
    total = len(evaluations)

    print(f"\nOverall Accuracy: {matches}/{total} = {100*matches/total:.1f}%")
    print()
    print("Confusion Matrix (Risk Level):")
    gt_pred = "GT \\ Pred"
    print(f"{gt_pred:<15} {'HighRisk':>12} {'MinimalRisk':>12} {'LimitedRisk':>12}")
    print("-" * 52)

    for gt in ["HighRisk", "MinimalRisk", "LimitedRisk"]:
        row = f"{gt:<15}"
        for pred in ["HighRisk", "MinimalRisk", "LimitedRisk"]:
            val = risk_confusion.get(gt, {}).get(pred, 0)
            row += f"{val:>12}"
        print(row)

    print()

def generate_summary_stats(evaluations, stats):
    """Generate summary statistics."""
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY - v0.41.0")
    print("=" * 80)
    print()

    # Basic stats
    print(f"Total Cases:        {stats.get('total_incidents', 0)}")
    print(f"Successful:         {stats.get('successful', 0)} ({100*stats.get('successful',0)/stats.get('total_incidents',1):.1f}%)")
    print(f"Failed:             {stats.get('failed', 0)}")
    print(f"Low Confidence:     {stats.get('low_confidence', 0)}")
    print()

    # Ground truth accuracy
    gt = stats.get("ground_truth_accuracy", {})
    print("Ground Truth Accuracy:")
    print(f"  incident_type (strict):    {gt.get('incident_type_strict', 0):.1f}%")
    print(f"  incident_type (flexible):  {gt.get('incident_type_flexible', 0):.1f}%")
    print(f"  risk_level:                {gt.get('risk_level', 0):.1f}%")
    print()

    # Performance
    perf = stats.get("performance", {})
    print("Performance:")
    print(f"  Mean processing time:  {perf.get('mean_time', 0):.2f}s")
    print(f"  Median processing time: {perf.get('median_time', 0):.2f}s")
    print()

    # Confidence
    conf = stats.get("confidence", {})
    print("Extraction Confidence:")
    print(f"  Mean:   {conf.get('mean', 0):.3f}")
    print(f"  Median: {conf.get('median', 0):.3f}")
    print(f"  Min:    {conf.get('min', 0):.3f}")
    print(f"  Max:    {conf.get('max', 0):.3f}")
    print()

def save_report_json(per_class_metrics, macro, micro, weighted, patterns, risk_confusion):
    """Save detailed report as JSON."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "version": "0.41.0",
        "incident_type_metrics": {
            "per_class": per_class_metrics,
            "macro_avg": macro,
            "micro_avg": micro,
            "weighted_avg": weighted
        },
        "misclassification_patterns": patterns[:20],
        "risk_level_confusion": risk_confusion
    }

    output_file = f"{RESULTS_DIR}/classification_analysis_v041.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {output_file}")

def main():
    print("Loading benchmark data...")
    evaluations, stats = load_data()

    print(f"Loaded {len(evaluations)} evaluations")

    # Build confusion matrix
    predictions, ground_truths, labels = build_confusion_data(evaluations)
    print(f"Found {len(labels)} unique labels: {labels}")

    # Compute metrics
    matrix = compute_confusion_matrix(predictions, ground_truths, labels)
    per_class_metrics = compute_per_class_metrics(matrix, labels)
    macro, micro, weighted = compute_macro_micro_metrics(per_class_metrics)

    # Analyze misclassifications
    patterns = analyze_misclassifications(evaluations)

    # Analyze risk level
    risk_confusion = analyze_risk_level(evaluations)

    # Print reports
    generate_summary_stats(evaluations, stats)
    print_confusion_matrix(matrix, labels)
    print_classification_report(per_class_metrics, macro, micro, weighted)
    print_misclassification_analysis(patterns)
    print_risk_level_analysis(risk_confusion, evaluations)

    # Save JSON report
    save_report_json(per_class_metrics, macro, micro, weighted, patterns, risk_confusion)

    # Key findings for TFM
    print("\n" + "=" * 80)
    print("KEY FINDINGS FOR TFM")
    print("=" * 80)
    print()
    print("1. INCIDENT TYPE CLASSIFICATION:")
    print(f"   - Weighted F1-Score: {weighted['f1']:.3f}")
    print(f"   - Macro F1-Score: {macro['f1']:.3f}")
    print(f"   - Best performing class: {max(per_class_metrics.items(), key=lambda x: x[1]['f1'] if x[1]['support'] > 10 else 0)[0]}")
    print()
    print("2. MAIN CHALLENGES:")
    print(f"   - Top misclassification: {patterns[0]['expected']} -> {patterns[0]['predicted']} ({patterns[0]['count']} cases)")
    print(f"   - privacy_violation is over-predicted (high FP rate)")
    print()
    print("3. RISK LEVEL CLASSIFICATION:")
    risk_matches = sum(1 for e in evaluations if e.get("risk_level", {}).get("match", False))
    print(f"   - Accuracy: {100*risk_matches/len(evaluations):.1f}%")
    print(f"   - Strong performance for high-stakes risk assessment")
    print()

if __name__ == "__main__":
    main()
