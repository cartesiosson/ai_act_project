"""
Reglas SWRL Externas para AI Act
================================

Este paquete contiene reglas SWRL externalizadas para el sistema de razonamiento AI Act.

Módulos:
- base_rules: Reglas contextuales y normativas básicas  
- technical_rules: Reglas técnicas para criterios internos GPAI
- cascade_rules: Reglas de cascada para activación de requisitos
- rules_engine: Motor principal de procesamiento de reglas

Uso:
    from ontologias.rules import rules_engine
    
    inferences = rules_engine.apply_rules(data_graph, combined_graph)
"""

from .rules_engine import rules_engine, ExternalRulesEngine

__all__ = ['rules_engine', 'ExternalRulesEngine']