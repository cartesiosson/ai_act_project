#!/usr/bin/env python3
"""
Synthetic Benchmark Visualization Generator

Generates KPI charts and Confusion Matrices for synthetic benchmark evaluation.
Includes both STRICT (exact match) and FLEXIBLE (semantic match) evaluations.

Author: TFM EU AI Act Compliance
Date: January 2026
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, accuracy_score
from datetime import datetime

# Paths
BENCHMARK_DIR = Path(__file__).parent
RESULTS_DIR = BENCHMARK_DIR / "results"

# Semantic mappings for flexible evaluation
INCIDENT_TYPE_MAPPINGS = {
    'bias': ['bias', 'discrimination', 'fairness'],
    'safety_failure': ['safety_failure', 'accuracy_failure', 'safety'],
    'transparency_failure': ['transparency_failure', 'accountability', 'transparency'],
    'privacy_violation': ['privacy_violation', 'privacy', 'data_leakage'],
    'misinformation': ['misinformation', 'Mis/disinformation', 'fake_content'],
    'copyright': ['copyright', 'appropriation', 'ip_violation'],
}

RISK_LEVEL_MAPPINGS = {
    'HighRisk': ['HighRisk', 'Unacceptable'],
    'MinimalRisk': ['MinimalRisk', 'LimitedRisk', 'OutOfScope'],
}


def load_results(results_file: Path):
    """Load benchmark results."""
    with open(results_file) as f:
        return json.load(f)


def get_flexible_match(expected: str, predicted: str, mappings: dict) -> bool:
    """Check if prediction matches expected using semantic mappings."""
    if expected == predicted:
        return True

    for base, variations in mappings.items():
        if expected in variations and predicted in variations:
            return True
    return False


def normalize_label(label: str, mappings: dict) -> str:
    """Normalize label to base category for flexible evaluation."""
    for base, variations in mappings.items():
        if label in variations:
            return base
    return label


def extract_classification_data(data: list, strict: bool = True):
    """Extract incident type and risk level classification data."""
    completed = [r for r in data if r.get('status') == 'COMPLETED']

    incident_types = {'y_true': [], 'y_pred': []}
    risk_levels = {'y_true': [], 'y_pred': []}

    for r in completed:
        # Incident type
        exp_type = r.get('expected_incident_type') or r.get('metadata', {}).get('template_type')
        pred_type = r.get('extraction', {}).get('incident', {}).get('incident_type')

        if exp_type and pred_type:
            if not strict:
                exp_type = normalize_label(exp_type, INCIDENT_TYPE_MAPPINGS)
                pred_type = normalize_label(pred_type, INCIDENT_TYPE_MAPPINGS)
            incident_types['y_true'].append(exp_type)
            incident_types['y_pred'].append(pred_type)

        # Risk level
        exp_risk = r.get('expected_risk_level') or r.get('metadata', {}).get('expected_risk_level')
        pred_risk = r.get('eu_ai_act', {}).get('risk_level')

        if exp_risk and pred_risk:
            if not strict:
                exp_risk = normalize_label(exp_risk, RISK_LEVEL_MAPPINGS)
                pred_risk = normalize_label(pred_risk, RISK_LEVEL_MAPPINGS)
            risk_levels['y_true'].append(exp_risk)
            risk_levels['y_pred'].append(pred_risk)

    return incident_types, risk_levels


def compute_metrics(y_true: list, y_pred: list) -> dict:
    """Compute classification metrics."""
    labels = sorted(set(y_true) | set(y_pred))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )

    accuracy = accuracy_score(y_true, y_pred)

    return {
        'accuracy': accuracy,
        'precision_macro': float(np.mean(precision)),
        'recall_macro': float(np.mean(recall)),
        'f1_macro': float(np.mean(f1)),
        'precision_weighted': float(np.average(precision, weights=support)) if sum(support) > 0 else 0,
        'recall_weighted': float(np.average(recall, weights=support)) if sum(support) > 0 else 0,
        'f1_weighted': float(np.average(f1, weights=support)) if sum(support) > 0 else 0,
        'per_class': {
            label: {
                'precision': float(precision[i]),
                'recall': float(recall[i]),
                'f1': float(f1[i]),
                'support': int(support[i])
            }
            for i, label in enumerate(labels)
        }
    }


def generate_kpi_chart(
    incident_metrics: dict,
    risk_metrics: dict,
    mode: str,
    total_incidents: int,
    completed: int,
    errors: int,
    output_path: Path
):
    """Generate KPI visualization chart."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    mode_label = "ESTRICTO" if mode == "strict" else "FLEXIBLE"
    mode_desc = "(Coincidencia exacta)" if mode == "strict" else "(Coincidencia semántica)"

    fig.suptitle(
        f'SERAMIS Benchmark Sintético - KPIs {mode_label}\n'
        f'{mode_desc}\n'
        f'Total: {total_incidents} | Completados: {completed} | Errores: {errors}',
        fontsize=14, fontweight='bold'
    )

    # 1. Overall accuracy comparison
    ax1 = axes[0, 0]
    categories = ['Tipo de\nIncidente', 'Nivel de\nRiesgo']
    accuracies = [incident_metrics['accuracy'], risk_metrics['accuracy']]
    colors = ['#3498db', '#e74c3c']
    bars = ax1.bar(categories, accuracies, color=colors, width=0.6)
    ax1.set_ylim(0, 1.1)
    ax1.set_ylabel('Accuracy', fontsize=11)
    ax1.set_title('Precisión Global por Clasificación', fontsize=12, fontweight='bold')
    ax1.axhline(y=0.7, color='green', linestyle='--', alpha=0.7, label='Umbral 70%')
    ax1.legend()

    for bar, acc in zip(bars, accuracies):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{acc:.1%}', ha='center', va='bottom', fontsize=14, fontweight='bold')

    # 2. Incident Type per-class metrics
    ax2 = axes[0, 1]
    if incident_metrics['per_class']:
        classes = list(incident_metrics['per_class'].keys())
        x = np.arange(len(classes))
        width = 0.25

        precisions = [incident_metrics['per_class'][c]['precision'] for c in classes]
        recalls = [incident_metrics['per_class'][c]['recall'] for c in classes]
        f1s = [incident_metrics['per_class'][c]['f1'] for c in classes]

        ax2.bar(x - width, precisions, width, label='Precision', color='#2ecc71')
        ax2.bar(x, recalls, width, label='Recall', color='#3498db')
        ax2.bar(x + width, f1s, width, label='F1-Score', color='#9b59b6')

        ax2.set_xticks(x)
        ax2.set_xticklabels(classes, rotation=45, ha='right', fontsize=9)
        ax2.set_ylim(0, 1.1)
        ax2.set_ylabel('Score')
        ax2.set_title('Métricas por Tipo de Incidente', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right')

    # 3. Risk Level per-class metrics
    ax3 = axes[1, 0]
    if risk_metrics['per_class']:
        classes = list(risk_metrics['per_class'].keys())
        x = np.arange(len(classes))
        width = 0.25

        precisions = [risk_metrics['per_class'][c]['precision'] for c in classes]
        recalls = [risk_metrics['per_class'][c]['recall'] for c in classes]
        f1s = [risk_metrics['per_class'][c]['f1'] for c in classes]

        ax3.bar(x - width, precisions, width, label='Precision', color='#2ecc71')
        ax3.bar(x, recalls, width, label='Recall', color='#3498db')
        ax3.bar(x + width, f1s, width, label='F1-Score', color='#9b59b6')

        ax3.set_xticks(x)
        ax3.set_xticklabels(classes, rotation=0, fontsize=10)
        ax3.set_ylim(0, 1.1)
        ax3.set_ylabel('Score')
        ax3.set_title('Métricas por Nivel de Riesgo (EU AI Act)', fontsize=12, fontweight='bold')
        ax3.legend(loc='upper right')

    # 4. Summary metrics table
    ax4 = axes[1, 1]
    ax4.axis('off')

    summary_data = [
        ['Métrica', 'Tipo Incidente', 'Nivel Riesgo'],
        ['Accuracy', f"{incident_metrics['accuracy']:.1%}", f"{risk_metrics['accuracy']:.1%}"],
        ['Precision (macro)', f"{incident_metrics['precision_macro']:.3f}", f"{risk_metrics['precision_macro']:.3f}"],
        ['Recall (macro)', f"{incident_metrics['recall_macro']:.3f}", f"{risk_metrics['recall_macro']:.3f}"],
        ['F1-Score (macro)', f"{incident_metrics['f1_macro']:.3f}", f"{risk_metrics['f1_macro']:.3f}"],
        ['F1-Score (weighted)', f"{incident_metrics['f1_weighted']:.3f}", f"{risk_metrics['f1_weighted']:.3f}"],
    ]

    table = ax4.table(
        cellText=summary_data[1:],
        colLabels=summary_data[0],
        loc='center',
        cellLoc='center',
        colWidths=[0.35, 0.3, 0.3]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)

    # Color header
    for j in range(3):
        table[(0, j)].set_facecolor('#34495e')
        table[(0, j)].set_text_props(color='white', fontweight='bold')

    ax4.set_title(f'Resumen de Métricas ({mode_label})', fontsize=12, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path.name}")


def generate_confusion_matrix(
    y_true: list,
    y_pred: list,
    title: str,
    mode: str,
    output_path: Path
):
    """Generate confusion matrix visualization."""
    labels = sorted(set(y_true) | set(y_pred))
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    mode_label = "ESTRICTO" if mode == "strict" else "FLEXIBLE"

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=labels,
        yticklabels=labels,
        cbar_kws={'label': 'Frecuencia'}
    )
    plt.xlabel('Predicción', fontsize=11)
    plt.ylabel('Ground Truth (Esperado)', fontsize=11)
    plt.title(f'{title}\nModo {mode_label}', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    # Add accuracy annotation
    accuracy = accuracy_score(y_true, y_pred)
    plt.figtext(0.99, 0.01, f'Accuracy: {accuracy:.1%}', ha='right', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path.name}")


def main(results_file: Path = None):
    """Main entry point."""
    print("=" * 70)
    print("SYNTHETIC BENCHMARK VISUALIZATION GENERATOR")
    print("=" * 70)

    # Find latest results
    if results_file is None:
        results_files = list(RESULTS_DIR.glob("synthetic_benchmark_results_v2_*.json"))
        if not results_files:
            print("No synthetic benchmark results found!")
            return
        results_file = max(results_files, key=lambda p: p.stat().st_mtime)

    print(f"\nLoading: {results_file.name}")
    data = load_results(results_file)

    total = len(data)
    completed = len([r for r in data if r.get('status') == 'COMPLETED'])
    errors = len([r for r in data if r.get('status') == 'ERROR'])

    print(f"  Total incidents: {total}")
    print(f"  Completed: {completed}")
    print(f"  Errors: {errors}")

    timestamp = results_file.stem.split('_')[-1]

    # Generate STRICT evaluations
    print("\n" + "-" * 70)
    print("Generating STRICT (exact match) visualizations...")
    print("-" * 70)

    incident_strict, risk_strict = extract_classification_data(data, strict=True)

    incident_metrics_strict = compute_metrics(incident_strict['y_true'], incident_strict['y_pred'])
    risk_metrics_strict = compute_metrics(risk_strict['y_true'], risk_strict['y_pred'])

    generate_kpi_chart(
        incident_metrics_strict,
        risk_metrics_strict,
        "strict",
        total, completed, errors,
        RESULTS_DIR / f"synthetic_kpis_estricto_{timestamp}.png"
    )

    generate_confusion_matrix(
        incident_strict['y_true'],
        incident_strict['y_pred'],
        "Matriz de Confusión: Tipo de Incidente",
        "strict",
        RESULTS_DIR / f"synthetic_confusion_incident_estricto_{timestamp}.png"
    )

    generate_confusion_matrix(
        risk_strict['y_true'],
        risk_strict['y_pred'],
        "Matriz de Confusión: Nivel de Riesgo (EU AI Act)",
        "strict",
        RESULTS_DIR / f"synthetic_confusion_risk_estricto_{timestamp}.png"
    )

    # Generate FLEXIBLE evaluations
    print("\n" + "-" * 70)
    print("Generating FLEXIBLE (semantic match) visualizations...")
    print("-" * 70)

    incident_flex, risk_flex = extract_classification_data(data, strict=False)

    incident_metrics_flex = compute_metrics(incident_flex['y_true'], incident_flex['y_pred'])
    risk_metrics_flex = compute_metrics(risk_flex['y_true'], risk_flex['y_pred'])

    generate_kpi_chart(
        incident_metrics_flex,
        risk_metrics_flex,
        "flexible",
        total, completed, errors,
        RESULTS_DIR / f"synthetic_kpis_flexible_{timestamp}.png"
    )

    generate_confusion_matrix(
        incident_flex['y_true'],
        incident_flex['y_pred'],
        "Matriz de Confusión: Tipo de Incidente",
        "flexible",
        RESULTS_DIR / f"synthetic_confusion_incident_flexible_{timestamp}.png"
    )

    generate_confusion_matrix(
        risk_flex['y_true'],
        risk_flex['y_pred'],
        "Matriz de Confusión: Nivel de Riesgo (EU AI Act)",
        "flexible",
        RESULTS_DIR / f"synthetic_confusion_risk_flexible_{timestamp}.png"
    )

    # Save evaluation report
    report = {
        "timestamp": datetime.now().isoformat(),
        "results_file": str(results_file),
        "total_incidents": total,
        "completed": completed,
        "errors": errors,
        "success_rate": completed / total if total > 0 else 0,
        "strict_evaluation": {
            "incident_type": incident_metrics_strict,
            "risk_level": risk_metrics_strict
        },
        "flexible_evaluation": {
            "incident_type": incident_metrics_flex,
            "risk_level": risk_metrics_flex
        }
    }

    report_path = RESULTS_DIR / f"synthetic_evaluation_report_{timestamp}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report saved: {report_path.name}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n{'Evaluation':<20} {'Incident Type':<20} {'Risk Level':<20}")
    print("-" * 60)
    print(f"{'ESTRICTO':<20} {incident_metrics_strict['accuracy']:<20.1%} {risk_metrics_strict['accuracy']:<20.1%}")
    print(f"{'FLEXIBLE':<20} {incident_metrics_flex['accuracy']:<20.1%} {risk_metrics_flex['accuracy']:<20.1%}")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(Path(sys.argv[1]))
    else:
        main()
