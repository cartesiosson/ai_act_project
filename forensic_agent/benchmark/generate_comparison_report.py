#!/usr/bin/env python3
"""
Genera reporte comparativo entre benchmark v0.41 (anterior) y nuevo benchmark.
Muestra mejoras en clasificación de incident_type.
"""

import json
import sys
from pathlib import Path
from collections import Counter

def load_evaluations(file_path):
    """Load evaluation results from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_confusion_matrix(evaluations):
    """Calculate confusion matrix for incident_type."""
    confusion = {}
    for eval in evaluations:
        it = eval.get('incident_type', {})
        expected = it.get('expected_primary')
        predicted = it.get('predicted')

        if expected and predicted:
            if expected not in confusion:
                confusion[expected] = {}
            confusion[expected][predicted] = confusion[expected].get(predicted, 0) + 1

    return confusion

def calculate_metrics(evaluations):
    """Calculate precision, recall, F1 for each class."""
    from collections import defaultdict

    # Count TP, FP, FN for each class
    metrics = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})

    for eval in evaluations:
        it = eval.get('incident_type', {})
        expected = it.get('expected_primary')
        predicted = it.get('predicted')

        if not expected or not predicted:
            continue

        if expected == predicted:
            metrics[expected]['tp'] += 1
        else:
            metrics[expected]['fn'] += 1
            metrics[predicted]['fp'] += 1

    # Calculate precision, recall, F1
    results = {}
    for class_name, counts in metrics.items():
        tp = counts['tp']
        fp = counts['fp']
        fn = counts['fn']

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        results[class_name] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': tp + fn,
            'tp': tp,
            'fp': fp,
            'fn': fn
        }

    return results

def print_comparison(old_file, new_file):
    """Print comparison between old and new results."""

    print("=" * 80)
    print("COMPARACIÓN: BENCHMARK v0.41 vs NUEVO (definiciones mejoradas)")
    print("=" * 80)
    print()

    # Load data
    old_evals = load_evaluations(old_file)
    new_evals = load_evaluations(new_file)

    print(f"Casos analizados: {len(old_evals)} (v0.41) vs {len(new_evals)} (nuevo)")
    print()

    # Calculate metrics
    old_metrics = calculate_metrics(old_evals)
    new_metrics = calculate_metrics(new_evals)

    # Focus on accuracy_failure and privacy_violation
    print("### MÉTRICAS CLAVE: accuracy_failure")
    print("-" * 80)

    if 'accuracy_failure' in old_metrics and 'accuracy_failure' in new_metrics:
        old_acc = old_metrics['accuracy_failure']
        new_acc = new_metrics['accuracy_failure']

        print(f"{'Métrica':<15} {'v0.41':<15} {'Nuevo':<15} {'Cambio':<15}")
        print("-" * 60)

        for metric in ['precision', 'recall', 'f1']:
            old_val = old_acc[metric]
            new_val = new_acc[metric]
            delta = new_val - old_val
            delta_str = f"{delta:+.3f}" if delta != 0 else "="

            print(f"{metric:<15} {old_val:<15.3f} {new_val:<15.3f} {delta_str:<15}")

        print(f"{'support':<15} {old_acc['support']:<15} {new_acc['support']:<15}")

    print()
    print("### MÉTRICAS CLAVE: privacy_violation")
    print("-" * 80)

    if 'privacy_violation' in old_metrics and 'privacy_violation' in new_metrics:
        old_priv = old_metrics['privacy_violation']
        new_priv = new_metrics['privacy_violation']

        print(f"{'Métrica':<15} {'v0.41':<15} {'Nuevo':<15} {'Cambio':<15}")
        print("-" * 60)

        for metric in ['precision', 'recall', 'f1']:
            old_val = old_priv[metric]
            new_val = new_priv[metric]
            delta = new_val - old_val
            delta_str = f"{delta:+.3f}" if delta != 0 else "="

            print(f"{metric:<15} {old_val:<15.3f} {new_val:<15.3f} {delta_str:<15}")

        print(f"{'FP count':<15} {old_priv['fp']:<15} {new_priv['fp']:<15} {new_priv['fp']-old_priv['fp']}")

    print()
    print("### TODAS LAS CLASES")
    print("-" * 80)

    all_classes = sorted(set(list(old_metrics.keys()) + list(new_metrics.keys())))

    print(f"{'Clase':<20} {'F1 (v0.41)':<12} {'F1 (nuevo)':<12} {'Cambio':<10}")
    print("-" * 60)

    for cls in all_classes:
        old_f1 = old_metrics.get(cls, {}).get('f1', 0)
        new_f1 = new_metrics.get(cls, {}).get('f1', 0)
        delta = new_f1 - old_f1
        delta_str = f"{delta:+.3f}" if delta != 0 else "="

        print(f"{cls:<20} {old_f1:<12.3f} {new_f1:<12.3f} {delta_str:<10}")

    print()
    print("### ERRORES ESPECÍFICOS: accuracy_failure → X")
    print("-" * 80)

    # Count misclassifications
    old_confusions = Counter()
    new_confusions = Counter()

    for eval in old_evals:
        it = eval.get('incident_type', {})
        if it.get('expected_primary') == 'accuracy_failure' and it.get('predicted') != 'accuracy_failure':
            old_confusions[it.get('predicted')] += 1

    for eval in new_evals:
        it = eval.get('incident_type', {})
        if it.get('expected_primary') == 'accuracy_failure' and it.get('predicted') != 'accuracy_failure':
            new_confusions[it.get('predicted')] += 1

    print(f"{'Predicción':<25} {'v0.41':<10} {'Nuevo':<10} {'Cambio':<10}")
    print("-" * 60)

    all_pred = sorted(set(list(old_confusions.keys()) + list(new_confusions.keys())))
    for pred in all_pred:
        old_count = old_confusions.get(pred, 0)
        new_count = new_confusions.get(pred, 0)
        delta = new_count - old_count
        delta_str = f"{delta:+d}" if delta != 0 else "="

        print(f"{pred:<25} {old_count:<10} {new_count:<10} {delta_str:<10}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_comparison_report.py <new_evaluations_file>")
        print("Example: python3 generate_comparison_report.py results/real_benchmark_evaluations_v2_20260108_105208.json")
        sys.exit(1)

    old_file = Path(__file__).parent / "results" / "real_benchmark_evaluations_v2_20260107_165124.json"
    new_file = Path(sys.argv[1])

    if not old_file.exists():
        print(f"ERROR: Old benchmark file not found: {old_file}")
        sys.exit(1)

    if not new_file.exists():
        print(f"ERROR: New benchmark file not found: {new_file}")
        sys.exit(1)

    print_comparison(old_file, new_file)

if __name__ == "__main__":
    main()
