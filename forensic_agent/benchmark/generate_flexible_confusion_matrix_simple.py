#!/usr/bin/env python3
"""
Generate simple confusion matrix using flexible matching.
Flexible matches are counted as correct (on diagonal).
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from sklearn.metrics import ConfusionMatrixDisplay

# Results file path
RESULTS_DIR = "/Users/cartesio/workspace/ai_act_project/forensic_agent/benchmark/results"
EVAL_FILE = f"{RESULTS_DIR}/real_benchmark_evaluations_v2_20260108_105208.json"

def load_evaluations():
    with open(EVAL_FILE, 'r') as f:
        return json.load(f)

def build_flexible_confusion_data(evaluations):
    """
    Build confusion matrix treating flexible matches as correct.
    If prediction is in expected_all, map it to expected_primary for the matrix.
    """
    main_categories = [
        'accuracy_failure',
        'bias',
        'privacy_violation',
        'safety_failure',
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
        expected_all = it.get("expected_all", [])
        
        if predicted and expected_primary:
            predicted = predicted.lower().replace(" ", "_")
            expected_primary = expected_primary.lower().replace(" ", "_")
            expected_all_normalized = [e.lower().replace(" ", "_") for e in expected_all]
            
            if expected_primary in main_categories:
                # If prediction is in expected_all (flexible match), treat as correct
                if predicted in expected_all_normalized:
                    # Map to expected_primary (will appear on diagonal)
                    predictions.append(expected_primary)
                else:
                    # Wrong prediction
                    if predicted not in main_categories:
                        predicted = "other"
                    predictions.append(predicted)
                
                ground_truths.append(expected_primary)
    
    return predictions, ground_truths, main_categories

def compute_metrics(predictions, ground_truths, labels):
    """Calculate precision, recall, F1 per class."""
    from collections import defaultdict
    
    metrics = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0, 'support': 0})
    
    for pred, true in zip(predictions, ground_truths):
        if pred == true:
            metrics[true]['tp'] += 1
        else:
            metrics[true]['fn'] += 1
            metrics[pred]['fp'] += 1
        
        metrics[true]['support'] += 1
    
    results = {}
    for label in labels:
        m = metrics[label]
        precision = m['tp'] / (m['tp'] + m['fp']) if (m['tp'] + m['fp']) > 0 else 0
        recall = m['tp'] / (m['tp'] + m['fn']) if (m['tp'] + m['fn']) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        results[label] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': m['support']
        }
    
    return results

def plot_confusion_matrix(predictions, ground_truths, labels, output_path):
    """Create clean confusion matrix plot."""
    
    # Short labels for display
    short_labels = {
        'accuracy_failure': 'Accuracy',
        'bias': 'Bias',
        'privacy_violation': 'Privacy',
        'safety_failure': 'Safety',
        'transparency_failure': 'Transparency',
        'misinformation': 'Misinfo',
        'copyright': 'Copyright'
    }
    display_labels = [short_labels.get(l, l) for l in labels]
    
    # Compute confusion matrix
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    n = len(labels)
    matrix = np.zeros((n, n), dtype=int)
    
    for pred, gt in zip(predictions, ground_truths):
        if gt in label_to_idx and pred in label_to_idx:
            matrix[label_to_idx[gt], label_to_idx[pred]] += 1
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Normalize by row (recall)
    row_sums = matrix.sum(axis=1, keepdims=True)
    matrix_normalized = np.divide(matrix, row_sums, where=row_sums!=0)
    
    # Create heatmap
    im = ax.imshow(matrix_normalized, cmap='Blues', aspect='auto', vmin=0, vmax=1)
    
    # Colorbar
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Recall (Proportion of True Class)', fontsize=12)
    
    # Ticks
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(display_labels, fontsize=11, rotation=45, ha='right')
    ax.set_yticklabels(display_labels, fontsize=11)
    
    # Add text annotations
    for i in range(n):
        for j in range(n):
            count = matrix[i, j]
            if count > 0:
                proportion = matrix_normalized[i, j]
                text_color = "white" if proportion > 0.5 else "black"
                
                # Show count and percentage
                text = f'{count}\n({proportion:.0%})'
                ax.text(j, i, text, ha="center", va="center", 
                       color=text_color, fontsize=10, weight='bold' if i==j else 'normal')
    
    # Labels
    ax.set_xlabel('Predicted Type', fontsize=13, weight='bold')
    ax.set_ylabel('Expected Type (Primary)', fontsize=13, weight='bold')
    ax.set_title('Incident Type Classification - Flexible Matching\n(Multi-label predictions counted as correct)', 
                 fontsize=14, weight='bold', pad=20)
    
    # Grid
    ax.set_xticks(np.arange(n) - 0.5, minor=True)
    ax.set_yticks(np.arange(n) - 0.5, minor=True)
    ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Confusion matrix saved to: {output_path}")

def print_metrics_report(metrics, predictions, ground_truths):
    """Print classification report."""
    
    print("\n" + "="*80)
    print("CLASSIFICATION REPORT - Flexible Matching")
    print("="*80)
    
    total_cases = len(predictions)
    correct = sum(1 for p, g in zip(predictions, ground_truths) if p == g)
    accuracy = correct / total_cases if total_cases > 0 else 0
    
    print(f"\nOverall Accuracy: {correct}/{total_cases} = {accuracy:.1%}")
    print()
    
    print(f"{'Class':<20} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
    print("-"*70)
    
    macro_precision = 0
    macro_recall = 0
    macro_f1 = 0
    total_support = 0
    
    for label in sorted(metrics.keys(), key=lambda x: -metrics[x]['support']):
        m = metrics[label]
        if m['support'] > 0:
            print(f"{label:<20} {m['precision']:<12.3f} {m['recall']:<12.3f} {m['f1']:<12.3f} {m['support']:<10}")
            macro_precision += m['precision']
            macro_recall += m['recall']
            macro_f1 += m['f1']
            total_support += m['support']
    
    n_classes = len([m for m in metrics.values() if m['support'] > 0])
    
    print("-"*70)
    print(f"{'Macro Avg':<20} {macro_precision/n_classes:<12.3f} {macro_recall/n_classes:<12.3f} {macro_f1/n_classes:<12.3f} {total_support:<10}")
    print()

def main():
    print("Loading evaluations...")
    evaluations = load_evaluations()
    print(f"Loaded {len(evaluations)} evaluations")
    
    # Build confusion data with flexible matching
    predictions, ground_truths, labels = build_flexible_confusion_data(evaluations)
    
    print(f"\nProcessed {len(predictions)} cases with primary type in main categories")
    
    # Plot confusion matrix
    output_path = f"{RESULTS_DIR}/confusion_matrix_flexible_simple_v041.png"
    plot_confusion_matrix(predictions, ground_truths, labels, output_path)
    
    # Calculate and print metrics
    metrics = compute_metrics(predictions, ground_truths, labels)
    print_metrics_report(metrics, predictions, ground_truths)
    
    print("\nVisualization complete!")

if __name__ == "__main__":
    main()
