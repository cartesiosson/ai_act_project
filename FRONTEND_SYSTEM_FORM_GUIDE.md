# 📋 Sistema Completo de Registro de Sistemas de IA - Guía Frontend

**Fecha:** 22 Nov 2025
**Versión:** v0.37.2 (Ontología Consolidada)
**Status:** ✅ **Completamente Funcional**

---

## 📌 Resumen Ejecutivo

El sistema de registro de sistemas de IA (SystemsPage + SystemCard) ha sido completamente rediseñado para soportar **todos los conceptos** de la ontología consolidada v0.37.2. Ahora puede registrarse un sistema de IA con información completa sobre:

- ✅ Propiedades básicas (nombre, versión)
- ✅ Propósitos y contextos de despliegue
- ✅ Origen de datos de entrenamiento
- ✅ Tipos y escalas de algoritmos
- ✅ Clasificación GPAI (Artículos 51-55)
- ✅ Criterios contextuales (vulnerabilidad, impacto sistémico)
- ✅ Requisitos de cumplimiento (técnico, seguridad, robustez, documentación, gobernanza de datos)
- ✅ Mapeos a estándares internacionales (ISO 42001, NIST AI RMF)
- ✅ Requerimientos de supervisión humana y derechos fundamentales

---

## 🎯 Estructura del Formulario

El formulario está organizado en **6 secciones principales** con separadores visuales:

### 1️⃣ Información Básica del Sistema
**Ubicación:** Arriba del formulario
**Campos obligatorios:**
- `System Name` (texto) - Nombre del sistema
- `Version` (texto) - Versión (ej: 1.0.0)

**Campos opcionales:**
- Auto-generado: `URN` (identificador único)

```jsx
// El URN se genera automáticamente en el backend
// Formato: urn:ai-act:system:GUID:v{version}
```

---

### 2️⃣ Propiedades Fundamentales del Sistema
**Ubicación:** Segunda sección (2x2 grid)
**Campos (todos multi-selección):**

| Campo | Descripción | Valor |
|-------|-------------|-------|
| `Purpose(s)` | Propósitos regulados bajo AI Act Annex III | array[string] |
| `Deployment Context(s)` | Contextos de despliegue (Healthcare, Education, etc) | array[string] |
| `Training Data Origin(s)` | Origen de datos de entrenamiento (Public, Private, Synthetic) | array[string] |
| `System Capability Criteria` | Criterios de capacidad del sistema | array[string] |

**Ejemplo:**
```
Purpose(s): BiometricIdentification, FacialRecognition
Deployment Context(s): LawEnforcement, PublicServices
Training Data Origin(s): PublicData, SyntheticData
```

---

### 3️⃣ Algoritmo & Capacidades del Modelo
**Ubicación:** Tercera sección (2x2 grid)
**Campos:**

| Campo | Descripción | Tipo |
|-------|-------------|------|
| `Algorithm Types` | Tipos de algoritmo (Neural Network, Transformer, etc) | array[string] |
| `Model Scale` | Escala del modelo (Foundation Model Scale, etc) | array[string] |
| `System Capabilities` | Capacidades del sistema (Generative, etc) | array[string] |

**Ejemplo:**
```
Algorithm Types: NeuralNetwork, TransformerModel
Model Scale: FoundationModelScale
System Capabilities: GenerativeCapability, TextGeneration
```

---

### 4️⃣ Clasificación EU AI Act
**Ubicación:** Cuarta sección (después de separador de línea)
**Campos:**

| Campo | Descripción | Tipo |
|-------|-------------|------|
| `GPAI Classification` | Clasificación GPAI (Articles 51-55) | array[string] |
| `Contextual Criteria` | Criterios contextuales (vulnerabilidad, impacto) | array[string] |

**Conceptos GPAI disponibles:**
- `GeneralPurposeAIModel` - Modelo de IA de propósito general básico
- `HighCapabilityGPAIModel` - GPAI de alta capacidad (Articles 52-55)

**Criterios contextuales (ejemplos):**
- `ChildrenAndMinorsVulnerabilityContext` - Sistemas que afecten a menores
- `ElderlyAndDisabledVulnerabilityContext` - Sistemas que afecten a adultos mayores
- `MisinformationAmplificationRiskContext` - Riesgo de amplificación de desinformación
- `AutonomyAndControlLimitationContext` - Limitación de autonomía/control
- `SystemicImpactContext` - Impacto sistémico en la sociedad

**Ejemplo:**
```
GPAI Classification: GeneralPurposeAIModel, HighCapabilityGPAIModel
Contextual Criteria: MisinformationAmplificationRiskContext, ChildrenAndMinorsVulnerabilityContext
```

---

### 5️⃣ Requisitos de Cumplimiento
**Ubicación:** Quinta sección (grid 1x5)
**Campos (todos multi-selección):**

| Campo | Descripción |
|-------|-------------|
| `Technical Requirements` | Requisitos técnicos del AI Act |
| `Security Requirements` | Requisitos de seguridad (robustez, adversarial) |
| `Robustness Requirements` | Requisitos de robustez y fiabilidad |
| `Documentation Requirements` | Requisitos de documentación |
| `Data Governance Requirements` | Requisitos de gobernanza de datos |

**Ejemplo:**
```
Technical Requirements: ModelDocumentation, RiskAssessment, TestingValidation
Security Requirements: AdversarialRobustness, DataSecurityProtocols
Robustness Requirements: InputValidation, ErrorHandling, FailsafeMechanisms
Documentation Requirements: TechnicalDocumentation, UserDocumentation
Data Governance Requirements: DataQualityFramework, DataRetention, DataDeletion
```

---

### 6️⃣ Estándares & Marcos Internacionales
**Ubicación:** Sexta sección
**Campos (todos multi-selección):**

| Campo | Descripción |
|-------|-------------|
| `ISO 42001 Requirements` | Requisitos de ISO 42001 (AI Management System) |
| `NIST AI RMF Functions` | Funciones NIST AI Risk Management Framework |

**Conceptos ISO 42001:**
- `ISO42001SecureAPIDesign`
- `ISO42001DataMinimization`
- `ISO42001TransparencyDocumentation`
- `ISO42001HumanReviewProcess`

**Funciones NIST RMF:**
- `NISTGovernanceFunction` - Governance
- `NISTMapandMeasureFunction` - Map and Measure
- `NISTManageRisksFunction` - Manage Risks
- `NISTMeasureFunction` - Measure

**Ejemplo:**
```
ISO 42001 Requirements: ISO42001SecureAPIDesign, ISO42001DataMinimization
NIST AI RMF Functions: NISTGovernanceFunction, NISTMapandMeasureFunction, NISTManageRisksFunction
```

---

### 7️⃣ Supervisión Humana & Derechos Fundamentales
**Ubicación:** Séptima sección (grid 1x3)
**Campos:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Requires Human Oversight` | boolean (checkbox) | ¿Requiere supervisión humana? |
| `Fundamental Rights Assessment` | boolean (checkbox) | ¿Requiere evaluación de derechos fundamentales? |
| `Transparency Level` | select (High/Medium/Low) | Nivel de transparencia requerido |

**Ejemplo:**
```
Requires Human Oversight: ✓ (checked)
Fundamental Rights Assessment: ✓ (checked)
Transparency Level: High
```

---

## 📊 Vista de Tarjeta (SystemCard)

Después de crear/cargar un sistema, la tarjeta muestra **todas las propiedades** organizadas en secciones:

```
┌─────────────────────────────────────────────────────┐
│ System Name                                         │
│ URN: urn:ai-act:system:... (pequeño, gris)        │
├─────────────────────────────────────────────────────┤
│ Risk Level: HighRisk                                │
│ GPAI Classification: GeneralPurposeAIModel          │
├─────────────────────────────────────────────────────┤
│ Purpose(s): BiometricIdentification, ...            │
│ Deployment Context(s): LawEnforcement, ...          │
│ Training Data Origin(s): PublicData, ...            │
│ System Capabilities: NeuralNetwork, ...             │
├─────────────────────────────────────────────────────┤
│ Algorithm Type(s): TransformerModel, ...            │
│ Model Scale: FoundationModelScale                   │
│ Capabilities: GenerativeCapability, ...             │
├─────────────────────────────────────────────────────┤
│ Contextual Criteria: MisinformationAmplification... │
├─────────────────────────────────────────────────────┤
│ COMPLIANCE REQUIREMENTS:                             │
│   Technical: ModelDocumentation, ...                │
│   Security: AdversarialRobustness, ...              │
│   Robustness: InputValidation, ...                  │
│   Documentation: TechnicalDocumentation, ...        │
│   Data Governance: DataQualityFramework, ...        │
├─────────────────────────────────────────────────────┤
│ STANDARDS & FRAMEWORKS:                             │
│   ISO 42001: ISO42001SecureAPIDesign, ...           │
│   NIST AI RMF: NISTGovernanceFunction, ...          │
├─────────────────────────────────────────────────────┤
│ Human Oversight: Required | Fundamental Rights: Yes │
│ Transparency Level: High                            │
├─────────────────────────────────────────────────────┤
│ Version: 1.0.0                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Flujos de Uso

### Crear un Nuevo Sistema Completo

1. **Rellenar sección "Información Básica":**
   - System Name: "Facial Recognition System v2"
   - Version: "2.0.0"

2. **Propiedades Fundamentales:**
   - Purpose(s): Select "FacialRecognition", "BiometricIdentification"
   - Deployment Context(s): Select "LawEnforcement"
   - Training Data Origin(s): Select "PublicData", "SyntheticData"
   - System Capability Criteria: Select all relevant

3. **Algoritmo & Modelo:**
   - Algorithm Types: Select "TransformerModel", "DeepNeuralNetwork"
   - Model Scale: Select "FoundationModelScale"

4. **Clasificación AI Act:**
   - GPAI Classification: Select "HighCapabilityGPAIModel"
   - Contextual Criteria: Select "ChildrenAndMinorsVulnerabilityContext", "MisinformationAmplificationRiskContext"

5. **Requisitos de Cumplimiento:**
   - Technical: Select all applicable
   - Security: Select "AdversarialRobustness", "DataSecurityProtocols"
   - Robustness: Select "InputValidation", "FailsafeMechanisms"
   - Documentation: Select "TechnicalDocumentation"
   - Data Governance: Select "DataQualityFramework"

6. **Estándares Internacionales:**
   - ISO 42001: Select "ISO42001SecureAPIDesign", "ISO42001DataMinimization"
   - NIST AI RMF: Select "NISTGovernanceFunction", "NISTMapandMeasureFunction", "NISTManageRisksFunction"

7. **Gobernanza Humana:**
   - ✓ Requires Human Oversight
   - ✓ Fundamental Rights Assessment
   - Transparency Level: "High"

8. **Crear Sistema:**
   - Click "Create System" button
   - Sistema se registra en base de datos
   - Tarjeta aparece en lista de sistemas

### Cargar y Modificar un Sistema Existente

1. **En la tabla de sistemas, click "Load"** en el sistema a modificar
2. **Modal de confirmación** advierte que se perderán datos del formulario actual
3. **Click "Proceed"** carga todos los datos del sistema en el formulario
4. **Editar campos deseados** (todos los campos son editables)
5. **Click "Modify System"** para guardar cambios
6. **O click "Clear Form"** para descartar cambios

### Filtrar Sistemas

En la sección de filtros (debajo del formulario):
- **Filtrar por nombre** (búsqueda de texto)
- **Filtrar por Risk Level** (dropdown)
- **Filtrar por Purpose** (dropdown)
- **Filtrar por Deployment Context** (dropdown)
- **Filtrar por Training Data Origin** (dropdown)

---

## 🔌 Integración Backend

El frontend espera que estos **endpoints de vocabulario** estén implementados en el backend:

```
GET /vocab/purposes?lang=en
GET /vocab/risks?lang=en
GET /vocab/contexts?lang=en
GET /vocab/training_origins?lang=en
GET /vocab/system_capability_criteria?lang=en
GET /vocab/algorithmtypes?lang=en
GET /vocab/modelscales?lang=en
GET /vocab/capabilities?lang=en
GET /vocab/gpai?lang=en                    ← NEW
GET /vocab/contextualcriteria?lang=en      ← NEW
GET /vocab/compliance?lang=en               ← NEW
GET /vocab/technical?lang=en                ← NEW
GET /vocab/security?lang=en                 ← NEW
GET /vocab/robustness?lang=en               ← NEW
GET /vocab/documentation?lang=en            ← NEW
GET /vocab/datagovernance?lang=en           ← NEW
GET /vocab/iso?lang=en                      ← NEW
GET /vocab/nist?lang=en                     ← NEW
GET /vocab/transparency?lang=en             ← NEW
```

**Formato de respuesta esperado:**
```json
[
  {"id": "ai:GeneralPurposeAIModel", "label": "General Purpose AI"},
  {"id": "ai:HighCapabilityGPAIModel", "label": "High Capability GPAI"},
  ...
]
```

**Rutas CRUD del sistema:**
```
POST   /systems              - Crear nuevo sistema
GET    /systems?...          - Listar sistemas (con paginación/filtros)
GET    /systems/{urn}        - Obtener sistema por URN
PUT    /systems/{urn}        - Modificar sistema existente
DELETE /systems/{urn}        - Eliminar sistema
GET    /systems/{urn}/validate  - Validar sistema con SHACL
```

---

## 📱 Diseño Responsivo

El formulario utiliza **Tailwind CSS grid** con breakpoints:

```
grid-cols-1              # Mobile (< 768px): 1 columna
md:grid-cols-2           # Tablet/Desktop (≥ 768px): 2 columnas
md:grid-cols-3           # Para secciones específicas: 3 columnas
```

**Comportamiento responsivo:**
- **Mobile:** Campo por fila, formulario vertical
- **Tablet:** 2 campos por fila, mejor aprovechamiento de espacio
- **Desktop:** 2-3 campos por fila, layout horizontal optimizado

---

## 🎨 Estilos & Temas

- **Colores:** Implementado tema claro/oscuro con `dark:` prefix
- **Inputs:** Fondos blancos (light) / gris oscuro (dark)
- **Text:** Negro (light) / blanco (dark)
- **Bordes:** Grises estándar (light) / grises oscuros (dark)
- **Botones:** Azul (create), Gris (clear), Rojo (delete), Verde (load)

```jsx
// Ejemplo de elemento con soporte dark mode
<select className="w-full border rounded p-2 bg-white text-black dark:bg-gray-800 dark:text-white">
  {/* opciones */}
</select>
```

---

## 💾 Persistencia de Datos

**Guardar sistema:**
```javascript
POST /systems
{
  "@context": "http://ontologias/json-ld-context.json",
  "@type": "ai:IntelligentSystem",
  "hasName": "My System",
  "hasPurpose": ["ai:Purpose1", "ai:Purpose2"],
  "hasDeploymentContext": [...],
  // ... todos los demás campos
}
```

**Base de datos:**
- Almacenada en MongoDB
- Indexada por URN (`ai:hasUrn`)
- Soporta versionado
- Validada con SHACL en backend

---

## 🔍 Validación

**Frontend:**
- Campo `System Name` obligatorio (no submit sin nombre)
- Campos adicionales opcionales

**Backend (SHACL):**
- Valida estructura RDF
- Valida cardinalidades de propiedades
- Valida tipos de clases
- Retorna errores con mensajes descriptivos

---

## 🚀 Roadmap Futuro

**Posibles mejoras:**
- [ ] Drag & drop para reordenar campos
- [ ] Tabs para secciones del formulario
- [ ] Vista previa en tiempo real
- [ ] Exportar sistema como RDF/Turtle
- [ ] Importar sistemas desde archivo
- [ ] Búsqueda avanzada con filtros múltiples
- [ ] Histórico de cambios/versiones
- [ ] Compartir sistemas entre usuarios
- [ ] Plantillas de sistemas comunes
- [ ] Validación visual en tiempo real

---

## 📚 Véase También

- [QUICK_START.md](QUICK_START.md) - Guía de inicio rápido
- [ARCHITECTURE_SHACL.md](ARCHITECTURE_SHACL.md) - Arquitectura del sistema
- [ontologia-v0.37.2.ttl](ontologias/versions/0.37.2/ontologia-v0.37.2.ttl) - Ontología consolidada
- [SESSION_SUMMARY.md](SESSION_SUMMARY.md) - Resumen de la sesión

---

## ❓ Preguntas Frecuentes

**P: ¿Cómo agregar más campos al formulario?**
R: Editar SystemsPage.tsx, agregar nuevo state, field en form, y endpoint en useEffect.

**P: ¿Por qué algunos campos aparecen vacíos?**
R: Si el endpoint backend retorna vacío o error, se muestran las opciones por defecto.

**P: ¿Puedo multi-seleccionar en cualquier campo?**
R: Sí, todos los campos con `<select multiple>` permiten Ctrl+Click para multi-selección.

**P: ¿Se guarda el borrador automáticamente?**
R: No, solo se guarda al hacer click en "Create System" o "Modify System".

**P: ¿Qué pasa si cierro el navegador sin guardar?**
R: Los datos se pierden (no hay persistencia local).

---

## ✅ Checklist de Implementación

```
[x] SystemCard expandido con 26 propiedades
[x] SystemsPage con soporte para 32 propiedades
[x] 4 nuevas secciones de formulario
[x] 11 nuevos endpoints de vocabulario
[x] Diseño responsivo completado
[x] Tema claro/oscuro soportado
[x] Validación básica implementada
[x] Documentación completada
```

---

**Versión:** 1.0.0
**Fecha:** 22 Nov 2025
**Estado:** ✅ **LISTO PARA PRODUCCIÓN**

🎉 **El sistema de registro de sistemas de IA está completo y funcional con soporte para todos los conceptos de la ontología v0.37.2**
