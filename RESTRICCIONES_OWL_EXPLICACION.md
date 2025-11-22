# 🔒 Restricciones OWL - Cuándo se Ejecutan

## Respuesta Directa

Las restricciones OWL **NO se ejecutan "durante" el razonamiento SWRL**. Se ejecutan en **momentos específicos** dependiendo de cuándo valides:

```
┌─────────────────────────────────────────────────────────┐
│         LÍNEA DE TIEMPO DE EJECUCIÓN                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. ANTES DEL RAZONAMIENTO (OPCIONAL)                   │
│    └─→ Validar datos de entrada con OWL restrictions   │
│        ¿Sistema tiene ≥1 Purpose? ¿≥1 DataOrigin?      │
│                                                         │
│ 2. DURANTE EL RAZONAMIENTO (SWRL)                      │
│    └─→ Reglas SWRL ejecutan (12 reglas)                │
│        ⚠️ OWL restrictions NO interfieren aquí          │
│                                                         │
│ 3. DESPUÉS DEL RAZONAMIENTO (OPCIONAL)                 │
│    └─→ Validar resultados con OWL restrictions        │
│        ¿Cada Criterion tiene 1 RiskLevel?              │
│        ¿Cada Requirement está documentado?             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Las Restricciones OWL NO Son Reglas SWRL

Esta es la diferencia clave:

| Aspecto | SWRL Rules (Existentes) | OWL Restrictions (Nuevas) |
|--------|-------------------------|--------------------------|
| **Tipo** | Reglas de inferencia | Restricciones/Validación |
| **Ejecuta** | Razonamiento activo | Validación pasiva |
| **Cuándo** | Durante razonamiento | Cuando ejecutas validador |
| **Ejemplo** | IF Recruitment THEN NonDiscrimination | IntelligentSystem DEBE tener ≥1 Purpose |
| **Efecto** | Agrega criterios nuevos | Detecta violaciones |
| **En reasoning.py** | Auto-ejecuta cada vez | Solo si lo llamas |

---

## 📊 Comparación Visual

### SWRL Rules (Ya tienes 12)

```
┌──────────────────────────────────────────┐
│  SISTEMA IA (Entrada)                    │
│  Purpose: RecruitmentOrEmployment        │
└──────────────────────────────────────────┘
                  ↓
         [REGLA SWRL 2 EJECUTA]
         IF Purpose = Recruitment
         THEN add NonDiscrimination
                  ↓
┌──────────────────────────────────────────┐
│  SISTEMA IA (Salida)                     │
│  Purpose: RecruitmentOrEmployment        │
│  hasNormativeCriterion: NonDiscrimination│  ← AGREGADO
└──────────────────────────────────────────┘

🔄 AUTO-EJECUTA cada vez que pasas datos
✅ Genera criterios nuevos automáticamente
```

### OWL Restrictions (Nuevas en v0.37.1)

```
┌──────────────────────────────────────────┐
│  SISTEMA IA (Datos)                      │
│  Purpose: RecruitmentOrEmployment        │
│  hasPurpose: [VACÍO]  ← PROBLEMA         │
└──────────────────────────────────────────┘
                  ↓
    [VALIDADOR OWL EJECUTA (OPCIONAL)]
    ¿IntelligentSystem tiene ≥1 Purpose?
    ❌ NO CUMPLE → Error/Advertencia
                  ↓
┌──────────────────────────────────────────┐
│  REPORTE DE VALIDACIÓN                   │
│  ❌ Violación: hasPurpose minCardinality │
│  Message: "System must have at least 1   │
│           Purpose"                       │
└──────────────────────────────────────────┘

⏸️ NO AUTO-EJECUTA (debes llamarlo)
✅ Detecta problemas en datos
```

---

## 🔍 Restricciones OWL Que Agregué

```turtle
# RESTRICCIÓN 1: IntelligentSystem
ai:IntelligentSystem rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ai:hasPurpose ;
    owl:minCardinality 1  ← Debe tener ≥1
]

# RESTRICCIÓN 2: IntelligentSystem
ai:IntelligentSystem rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ai:hasTrainingDataOrigin ;
    owl:minCardinality 1  ← Debe tener ≥1
]

# RESTRICCIÓN 3: Purpose
ai:Purpose rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ai:activatesCriterion ;
    owl:minCardinality 1  ← Cada Purpose debe activar ≥1
]

# RESTRICCIÓN 4: Criterion
ai:Criterion rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ai:assignsRiskLevel ;
    owl:minCardinality 1 ;    ← Exactamente 1
    owl:maxCardinality 1      ← No más de 1
]
```

---

## ⏱️ CUÁNDO SE EJECUTAN (En Detalle)

### Escenario 1: SIN Validación (Actual v0.37.0 y v0.37.1 sin validador)

```
┌─────────────────────────────────────────────────────────┐
│  TU FLUJO ACTUAL                                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Sistema IA (JSON) llega a /reasoning API            │
│                                                         │
│ 2. system_to_ttl() convierte a Turtle                  │
│    {                                                    │
│      "hasPurpose": [],  ← VACÍO (incorrecto)          │
│    }                                                    │
│    →                                                    │
│    <urn:uuid:123> ai:IntelligentSystem ;              │
│    [SIN hasPurpose]  ← OWL restriction INCUMPLIDA      │
│                                                         │
│ 3. Reasoner (Jena) recibe TTL                          │
│    ⚠️ Jena NO valida OWL restrictions por defecto     │
│    Solo ejecuta SWRL rules                             │
│                                                         │
│ 4. Resultado: JSON devuelto                            │
│    {                                                    │
│      "hasPurpose": [],  ← Vacío, pero no error         │
│      "criteria": [...]  ← SWRL ejecutó igual           │
│    }                                                    │
│                                                         │
│ ⚠️ OWL RESTRICTIONS NO EJECUTARON                      │
│    (No hay validador activo)                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Escenario 2: CON Validación (v0.37.1 + SHACL shapes)

```
┌─────────────────────────────────────────────────────────┐
│  FLUJO MEJORADO (CON VALIDACIÓN OPCIONAL)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Sistema IA (JSON) llega a /reasoning API            │
│                                                         │
│ 2. PRE-VALIDACIÓN (NUEVO - OPCIONAL)                  │
│    if VALIDATION_ENABLED:                              │
│        validate_with_shacl(data)                       │
│        → ¿hasPurpose vacío?                            │
│        → ❌ Error: "Must have ≥1 Purpose"              │
│        → DETENER aquí                                  │
│                                                         │
│ 3. [Si pasa validación] Reasoner ejecuta              │
│                                                         │
│ 4. POST-VALIDACIÓN (NUEVO - OPCIONAL)                 │
│    if VALIDATION_ENABLED:                              │
│        validate_with_shacl(results)                    │
│        → ¿Cada Criterion tiene 1 RiskLevel?           │
│        → ¿Cada Requirement documentado EN/ES?         │
│                                                         │
│ 5. Resultado: JSON + validation_report                 │
│                                                         │
│ ✅ OWL RESTRICTIONS EJECUTARON (En validación)        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Cómo Implementar Validación (Si quieres)

### Opción A: Usar SHACL (Recomendado)

```python
# En reasoning.py (NUEVO - opcional)

from pyshacl import validate

# PRE-VALIDACIÓN
def pre_validate_system(system_data):
    """Validar antes de razonamiento"""

    # Convertir a RDF
    system_ttl = system_to_ttl(system_data)
    data_graph = Graph().parse(data=system_ttl, format="ttl")

    # Cargar SHACL shapes
    shapes_graph = Graph().parse(
        "ontologias/shacl/ai-act-shapes.ttl",
        format="ttl"
    )

    # Validar
    conforms, report_graph, report_text = validate(
        data_graph,
        shapes_graph=shapes_graph,
        inplace=False
    )

    if not conforms:
        raise ValidationError(f"Sistema incumple restricciones:\n{report_text}")

    return True


# POST-VALIDACIÓN
def post_validate_results(results_graph):
    """Validar después de razonamiento"""

    shapes_graph = Graph().parse(
        "ontologias/shacl/ai-act-shapes.ttl",
        format="ttl"
    )

    conforms, report_graph, report_text = validate(
        results_graph,
        shapes_graph=shapes_graph
    )

    return {
        "valid": conforms,
        "report": report_text if not conforms else None
    }


# USAR EN API
@router.post("/reasoning/evaluate")
async def evaluate_system(system: dict):

    # 1. Pre-validar
    if VALIDATION_ENABLED:
        pre_validate_system(system)  # Lanza error si falla

    # 2. Razonamiento normal (SWRL rules ejecutan)
    results = perform_reasoning(system)

    # 3. Post-validar
    if VALIDATION_ENABLED:
        validation_report = post_validate_results(results)
        results["validation"] = validation_report

    return results
```

### Opción B: Usar OWL Reasoner (Con soporte nativo)

```python
# Usar Hermit o Pellet (razonadores OWL que soportan restricciones)

from owlready2 import get_ontology

onto = get_ontology("file:///ontologias/ontologia-v0.37.1.ttl")

# Cargar razonador OWL
with onto:
    sync_reasoner_hermit()  # Valida restricciones OWL automáticamente

# Hermit verificará automáticamente:
# - IntelligentSystem tiene ≥1 hasPurpose?
# - Purpose tiene ≥1 activatesCriterion?
# - Etc.

# Si hay violación, Hermit lo detecta
for inconsistency in onto.inconsistencies():
    print(f"❌ Violación: {inconsistency}")
```

---

## ⏳ Cronología en Tu Flujo Actual

### v0.37.0 (Actual)

```
Tiempo 0: Usuario envía sistema IA
  ↓
Tiempo 1: system_to_ttl() convierte
  ↓
Tiempo 2: Reasoner Jena infiere (SWRL rules)
          ⚠️ NO valida OWL restrictions
  ↓
Tiempo 3: Resultado devuelto (puede tener datos incompletos)
```

### v0.37.1 Sin Activar Validación (Compatible)

```
Tiempo 0: Usuario envía sistema IA
  ↓
Tiempo 1: system_to_ttl() convierte
  ↓
Tiempo 2: Reasoner Jena infiere (SWRL rules)
          ⚠️ OWL restrictions definen estructura, pero no se validan
  ↓
Tiempo 3: Resultado devuelto (igual que v0.37.0)
```

### v0.37.1 CON Validación Activada (Futuro)

```
Tiempo 0: Usuario envía sistema IA
  ↓
Tiempo 0.5: ✅ VALIDACIÓN PRE (OWL restrictions actúan)
            ¿Datos cumplen restricciones básicas?
            ❌ Si NO → Error inmediato
            ✅ Si SÍ → Continúa
  ↓
Tiempo 1: system_to_ttl() convierte
  ↓
Tiempo 2: Reasoner Jena infiere (SWRL rules)
  ↓
Tiempo 2.5: ✅ VALIDACIÓN POST (OWL restrictions actúan)
            ¿Resultados cumplen restricciones?
            ⚠️ Si NO → Warning o error
  ↓
Tiempo 3: Resultado devuelto + validation_report
```

---

## 🎯 Resumen: Cuándo Ejecutan

| Momento | OWL Restrictions | SWRL Rules | Quién controla |
|---------|-----------------|-----------|-----------------|
| **Antes de razonamiento** | ✅ (si usas validador) | ❌ No | Tú (opcional) |
| **Durante razonamiento** | ❌ No interfieren | ✅ Auto-ejecutan | Jena Reasoner |
| **Después de razonamiento** | ✅ (si usas validador) | ❌ No | Tú (opcional) |
| **En v0.37.0** | N/A | ✅ Ejecutan | Jena |
| **En v0.37.1 sin validador** | ❌ Definen, no ejecutan | ✅ Ejecutan | Jena |
| **En v0.37.1 con validador** | ✅ Validan | ✅ Ejecutan | Jena + SHACL |

---

## ⚠️ Importante: NO Son SWRL Rules

Esto es un error común:

```
❌ INCORRECTO:
"Las restricciones OWL se ejecutan como SWRL rules"

✅ CORRECTO:
"Las restricciones OWL definen límites estructurales
que pueden validarse con herramientas como SHACL"
```

Las restricciones OWL son **declarativas** (dicen qué debe cumplirse), no **procedurales** (cómo hacerlo).

---

## 🔧 Estado Actual en Tu Proyecto

```
✅ v0.37.1 tiene restricciones OWL definidas
✅ SHACL shapes están listos para usar
⏸️ Pero NO están activadas automáticamente
⏸️ Tu flujo actual (v0.37.0) NO valida

Para activar validación:
1. Modificar reasoning.py para llamar a validador SHACL
2. Decidir si pre-validar, post-validar, o ambas
3. Decidir nivel de severidad (error o warning)
```

---

## 💡 Recomendación

### Ahora (v0.37.1 sin cambios en código)

```python
# reasoning.py sigue igual
# SWRL rules ejecutan igual
# OWL restrictions existen pero no validan
# Compatibilidad: 100% ✅
```

### Futuro (Cuando quieras mejorar)

```python
# Agregar en reasoning.py:
if ENABLE_OWL_VALIDATION:
    pre_validate_with_shacl()      # Valida entrada
    perform_reasoning()            # SWRL rules
    post_validate_with_shacl()     # Valida salida
```

---

**Generado:** 22 Nov 2025
**Documento:** Explicación de Restricciones OWL
**Versión:** v0.37.1
