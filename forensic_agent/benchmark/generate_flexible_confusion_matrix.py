#!/usr/bin/env python3
"""
Generate confusion matrices with flexible matching visualization.
Shows both strict match (diagonal only) and flexible match (multi-label correct).
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use('Agg')

# Results file path
RESULTS_DIR = "/Users/cartesio/workspace/ai_act_project/forensic_agent/benchmark/results"
EVAL_FILE = f"{RESULTS_DIR}/real_benchmark_evaluations_v2_20260108_105208.json"

def load_evaluations():
    with open(EVAL_FILE, 'r') as f:
        return json.load(f)

def build_flexible_confusion_data(evaluations):
    """Build confusion matrix with flexible matching annotation."""
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
    is_flexible = []  # Track which are flexible matches
    
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
                if predicted not in main_categories:
                    predicted = "other"
                
                predictions.append(predicted)
                ground_truths.append(expected_primary)
                
                # Check if flexible match but not strict match
                is_flex = (predicted in expected_all_normalized) and (predicted != expected_primary)
                is_flexible.append(is_flex)
    
    return predictions, ground_truths, is_flexible, main_categories + ["other"]

def compute_flexible_confusion_matrix(predictions, ground_truths, is_flexible, labels):
    """Compute confusion matrix with flexible match tracking."""
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    n = len(labels)
    
    # Three matrices: strict correct, flexible correct, wrong
    strict_matrix = np.zeros((n, n), dtype=int)
    flexible_matrix = np.zeros((n, n), dtype=int)
    wrong_matrix = np.zeros((n, n), dtype=int)
    
    for pred, gt, is_flex in zip(predictions, ground_truths, is_flexible):
        if gt in label_to_idx:
            pred_idx = label_to_idx.get(pred, label_to_idx.get("other", n-1))
            gt_idx = label_to_idx[gt]
            
            if pred == gt:
                # Strict match (diagonal)
                strict_matrix[gt_idx, pred_idx] += 1
            elif is_flex:
                # Flexible match (off-diagonal but valid)
                flexible_matrix[gt_idx, pred_idx] += 1
            else:
                # Wrong prediction
                wrong_matrix[gt_idx, pred_idx] += 1
    
    return strict_matrix, flexible_matrix, wrong_matrix

def plot_flexible_confusion_matrix(strict_matrix, flexible_matrix, wrong_matrix, labels, output_path):
    """Create confusion matrix with color coding for flexible matches."""
    
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
    
    fig, ax = plt.subplots(figsize=(14, 11))
    
    # Combine matrices with different colors
    # We'll create a colored visualization
    n = len(labels)
    
    # Create RGB image (3 channels)
    image = np.ones((n, n, 3))  # Start with white background
    
    # Normalize for visualization
    total_matrix = strict_matrix + flexible_matrix + wrong_matrix
    row_sums = total_matrix.sum(axis=1, keepdims=True)
    
    for i in range(n):
        for j in range(n):
            if row_sums[i] == 0:
                continue
                
            strict_val = strict_matrix[i, j] / row_sums[i]
            flex_val = flexible_matrix[i, j] / row_sums[i]
            wrong_val = wrong_matrix[i, j] / row_sums[i]
            
            # Color scheme:
            # Green = strict correct
            # Yellow = flexible correct
            # Red = wrong
            
            if strict_val > 0:
                # Green (correct)
                image[i, j, 0] = 0
                image[i, j, 1] = strict_val * 0.8
                image[i, j, 2] = 0
            elif flex_val > 0:
                # Yellow (flexible)
                image[i, j, 0] = flex_val * 0.9
                image[i, j, 1] = flex_val * 0.9
                image[i, j, 2] = 0
            elif wrong_val > 0:
                # Red (wrong)
                image[i, j, 0] = wrong_val * 0.8
                image[i, j, 1] = 0
                image[i, j, 2] = 0
    
    # Display image
    ax.imshow(image, aspect='auto')
    
    # Add text annotations with counts
    for i in range(n):
        for j in range(n):
            strict_count = strict_matrix[i, j]
            flex_count = flexible_matrix[i, j]
            wrong_count = wrong_matrix[i, j]
            
            if strict_count > 0:
                text = ax.text(j, i, f'{strict_count}',
                             ha="center", va="center", color="white", fontsize=10, weight='bold')
            elif flex_count > 0:
                text = ax.text(j, i, f'{flex_count}\n(flex)',
                             ha="center", va="center", color="black", fontsize=9)
            elif wrong_count > 0:
                text = ax.text(j, i, f'{wrong_count}',
                             ha="center", va="center", color="white", fontsize=9)
    
    # Set ticks
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(display_labels, fontsize=11, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(display_labels, fontsize=11)
    
    # Labels
    ax.set_xlabel('Predicted Type', fontsize=13, weight='bold')
    ax.set_ylabel('Expected Type (Primary)', fontsize=13, weight='bold')
    ax.set_title('Incident Type Classification - Flexible Matching\n(Green=Strict Match, Yellow=Flexible Match, Red=Wrong)', 
                 fontsize=14, weight='bold', pad=20)
    
    # Add legend
    strict_patch = mpatches.Patch(color='darkgreen', label='Strict Match (primary type)')
    flex_patch = mpatches.Patch(color='yellow', label='Flexible Match (in expected_all)')
    wrong_patch = mpatches.Patch(color='darkred', label='Wrong Prediction')
    ax.legend(handles=[strict_patch, flex_patch, wrong_patch], 
             loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=11)
    
    # Add grid
    ax.set_xticks(np.arange(n) - 0.5, minor=True)
    ax.set_yticks(np.arange(n) - 0.5, minor=True)
    ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Flexible confusion matrix saved to: {output_path}")

def calculate_metrics(strict_matrix, flexible_matrix, wrong_matrix, labels):
    """Calculate metrics showing improvement from flexible matching."""
    
    print("\n" + "="*80)
    print("METRICS COMPARISON: Strict vs Flexible Matching")
    print("="*80)
    
    n = len(labels)
    total_matrix = strict_matrix + flexible_matrix + wrong_matrix
    
    total_cases = total_matrix.sum()
    strict_correct = strict_matrix.sum()
    flexible_correct = flexible_matrix.sum()
    wrong_total = wrong_matrix.sum()
    
    strict_accuracy = strict_correct / total_cases if total_cases > 0 else 0
    flexible_accuracy = (strict_correct + flexible_correct) / total_cases if total_cases > 0 else 0
    
    print(f"\nTotal Cases: {int(total_cases)}")
    print(f"\nStrict Match Accuracy:   {int(strict_correct)}/{int(total_cases)} = {strict_accuracy:.1%}")
    print(f"Flexible Match Accuracy: {int(strict_correct + flexible_correct)}/{int(total_cases)} = {flexible_accuracy:.1%}")
    print(f"  (Improvement: +{flexible_accuracy - strict_accuracy:.1%})")
    print(f"\nFlexible Matches: {int(flexible_correct)} cases ({flexible_correct/total_cases:.1%})")
    print(f"Genuine Errors:   {int(wrong_total)} cases ({wrong_total/total_cases:.1%})")
    
    # Per-class breakdown
    print(f"\n{'Class':<20} {'Strict':<10} {'Flexible':<12} {'Wrong':<10} {'Total':<10}")
    print("-"*70)
    
    for i, label in enumerate(labels):
        strict_count = strict_matrix[i, :].sum()
        flex_count = flexible_matrix[i, :].sum()
        wrong_count = wrong_matrix[i, :].sum()
        total = total_matrix[i, :].sum()
        
        if total > 0:
            print(f"{label:<20} {int(strict_count):<10} {int(flex_count):<12} {int(wrong_count):<10} {int(total):<10}")

def main():
    print("Loading evaluations...")
    evaluations = load_evaluations()
    print(f"Loaded {len(evaluations)} evaluations")
    
    # Build confusion data
    predictions, ground_truths, is_flexible, labels = build_flexible_confusion_data(evaluations)
    
    # Compute matrices
    strict_matrix, flexible_matrix, wrong_matrix = compute_flexible_confusion_matrix(
        predictions, ground_truths, is_flexible, labels
    )
    
    # Plot
    output_path = f"{RESULTS_DIR}/confusion_matrix_flexible_v041.png"
    plot_flexible_confusion_matrix(strict_matrix, flexible_matrix, wrong_matrix, labels, output_path)
    
    # Calculate and print metrics
    calculate_metrics(strict_matrix, flexible_matrix, wrong_matrix, labels)
    
    print("\nAll visualizations generated successfully!")

if __name__ == "__main__":
    main()
