"""
Sistema de Reglas SWRL Externas para AI Act
===========================================

Este módulo carga y ejecuta reglas SWRL definidas externamente en archivos Python,
proporcionando una alternativa mantenible y auditable al hardcoding de reglas en el código.

Arquitectura:
- base_rules.py: Reglas contextuales y normativas básicas (1-12)
- technical_rules.py: Reglas técnicas para criterios internos GPAI (13-19)
- cascade_rules.py: Reglas de cascada para activación de requisitos (20-23)
- ml_traditional_rules.py: Reglas para ML tradicional (20A, 21-23)
- logic_based_rules.py: Reglas para IA basada en lógica (24-28)
- statistical_rules.py: Reglas para enfoques estadísticos (29-33)

Cada regla se define como un diccionario con:
- id: Identificador único
- name: Nombre descriptivo
- description: Descripción detallada
- conditions: Lista de condiciones que deben cumplirse
- consequences: Lista de consecuencias que se aplican

Formato de condiciones:
{
    "property": "ai:hasParameterCount",
    "operator": ">", 
    "value": 1000000000,
    "type": "int"
}

Operadores soportados: ==, !=, >, <, >=, <=, in, contains
Tipos soportados: int, float, bool, str, uri
"""

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
import os
import importlib.util
from typing import List, Dict, Any, Tuple

# Namespace AI Act
AI = Namespace("http://ai-act.eu/ai#")

class ExternalRulesEngine:
    """Motor de reglas externas para procesamiento de reglas SWRL."""
    
    def __init__(self):
        self.base_rules = []
        self.technical_rules = []
        self.cascade_rules = []
        self.capability_rules = []
        self.ml_traditional_rules = []
        self.logic_based_rules = []
        self.statistical_rules = []
        self.all_rules = []
        self._load_rules()
    
    def _load_rules(self):
        """Carga todas las reglas desde archivos externos."""
        rules_dir = os.path.dirname(__file__)
        
        # Cargar reglas básicas
        try:
            base_module = self._load_module(os.path.join(rules_dir, "base_rules.py"), "base_rules")
            self.base_rules = base_module.BASE_RULES
            print(f"✅ Cargadas {len(self.base_rules)} reglas básicas")
        except Exception as e:
            print(f"❌ Error cargando reglas básicas: {e}")
        
        # Cargar reglas técnicas
        try:
            tech_module = self._load_module(os.path.join(rules_dir, "technical_rules.py"), "technical_rules")
            self.technical_rules = tech_module.TECHNICAL_RULES
            print(f"✅ Cargadas {len(self.technical_rules)} reglas técnicas")
        except Exception as e:
            print(f"❌ Error cargando reglas técnicas: {e}")
        
        # Cargar reglas de cascada
        try:
            cascade_module = self._load_module(os.path.join(rules_dir, "cascade_rules.py"), "cascade_rules")
            self.cascade_rules = cascade_module.CASCADE_RULES
            print(f"✅ Cargadas {len(self.cascade_rules)} reglas de cascada")
        except Exception as e:
            print(f"❌ Error cargando reglas de cascada: {e}")
        
        # Cargar reglas de capacidad del sistema
        try:
            capability_module = self._load_module(os.path.join(rules_dir, "capability_rules.py"), "capability_rules")
            self.capability_rules = capability_module.CAPABILITY_RULES
            print(f"✅ Cargadas {len(self.capability_rules)} reglas de capacidad")
        except Exception as e:
            print(f"❌ Error cargando reglas de capacidad: {e}")
            self.capability_rules = []

        # Cargar reglas de ML tradicional
        try:
            ml_trad_module = self._load_module(os.path.join(rules_dir, "ml_traditional_rules.py"), "ml_traditional_rules")
            self.ml_traditional_rules = ml_trad_module.ALL_RULES
            print(f"✅ Cargadas {len(self.ml_traditional_rules)} reglas de ML tradicional")
        except Exception as e:
            print(f"❌ Error cargando reglas de ML tradicional: {e}")
            self.ml_traditional_rules = []

        # Cargar reglas de lógica y conocimiento
        try:
            logic_module = self._load_module(os.path.join(rules_dir, "logic_based_rules.py"), "logic_based_rules")
            self.logic_based_rules = logic_module.ALL_RULES
            print(f"✅ Cargadas {len(self.logic_based_rules)} reglas de lógica/conocimiento")
        except Exception as e:
            print(f"❌ Error cargando reglas de lógica/conocimiento: {e}")
            self.logic_based_rules = []

        # Cargar reglas estadísticas
        try:
            stat_module = self._load_module(os.path.join(rules_dir, "statistical_rules.py"), "statistical_rules")
            self.statistical_rules = stat_module.ALL_RULES
            print(f"✅ Cargadas {len(self.statistical_rules)} reglas estadísticas")
        except Exception as e:
            print(f"❌ Error cargando reglas estadísticas: {e}")
            self.statistical_rules = []

        # Combinar todas las reglas
        self.all_rules = (
            self.base_rules +
            self.technical_rules +
            self.cascade_rules +
            self.capability_rules +
            self.ml_traditional_rules +
            self.logic_based_rules +
            self.statistical_rules
        )
        print(f"📊 Total reglas cargadas: {len(self.all_rules)}")
    
    def _load_module(self, file_path: str, module_name: str):
        """Carga dinámicamente un módulo Python desde archivo."""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def apply_rules(self, data_graph: Graph, combined_graph: Graph) -> int:
        """
        Aplica todas las reglas cargadas al grafo de datos.
        
        Args:
            data_graph: Grafo con datos de entrada
            combined_graph: Grafo combinado donde se añaden inferencias
            
        Returns:
            Número de inferencias aplicadas
        """
        inferences_count = 0
        
        # Obtener todos los sistemas inteligentes
        systems = set()
        for system in combined_graph.subjects(RDF.type, AI.IntelligentSystem):
            systems.add(system)
        
        if not systems:
            print("⚠️  No se encontraron sistemas inteligentes para procesar")
            return 0
        
            print(f"🔍 Procesando {len(systems)} sistemas con {len(self.all_rules)} reglas")
            
            # Debug: Imprimir propiedades del sistema para verificar datos técnicos
            for system in systems:
                print(f"🔍 Sistema: {system}")
                for prop, obj in combined_graph.predicate_objects(system):
                    if any(tech in str(prop) for tech in ['FLOP', 'Parameter', 'Accuracy', 'Autonomy', 'Market', 'Adaptive']):
                        print(f"   • {prop}: {obj}")
                break  # Solo el primer sistema        # Aplicar reglas iterativamente hasta que no haya más cambios (máximo 5 iteraciones)
        max_iterations = 5
        for iteration in range(max_iterations):
            iteration_inferences = 0
            print(f"🔄 Iteración {iteration + 1} de reglas...")
            
            # Aplicar cada regla a cada sistema
            rules_applied_this_iteration = 0
            for rule in self.all_rules:
                for system in systems:
                    if self._evaluate_conditions(rule["conditions"], system, combined_graph):
                        applied = self._apply_consequences(rule["consequences"], system, combined_graph, rule["id"])
                        if applied > 0:
                            rules_applied_this_iteration += 1
                        iteration_inferences += applied
                        inferences_count += applied
            
            if iteration == 0:  # Solo en primera iteración
                print(f"🔍 Reglas aplicables encontradas: {rules_applied_this_iteration}/{len(self.all_rules)}")
            
            print(f"📊 Iteración {iteration + 1}: {iteration_inferences} nuevas inferencias")
            
            # Si no se aplicaron nuevas reglas, terminar
            if iteration_inferences == 0:
                print(f"✅ Convergencia alcanzada después de {iteration + 1} iteraciones")
                break
        else:
            print(f"⚠️  Máximo de iteraciones alcanzado ({max_iterations})")
        
        return inferences_count
    
    def _evaluate_conditions(self, conditions: List[Dict], system: URIRef, graph: Graph) -> bool:
        """Evalúa si todas las condiciones de una regla se cumplen para un sistema."""
        for condition in conditions:
            if not self._evaluate_single_condition(condition, system, graph):
                return False
        return True
    
    def _evaluate_single_condition(self, condition: Dict, system: URIRef, graph: Graph) -> bool:
        """Evalúa una sola condición."""
        property_uri = URIRef(condition["property"].replace("ai:", str(AI)))
        operator = condition["operator"]
        expected_value = condition["value"]
        value_type = condition.get("type", "str")
        
        # Obtener valores del grafo
        for _, _, obj in graph.triples((system, property_uri, None)):
            graph_value = self._convert_value(obj, value_type)
            
            if self._compare_values(graph_value, operator, expected_value):
                return True
        
        return False
    
    def _convert_value(self, rdf_value, target_type: str):
        """Convierte un valor RDF al tipo Python especificado."""
        if isinstance(rdf_value, Literal):
            if target_type == "int":
                return int(rdf_value)
            elif target_type == "float":
                return float(rdf_value)
            elif target_type == "bool":
                return bool(rdf_value.value) if hasattr(rdf_value, 'value') else str(rdf_value).lower() == 'true'
            else:
                return str(rdf_value)
        elif isinstance(rdf_value, URIRef):
            if target_type == "uri":
                return str(rdf_value)
            else:
                return str(rdf_value)
        else:
            return str(rdf_value)
    
    def _compare_values(self, graph_value, operator: str, expected_value) -> bool:
        """Compara dos valores usando el operador especificado."""
        try:
            if operator == "==":
                if isinstance(expected_value, str) and expected_value.startswith("ai:"):
                    expected_value = expected_value.replace("ai:", str(AI))
                return str(graph_value) == str(expected_value)
            elif operator == "!=":
                return graph_value != expected_value
            elif operator == ">":
                return graph_value > expected_value
            elif operator == "<":
                return graph_value < expected_value
            elif operator == ">=":
                return graph_value >= expected_value
            elif operator == "<=":
                return graph_value <= expected_value
            elif operator == "in":
                return graph_value in expected_value
            elif operator == "contains":
                return expected_value in graph_value
            else:
                print(f"⚠️  Operador desconocido: {operator}")
                return False
        except Exception as e:
            print(f"⚠️  Error comparando valores: {e}")
            return False
    
    def _apply_consequences(self, consequences: List[Dict], system: URIRef, graph: Graph, rule_id: str) -> int:
        """Aplica las consecuencias de una regla al grafo."""
        applied = 0
        
        for consequence in consequences:
            property_uri = URIRef(consequence["property"].replace("ai:", str(AI)))
            value_str = consequence["value"]
            
            if value_str.startswith("ai:"):
                value_uri = URIRef(value_str.replace("ai:", str(AI)))
            else:
                value_uri = URIRef(value_str)
            
            # Verificar si ya existe esta triple
            if (system, property_uri, value_uri) not in graph:
                graph.add((system, property_uri, value_uri))
                print(f"DEBUG: ✅ Inferencia aplicada ({rule_id}): {system} -> {property_uri.split('#')[-1]} -> {value_uri.split('#')[-1]}")
                applied += 1
        
        return applied
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Retorna un resumen de todas las reglas cargadas."""
        return {
            "total_rules": len(self.all_rules),
            "base_rules": len(self.base_rules),
            "technical_rules": len(self.technical_rules),
            "cascade_rules": len(self.cascade_rules),
            "capability_rules": len(self.capability_rules),
            "ml_traditional_rules": len(self.ml_traditional_rules),
            "logic_based_rules": len(self.logic_based_rules),
            "statistical_rules": len(self.statistical_rules),
            "rules_by_id": {rule["id"]: rule["name"] for rule in self.all_rules}
        }


def load_external_rules_engine():
    """Factory function para crear una instancia del motor de reglas externas."""
    return ExternalRulesEngine()


# Instancia global del motor de reglas
rules_engine = load_external_rules_engine()