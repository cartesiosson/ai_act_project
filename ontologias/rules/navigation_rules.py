# =============================================================
# REGLAS GENÉRICAS DE NAVEGACIÓN DE LA ONTOLOGÍA
# Estas reglas implementan la lógica de inferencia transitiva
# que conecta propiedades del sistema con criterios y requisitos
# (Sincronizadas desde swrl_rules.py)
# =============================================================

# REGLA NAV1: Purpose → activatesCriterion → hasCriteria
# Si un sistema tiene un propósito, y ese propósito activa un criterio,
# entonces el sistema tiene ese criterio
RULE_PURPOSE_CRITERION = {
    "id": "rule_nav_purpose_criterion",
    "name": "Purpose activates criterion derivation",
    "description": "If a system has a purpose that activates a criterion, the system has that criterion",
    "navigation_type": "transitive",
    "source_property": "ai:hasPurpose",
    "link_property": "ai:activatesCriterion",
    "target_property": "ai:hasCriteria"
}

# REGLA NAV2: DeploymentContext → triggersCriterion → hasCriteria
# Si un sistema tiene un contexto de despliegue que dispara un criterio,
# entonces el sistema tiene ese criterio
RULE_CONTEXT_CRITERION = {
    "id": "rule_nav_context_criterion",
    "name": "Context triggers criterion derivation",
    "description": "If a system has a deployment context that triggers a criterion, the system has that criterion",
    "navigation_type": "transitive",
    "source_property": "ai:hasDeploymentContext",
    "link_property": "ai:triggersCriterion",
    "target_property": "ai:hasCriteria"
}

# REGLA NAV3: SystemCapabilityCriteria → hasCriteria
# Los criterios de capacidad del sistema también cuentan como criterios
RULE_CAPABILITY_CRITERION = {
    "id": "rule_nav_capability_criterion",
    "name": "System capability as criterion",
    "description": "System capability criteria are treated as regular criteria",
    "navigation_type": "direct",
    "source_property": "ai:hasSystemCapabilityCriteria",
    "target_property": "ai:hasCriteria"
}

# REGLA NAV4: Criterion → activatesRequirement → hasComplianceRequirement
# Si un sistema tiene un criterio que activa requisitos,
# entonces el sistema tiene esos requisitos
RULE_CRITERION_REQUIREMENT = {
    "id": "rule_nav_criterion_requirement",
    "name": "Criterion activates requirement derivation",
    "description": "If a system has a criterion that activates a requirement, the system has that requirement",
    "navigation_type": "transitive",
    "source_property": "ai:hasCriteria",
    "link_property": "ai:activatesRequirement",
    "target_property": "ai:hasComplianceRequirement"
}

# REGLA NAV5: Criterion → assignsRiskLevel → hasRiskLevel
# Si un criterio asigna un nivel de riesgo, el sistema tiene ese nivel
RULE_CRITERION_RISK = {
    "id": "rule_nav_criterion_risk",
    "name": "Criterion assigns risk level",
    "description": "If a system has a criterion that assigns a risk level, the system has that risk level",
    "navigation_type": "transitive",
    "source_property": "ai:hasCriteria",
    "link_property": "ai:assignsRiskLevel",
    "target_property": "ai:hasRiskLevel"
}

# REGLA NAV6: DataType Processing → triggersDataRequirement → hasDataRequirement
# Si un sistema procesa cierto tipo de datos, hereda los requisitos de ese tipo
RULE_DATA_REQUIREMENT = {
    "id": "rule_nav_data_requirement",
    "name": "Data type triggers data requirement",
    "description": "If a system processes a data type, it inherits requirements for that data type",
    "navigation_type": "transitive",
    "source_property": "ai:processesDataType",
    "link_property": "ai:triggersDataRequirement",
    "target_property": "ai:hasDataRequirement"
}

# Lista de todas las reglas de navegación
NAVIGATION_RULES = [
    RULE_PURPOSE_CRITERION,
    RULE_CONTEXT_CRITERION,
    RULE_CAPABILITY_CRITERION,
    RULE_CRITERION_REQUIREMENT,
    RULE_CRITERION_RISK,
    RULE_DATA_REQUIREMENT
]

# Metadata para documentación
NAVIGATION_RULES_METADATA = {
    "version": "1.0.0",
    "description": "Generic ontology navigation rules for EU AI Act compliance inference",
    "rule_types": {
        "transitive": "Follows a chain: system -> property -> intermediate -> link_property -> target",
        "direct": "Direct copy: system -> source_property -> value becomes system -> target_property -> value"
    },
    "total_rules": len(NAVIGATION_RULES)
}
