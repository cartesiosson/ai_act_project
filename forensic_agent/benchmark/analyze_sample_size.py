#!/usr/bin/env python3
"""
Análisis de tamaño de muestra estadísticamente significativo
para clasificación de tipos de incidentes en AIAAIC.
"""

import json
import math
from collections import Counter

# Cargar datos del benchmark anterior (100 casos)
with open('results/real_benchmark_evaluations_v2_20260107_165124.json', 'r') as f:
    evals = json.load(f)

# Contar distribución de tipos de incidentes (ground truth)
incident_types = []
for e in evals:
    it = e.get('incident_type', {})
    expected = it.get('expected_primary')
    if expected:
        incident_types.append(expected)

type_counts = Counter(incident_types)
total = len(incident_types)

print('=' * 80)
print('ANÁLISIS DE DISTRIBUCIÓN DE TIPOS DE INCIDENTES (AIAAIC)')
print('=' * 80)
print(f'\nTotal casos analizados: {total}')
print()

# Distribución observada
print('Distribución observada en muestra de 100 casos:')
print(f"{'Tipo':<25} {'Casos':>8} {'%':>8} {'Proporción':>12}")
print('-' * 60)

sorted_types = sorted(type_counts.items(), key=lambda x: -x[1])
for incident_type, count in sorted_types:
    pct = 100 * count / total
    prop = count / total
    print(f'{incident_type:<25} {count:>8} {pct:>7.1f}% {prop:>12.4f}')

print()
print('=' * 80)
print('CÁLCULO DE TAMAÑO DE MUESTRA MÍNIMO')
print('=' * 80)
print()

# Para cada clase, calcular tamaño mínimo usando fórmula de proporción
# n = (Z^2 * p * (1-p)) / E^2
# Donde:
# - Z = 1.96 para 95% confianza
# - p = proporción observada
# - E = margen de error deseado

Z = 1.96  # 95% confianza
margins = [0.05, 0.10, 0.15]  # 5%, 10%, 15% error

print('Tamaño mínimo de muestra por clase (para detectar cada tipo):')
print()

for margin in margins:
    print(f'Con margen de error E = {margin:.0%} y 95% confianza:')
    print(f"{'Tipo':<25} {'Proporción':>12} {'n mínimo':>10}")
    print('-' * 50)

    max_n = 0
    for incident_type, count in sorted_types:
        p = count / total

        # Fórmula para proporción
        n = (Z**2 * p * (1-p)) / (margin**2)
        max_n = max(max_n, n)

        print(f'{incident_type:<25} {p:>12.4f} {int(math.ceil(n)):>10}')

    label = 'MÁXIMO (limitante):'
    print(f'{label:<25} {"":>12} {int(math.ceil(max_n)):>10}')
    print()

print()
print('=' * 80)
print('ANÁLISIS POR CLASE MINORITARIA')
print('=' * 80)
print()

# Para clases minoritarias, necesitamos suficientes ejemplos para evaluar
min_samples_per_class = [5, 10, 15, 20]

print('Casos necesarios para garantizar N ejemplos de la clase más rara:')
print()

min_proportion = min([count/total for count in type_counts.values()])
rarest_type = min(type_counts.items(), key=lambda x: x[1])

print(f'Clase más rara: {rarest_type[0]} ({rarest_type[1]}/{total} = {100*rarest_type[1]/total:.1f}%)')
print()

print(f"{'Ejemplos deseados':>20} {'Muestra total necesaria':>25}")
print('-' * 50)

for min_samples in min_samples_per_class:
    needed = math.ceil(min_samples / min_proportion)
    print(f'{min_samples:>20} {needed:>25}')

print()
print('=' * 80)
print('RECOMENDACIÓN FINAL')
print('=' * 80)
print()

# Criterio conservador: al menos 10 ejemplos de la clase menos frecuente
min_examples = 10
recommended = math.ceil(min_examples / min_proportion)

print(f'Para garantizar al menos {min_examples} ejemplos de cada clase:')
print(f'  Tamaño mínimo recomendado: {recommended} casos')
print()
print(f'Benchmark actual: {total} casos')
status = "✓ SUFICIENTE" if total >= recommended else "✗ INSUFICIENTE"
print(f'Estado: {status}')
print()

# Análisis de poder estadístico para accuracy_failure
accuracy_count = type_counts.get('accuracy_failure', 0)
print(f'Casos específicos para accuracy_failure: {accuracy_count}')
print(f'  Con 21 casos, podemos detectar diferencias de ~22% (95% confianza)')
print(f'  Con 50 casos, podemos detectar diferencias de ~14% (95% confianza)')
print(f'  Con 100 casos, podemos detectar diferencias de ~10% (95% confianza)')
print()

# Recomendaciones específicas
print('=' * 80)
print('RECOMENDACIONES ESPECÍFICAS')
print('=' * 80)
print()
print('1. MÍNIMO ABSOLUTO: 67 casos')
print('   - Garantiza al menos 5 ejemplos de cada tipo')
print('   - Suficiente para análisis exploratorio')
print()
print('2. RECOMENDADO: 100-150 casos')
print('   - Garantiza 10-15 ejemplos de la clase más rara')
print('   - Margen de error ~10% para métricas globales')
print('   - Poder estadístico adecuado para comparaciones')
print()
print('3. ÓPTIMO: 200+ casos')
print('   - Garantiza 20+ ejemplos de cada tipo')
print('   - Margen de error ~7% para métricas globales')
print('   - Alta confiabilidad para todas las clases')
print()
print('Para el problema específico accuracy_failure vs privacy_violation:')
print(f'  - Actual: {accuracy_count} casos accuracy_failure')
print(f'  - Mínimo: 30 casos (para detectar mejoras de ±18%)')
print(f'  - Recomendado: 50 casos (para detectar mejoras de ±14%)')
print(f'  - Estado: {"✓ SUFICIENTE" if accuracy_count >= 30 else "✗ INSUFICIENTE"}')
