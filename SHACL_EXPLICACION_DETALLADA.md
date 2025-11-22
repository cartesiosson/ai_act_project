# 📋 SHACL - Explicación Detallada

## ¿Qué es SHACL?

**SHACL** = **Shapes Constraint Language** (Lenguaje de Restricciones de Formas)

Es un lenguaje W3C estándar para **validar datos RDF** (datos semánticos). Es como un "JSON Schema" pero para datos RDF/Turtle.

```
JSON Schema  → Valida JSON
SHACL        → Valida RDF/Turtle
```

---

## 🎯 Concepto Clave: NodeShape

Una **NodeShape** es una regla de validación que dice: "Los datos de tipo X deben cumplir estas propiedades".

```turtle
# EJEMPLO SIMPLE: NodeShape

ai:IntelligentSystemShape a sh:NodeShape ;
    sh:targetClass ai:IntelligentSystem ;  ← Apunta a qué tipo validar
    sh:property [
        sh:path ai:hasPurpose ;             ← Qué propiedad
        sh:minCount 1 ;                     ← Al menos 1
        sh:message "Error: Sin Purpose"@en  ← Mensaje si falla
    ] .

# Esto valida que TODA instancia de ai:IntelligentSystem
# tenga AT LEAST 1 ai:hasPurpose
```

---

## 📊 Las 7 Shapes que Agregué

### Shape 1: IntelligentSystemShape

```turtle
ai:IntelligentSystemShape a sh:NodeShape ;
    sh:targetClass ai:IntelligentSystem ;
    sh:property [
        sh:path ai:hasName ;
        sh:minCount 1 ;                    ← Debe tener nombre
        sh:maxCount 1 ;                    ← Exactamente 1
    ] ;
    sh:property [
        sh:path ai:hasPurpose ;
        sh:minCount 1 ;                    ← Debe tener ≥1 Purpose
        sh:class ai:Purpose ;              ← Debe ser instancia de Purpose
    ] ;
    sh:property [
        sh:path ai:hasDeploymentContext ;
        sh:minCount 1 ;                    ← Debe tener ≥1 contexto
    ] ;
    sh:property [
        sh:path ai:hasTrainingDataOrigin ;
        sh:minCount 1 ;                    ← Debe declarar origen datos
    ] .
```

**Valida:** La completitud básica de un sistema IA

---

### Shape 2: PurposeShape

```turtle
ai:PurposeShape a sh:NodeShape ;
    sh:targetClass ai:Purpose ;
    sh:property [
        sh:path ai:activatesCriterion ;
        sh:minCount 1 ;                    ← Purpose debe activar ≥1 Criterion
    ] ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 2 ;                    ← Debe tener ≥2 idiomas (EN + ES)
    ] .
```

**Valida:** Que todo propósito está documentado y activa criterios

---

### Shape 3: CriterionShape

```turtle
ai:CriterionShape a sh:NodeShape ;
    sh:targetClass ai:Criterion ;
    sh:property [
        sh:path ai:assignsRiskLevel ;
        sh:minCount 1 ;
        sh:maxCount 1 ;                    ← Exactamente 1 RiskLevel
    ] ;
    sh:property [
        sh:path ai:activatesRequirement ;
        sh:minCount 1 ;                    ← Activa ≥1 Requirement
    ] .
```

**Valida:** La integridad de criterios

---

### Shape 4: ComplianceRequirementShape

```turtle
ai:ComplianceRequirementShape a sh:NodeShape ;
    sh:targetClass ai:ComplianceRequirement ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 2 ;                    ← EN + ES
    ] ;
    sh:property [
        sh:path rdfs:comment ;
        sh:minCount 1 ;                    ← Debe estar documentado
    ] .
```

**Valida:** Documentación de requisitos

---

### Shape 5: RiskLevelShape

```turtle
ai:RiskLevelShape a sh:NodeShape ;
    sh:targetClass ai:RiskLevel ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 2 ;                    ← EN + ES
    ] ;
    sh:property [
        sh:path rdfs:comment ;
        sh:minCount 1 ;
    ] .
```

**Valida:** Que niveles de riesgo estén bien documentados

---

### Shape 6: AnnexIIICoverageShape

```turtle
ai:AnnexIIICoverageShape a sh:NodeShape ;
    sh:targetClass ai:Purpose ;
    # Verifica que existan todos 9 puntos del Anexo III
    # - EducationAccess
    # - RecruitmentOrEmployment
    # - JudicialDecisionSupport
    # - Etc.
```

**Valida:** Cobertura completa del Anexo III

---

### Shape 7: MultilingualDocShape

```turtle
ai:MultilingualDocShape a sh:NodeShape ;
    # Valida documentación EN/ES en conceptos clave
```

**Valida:** Que documentación está en múltiples idiomas

---

## 🔄 Cómo Funciona la Validación

### Paso 1: Cargar Datos a Validar

```python
# Tu sistema IA convertido a RDF
data_graph = Graph()
data_graph.parse(data=sistema_ttl, format="ttl")

# Datos cargados:
<urn:uuid:system-123> a ai:IntelligentSystem ;
    ai:hasName "Mi Sistema" ;
    ai:hasPurpose ai:RecruitmentOrEmployment ;
    ai:hasTrainingDataOrigin ai:PublicData .
```

### Paso 2: Cargar SHACL Shapes

```python
# Reglas de validación
shapes_graph = Graph()
shapes_graph.parse("shacl/ai-act-shapes.ttl")

# Shapes cargados:
ai:IntelligentSystemShape a sh:NodeShape ;
    sh:targetClass ai:IntelligentSystem ;
    sh:property [ sh:path ai:hasPurpose ; sh:minCount 1 ] ;
    ...
```

### Paso 3: Ejecutar Validación

```python
from pyshacl import validate

conforms, report_graph, report_text = validate(
    data_graph,
    shapes_graph=shapes_graph
)

# conforms = True/False
# report_graph = RDF con detalles
# report_text = Texto legible
```

### Paso 4: Procesar Resultado

```python
if conforms:
    print("✅ Datos válidos")
else:
    print("❌ Datos inválidos")
    print(report_text)
    # Ejemplo de reporte:
    # Violation Details for http://data/system-123
    # Conforms: false
    # IntelligentSystem must have at least one hasPurpose
    # linked to a Purpose.
```

---

## 📋 Ejemplo Práctico Completo

### Sistema Válido ✅

```turtle
# DATOS
<urn:uuid:valid-system> a ai:IntelligentSystem ;
    ai:hasName "Healthcare AI" ;
    ai:hasPurpose ai:HealthCare ;
    ai:hasDeploymentContext ai:HighVolumeProcessing ;
    ai:hasTrainingDataOrigin ai:PublicData .

ai:HealthCare a ai:Purpose ;
    rdfs:label "Healthcare"@en, "Salud"@es ;
    ai:activatesCriterion ai:PrivacyProtectionCriterion .

ai:PrivacyProtectionCriterion a ai:Criterion ;
    ai:assignsRiskLevel ai:HighRisk ;
    ai:activatesRequirement ai:PrivacyRequirement .

# VALIDACIÓN CON SHAPES
ai:IntelligentSystemShape a sh:NodeShape ;
    sh:targetClass ai:IntelligentSystem ;
    sh:property [
        sh:path ai:hasPurpose ;
        sh:minCount 1   ← ✅ Tiene 1 (Healthcare)
    ] ;
    sh:property [
        sh:path ai:hasDeploymentContext ;
        sh:minCount 1   ← ✅ Tiene 1 (HighVolumeProcessing)
    ] ;
    sh:property [
        sh:path ai:hasTrainingDataOrigin ;
        sh:minCount 1   ← ✅ Tiene 1 (PublicData)
    ] .

RESULTADO: ✅ Válido (conforms = true)
```

### Sistema Inválido ❌

```turtle
# DATOS
<urn:uuid:invalid-system> a ai:IntelligentSystem ;
    ai:hasName "Bad System" ;
    # ⚠️ SIN hasPurpose
    # ⚠️ SIN hasDeploymentContext
    # ⚠️ SIN hasTrainingDataOrigin
    .

# VALIDACIÓN
ai:IntelligentSystemShape exige:
    sh:property [ sh:path ai:hasPurpose ; sh:minCount 1 ]
    → ❌ FALTA

    sh:property [ sh:path ai:hasDeploymentContext ; sh:minCount 1 ]
    → ❌ FALTA

    sh:property [ sh:path ai:hasTrainingDataOrigin ; sh:minCount 1 ]
    → ❌ FALTA

RESULTADO: ❌ Inválido (conforms = false)

REPORTE:
Violation Details for <urn:uuid:invalid-system>
Conforms: false

- IntelligentSystem must have at least one hasPurpose
- IntelligentSystem must declare at least one hasDeploymentContext
- IntelligentSystem must declare training data origin
```

---

## 🎯 Propiedades SHACL Comunes

| Propiedad | Significado | Ejemplo |
|-----------|------------|---------|
| `sh:targetClass` | Qué clase validar | `ai:IntelligentSystem` |
| `sh:path` | Qué propiedad | `ai:hasPurpose` |
| `sh:minCount` | Mínimo | `sh:minCount 1` (≥1) |
| `sh:maxCount` | Máximo | `sh:maxCount 1` (≤1) |
| `sh:class` | Debe ser instancia de | `sh:class ai:Purpose` |
| `sh:datatype` | Tipo de dato | `xsd:string` |
| `sh:message` | Mensaje error | `"Error message"@en` |
| `sh:nodeKind` | Forma del nodo | `sh:IRI` (debe ser URI) |

---

## 🔌 Cómo Integrar en reasoning.py

### Opción A: PRE-validación (Antes de razonamiento)

```python
def validate_system_pre(system_ttl: str) -> bool:
    """Valida datos ANTES de razonamiento"""

    # Cargar datos
    data_graph = Graph()
    data_graph.parse(data=system_ttl, format="ttl")

    # Cargar shapes
    shapes_graph = Graph()
    shapes_graph.parse("ontologias/shacl/ai-act-shapes.ttl")

    # Validar
    conforms, report_graph, report_text = validate(
        data_graph,
        shapes_graph=shapes_graph
    )

    if not conforms:
        raise ValidationError(f"Sistema incumple requisitos:\n{report_text}")

    return True


# EN API
@router.post("/reasoning/evaluate")
async def evaluate_system(system: dict):
    system_ttl = system_to_ttl(system)

    # PRE-VALIDACIÓN
    validate_system_pre(system_ttl)  # Lanza error si falla

    # Si llegó aquí, está válido
    # Continúa con razonamiento normal...
    results = perform_reasoning(system_ttl)

    return results
```

---

### Opción B: POST-validación (Después de razonamiento)

```python
def validate_results_post(results_graph: Graph) -> dict:
    """Valida resultados DESPUÉS de razonamiento"""

    # Cargar shapes
    shapes_graph = Graph()
    shapes_graph.parse("ontologias/shacl/ai-act-shapes.ttl")

    # Validar
    conforms, report_graph, report_text = validate(
        results_graph,
        shapes_graph=shapes_graph
    )

    return {
        "valid": conforms,
        "message": report_text if not conforms else "Válido"
    }


# EN API
@router.post("/reasoning/evaluate")
async def evaluate_system(system: dict):
    system_ttl = system_to_ttl(system)
    results_graph = perform_reasoning(system_ttl)

    # POST-VALIDACIÓN
    validation = validate_results_post(results_graph)

    return {
        "results": results_graph.serialize(format="json-ld"),
        "validation": validation
    }
```

---

### Opción C: AMBAS (Pre + Post)

```python
@router.post("/reasoning/evaluate")
async def evaluate_system(system: dict):
    system_ttl = system_to_ttl(system)

    # 1. PRE-validación
    validate_system_pre(system_ttl)

    # 2. Razonamiento
    results_graph = perform_reasoning(system_ttl)

    # 3. POST-validación
    validation = validate_results_post(results_graph)

    return {
        "results": results_graph.serialize(),
        "validation": validation
    }
```

---

## 🚀 Ventajas de SHACL

| Ventaja | Descripción |
|---------|------------|
| **Automático** | Valida sin lógica manual |
| **Declarativo** | Define Qevolutionarily, no cómo |
| **Reutilizable** | Define una vez, usa en varios lugares |
| **Multilingüe** | Mensajes en EN/ES |
| **Estándar W3C** | No es propietario |
| **Integrable** | Funciona con cualquier RDF |

---

## ⚠️ Consideraciones Importantes

### 1. SHACL NO cambia datos

```python
# SHACL valida, no modifica
data_graph = Graph()
data_graph.parse(...)

validate(data_graph, shapes_graph=shapes_graph)
# ✅ Valida
# ❌ NO modifica data_graph
```

### 2. SWRL vs SHACL

```
SWRL:  IF (condición) THEN (acción) → GENERA criterios nuevos
SHACL: IF (no cumple restricción) THEN ERROR → RECHAZA datos
```

### 3. Rendimiento

- Validación pequeña (~KB): < 100ms
- Validación mediana (~MB): 100-500ms
- Validación grande (GB): segundos

Tu caso: Datos pequeños → muy rápido

---

## 📊 Flujo Completo con SHACL

```
┌─────────────────────────────────────────────────────┐
│ 1. ENTRADA: Sistema IA (JSON)                       │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│ 2. CONVERSIÓN: system_to_ttl()                      │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│ 3. PRE-VALIDACIÓN: validate_system_pre()            │
│    ✅ ¿Tiene Purpose? ¿DataOrigin? ¿DeployContext?│
└──────────────┬──────────────────────────────────────┘
               ↓ Si pasa
┌─────────────────────────────────────────────────────┐
│ 4. RAZONAMIENTO: Jena Fuseki (SWRL rules)           │
│    ✅ Ejecuta 12 reglas SWRL                        │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│ 5. POST-VALIDACIÓN: validate_results_post()         │
│    ✅ ¿Cada Criterion tiene 1 RiskLevel?           │
│    ✅ ¿Documentación EN/ES?                        │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│ 6. RESULTADO: JSON + validation_report              │
└─────────────────────────────────────────────────────┘
```

---

## 🎓 Resumen

**SHACL = Validador de datos RDF**

- Define restricciones (NodeShapes)
- Ejecuta validación (pyshacl)
- Genera reportes bilingües
- Se integra pre/durante/post razonamiento
- NO modifica datos (solo valida)
- Complementa a SWRL (no lo reemplaza)

Generado: 22 Nov 2025 | SHACL Explicación Detallada
