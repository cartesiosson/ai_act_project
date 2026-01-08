#!/usr/bin/env python3
"""
Generate visual confusion matrix for incident_type classification.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from collections import defaultdict

# Results file path
RESULTS_DIR = "/Users/cartesio/workspace/ai_act_project/forensic_agent/benchmark/results"
EVAL_FILE = f"{RESULTS_DIR}/real_benchmark_evaluations_v2_20260107_165124.json"

def load_evaluations():
    with open(EVAL_FILE, 'r') as f:
        return json.load(f)

def build_confusion_data(evaluations):
    """Build confusion matrix focusing on main categories."""
    # Main categories to analyze (filtering out rare ones)
    main_categories = [
        'privacy_violation',
        'safety_failure',
        'bias',
        'accuracy_failure',
        'transparency_failure',
        'misinformation',
        'copyright'
    ]

    predictions = []
    ground_truths = []

    for eval_item in evaluations:
        it = eval_item.get("incident_type", {})
        predicted = it.get("predicted", "")
        expected_primary = it.get("expected_primary", "")

        if predicted and expected_primary:
            predicted = predicted.lower().replace(" ", "_")
            expected_primary = expected_primary.lower().replace(" ", "_")

            # Only include if both are in main categories
            if expected_primary in main_categories:
                if predicted not in main_categories:
                    predicted = "other"
                predictions.append(predicted)
                ground_truths.append(expected_primary)

    return predictions, ground_truths, main_categories + ["other"]

def compute_confusion_matrix(predictions, ground_truths, labels):
    """Compute confusion matrix."""
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    n = len(labels)
    matrix = np.zeros((n, n), dtype=int)

    for pred, gt in zip(predictions, ground_truths):
        if gt in label_to_idx:
            pred_idx = label_to_idx.get(pred, label_to_idx.get("other", n-1))
            matrix[label_to_idx[gt], pred_idx] += 1

    return matrix

def plot_confusion_matrix(matrix, labels, output_path):
    """Create and save confusion matrix heatmap."""
    # Short labels for display
    short_labels = {
        'privacy_violation': 'Privacy',
        'safety_failure': 'Safety',
        'bias': 'Bias',
        'accuracy_failure': 'Accuracy',
        'transparency_failure': 'Transparency',
        'misinformation': 'Misinfo',
        'copyright': 'Copyright',
        'other': 'Other'
    }
    display_labels = [short_labels.get(l, l) for l in labels]

    fig, ax = plt.subplots(figsize=(12, 10))

    # Normalize by row (to show recall per class)
    row_sums = matrix.sum(axis=1, keepdims=True)
    matrix_normalized = np.divide(matrix, row_sums, where=row_sums!=0)

    # Create heatmap
    im = ax.imshow(matrix_normalized, cmap='Blues', aspect='auto', vmin=0, vmax=1)

    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Proportion (Recall)', fontsize=12)

    # Set ticks
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(display_labels, fontsize=11, rotation=45, ha='right')
    ax.set_yticklabels(display_labels, fontsize=11)

    # Labels
    ax.set_xlabel('Predicted', fontsize=14, fontweight='bold')
    ax.set_ylabel('Ground Truth (AIAAIC)', fontsize=14, fontweight='bold')
    ax.set_title('Confusion Matrix - incident_type Classification\n(Normalized by Row)', fontsize=14, fontweight='bold')

    # Add text annotations
    for i in range(len(labels)):
        for j in range(len(labels)):
            value = matrix[i, j]
            norm_value = matrix_normalized[i, j]
            if value > 0:
                text_color = 'white' if norm_value > 0.5 else 'black'
                ax.text(j, i, f'{value}\n({norm_value:.0%})',
                       ha='center', va='center', color=text_color, fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Confusion matrix saved to: {output_path}")
    plt.close()

def plot_classification_metrics(evaluations, output_path):
    """Plot per-class precision, recall, F1."""
    # Compute metrics from evaluations
    predictions, ground_truths, labels = build_confusion_data(evaluations)
    matrix = compute_confusion_matrix(predictions, ground_truths, labels)

    # Remove 'other' for metrics
    main_labels = labels[:-1]

    metrics = {}
    for i, label in enumerate(main_labels):
        tp = matrix[i, i]
        fp = matrix[:, i].sum() - tp
        fn = matrix[i, :].sum() - tp

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        support = matrix[i, :].sum()

        if support > 0:
            metrics[label] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'support': support
            }

    # Sort by F1 score
    sorted_labels = sorted(metrics.keys(), key=lambda x: -metrics[x]['f1'])

    # Short labels
    short_labels = {
        'privacy_violation': 'Privacy',
        'safety_failure': 'Safety',
        'bias': 'Bias',
        'accuracy_failure': 'Accuracy',
        'transparency_failure': 'Transparency',
        'misinformation': 'Misinfo',
        'copyright': 'Copyright'
    }

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(sorted_labels))
    width = 0.25

    precisions = [metrics[l]['precision'] for l in sorted_labels]
    recalls = [metrics[l]['recall'] for l in sorted_labels]
    f1s = [metrics[l]['f1'] for l in sorted_labels]

    bars1 = ax.bar(x - width, precisions, width, label='Precision', color='#2196F3')
    bars2 = ax.bar(x, recalls, width, label='Recall', color='#4CAF50')
    bars3 = ax.bar(x + width, f1s, width, label='F1-Score', color='#FF9800')

    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Classification Metrics by Incident Type', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([short_labels.get(l, l) for l in sorted_labels], fontsize=11)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.1)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)

    # Add support labels
    for i, label in enumerate(sorted_labels):
        support = metrics[label]['support']
        ax.text(i, 1.02, f'n={support}', ha='center', fontsize=9, color='gray')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Metrics plot saved to: {output_path}")
    plt.close()

def plot_risk_level_confusion(evaluations, output_path):
    """Plot risk level confusion matrix."""
    risk_confusion = defaultdict(lambda: defaultdict(int))

    for eval_item in evaluations:
        rl = eval_item.get("risk_level", {})
        predicted = rl.get("predicted", "unknown")
        expected = rl.get("expected", "unknown")
        risk_confusion[expected][predicted] += 1

    labels = ["HighRisk", "MinimalRisk", "LimitedRisk"]
    matrix = np.zeros((3, 3), dtype=int)

    for i, gt in enumerate(labels):
        for j, pred in enumerate(labels):
            matrix[i, j] = risk_confusion.get(gt, {}).get(pred, 0)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Normalize
    row_sums = matrix.sum(axis=1, keepdims=True)
    matrix_normalized = np.divide(matrix.astype(float), row_sums, where=row_sums!=0)

    im = ax.imshow(matrix_normalized, cmap='Greens', aspect='auto', vmin=0, vmax=1)
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Proportion', fontsize=11)

    ax.set_xticks(np.arange(3))
    ax.set_yticks(np.arange(3))
    ax.set_xticklabels(['High', 'Minimal', 'Limited'], fontsize=11)
    ax.set_yticklabels(['High', 'Minimal', 'Limited'], fontsize=11)

    ax.set_xlabel('Predicted Risk Level', fontsize=12, fontweight='bold')
    ax.set_ylabel('Expected Risk Level', fontsize=12, fontweight='bold')
    ax.set_title('Risk Level Classification - Confusion Matrix\n(EU AI Act Risk Categories)', fontsize=13, fontweight='bold')

    # Annotations
    for i in range(3):
        for j in range(3):
            value = matrix[i, j]
            norm_value = matrix_normalized[i, j]
            if value > 0:
                text_color = 'white' if norm_value > 0.5 else 'black'
                ax.text(j, i, f'{value}\n({norm_value:.0%})',
                       ha='center', va='center', color=text_color, fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Risk level confusion matrix saved to: {output_path}")
    plt.close()

def main():
    print("Loading evaluations...")
    evaluations = load_evaluations()
    print(f"Loaded {len(evaluations)} evaluations")

    predictions, ground_truths, labels = build_confusion_data(evaluations)
    matrix = compute_confusion_matrix(predictions, ground_truths, labels)

    # Generate plots
    plot_confusion_matrix(
        matrix, labels,
        f"{RESULTS_DIR}/confusion_matrix_incident_type_v041.png"
    )

    plot_classification_metrics(
        evaluations,
        f"{RESULTS_DIR}/classification_metrics_v041.png"
    )

    plot_risk_level_confusion(
        evaluations,
        f"{RESULTS_DIR}/confusion_matrix_risk_level_v041.png"
    )

    print("\nAll plots generated successfully!")

if __name__ == "__main__":
    main()
