# AI Act Project

## 📋 Descripción General

Este proyecto implementa un **sistema completo para la gestión y análisis de sistemas de inteligencia artificial** bajo el marco del AI Act europeo. El sistema incluye:

- 🧠 **Ontología formal** del dominio AI Act
- 🔧 **Servicios de razonamiento semántico** (OWL/SWRL)
- 🌐 **APIs REST** para gestión de datos
- 📊 **Interfaz web interactiva** para visualización y gestión
- 📚 **Documentación automática** de ontologías

## 🚀 Inicio Rápido

### Prerrequisitos
- **Docker** y **Docker Compose**
- **Git**
- Puerto 5173, 8000, 8001, 3030, 27017, 80 disponibles

### Instalación en 3 pasos

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd ai_act_project

# 2. Levantar todos los servicios
docker-compose up -d

# 3. Verificar que todo funciona
docker-compose ps
```

### Acceder a la aplicación
- 🌐 **Frontend**: http://localhost:5173
- 📊 **API Docs**: http://localhost:8000/docs  
- 📚 **Ontología Docs**: http://localhost/docs
- 🔍 **SPARQL Endpoint**: http://localhost:3030

---

## 🛠 Stack Tecnológico

| Capa | Tecnologías |
|------|-------------|
| **🖥️ Frontend** | React 19, TypeScript, Vite, TailwindCSS, D3.js, Vis-network |
| **⚡ Backend** | FastAPI, MongoDB, Apache Jena Fuseki, RDFLib, OwlReady2 |
| **🧠 Semántica** | OWL, SWRL, RDF/Turtle, JSON-LD, SPARQL, AIRO Integration |
| **🐳 Infraestructura** | Docker Compose, Nginx, Widoco |

---

## 🛠 Tecnologías Empleadas

### Backend
- **FastAPI** - Framework web moderno para Python
- **MongoDB** - Base de datos NoSQL para almacenamiento de documentos
- **Apache Jena Fuseki** - Servidor SPARQL y almacén de triples RDF
- **RDFLib** - Biblioteca Python para manejo de datos RDF
- **OwlReady2** - Razonador OWL/SWRL para inferencia semántica
- **Motor** - Driver asíncrono de MongoDB para Python

### Frontend
- **React 19** - Biblioteca de interfaz de usuario
- **TypeScript** - Superset tipado de JavaScript
- **Vite** - Herramienta de build rápida
- **TailwindCSS** - Framework de CSS utilitario
- **D3.js** - Visualización de datos y grafos
- **Vis-network** - Biblioteca para visualización de redes
- **React Router Dom** - Enrutamiento del lado cliente

### Infraestructura
- **Docker & Docker Compose** - Contenerización y orquestación
- **Nginx** - Servidor web para servir documentación
- **Widoco** - Generación automática de documentación de ontologías

### Semántica y Ontologías
- **OWL (Web Ontology Language)** - Lenguaje de ontologías web
- **SWRL (Semantic Web Rule Language)** - Reglas semánticas
- **RDF/Turtle** - Formato de datos semánticos
- **JSON-LD** - Formato JSON para datos enlazados
- **AIRO (AI Risk Ontology)** - Framework internacional de gestión de riesgo de IA

## 📦 Arquitectura del Sistema

### Componentes Principales

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| **Frontend** | `/frontend` | Interfaz React con visualización interactiva |
| **Backend API** | `/backend` | API REST con FastAPI + MongoDB/Fuseki |
| **Ontología** | `/ontologias` | Modelo formal AI Act + documentación |
| **Reasoner** | `/reasoner_service` | Motor de inferencia OWL/SWRL |
| **Herramientas** | `/tools` | Scripts para documentación y validación |

### 🎯 Servicios y Puertos

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| **Frontend** | 5173 | http://localhost:5173 | Interfaz web React |
| **Backend API** | 8000 | http://localhost:8000 | API REST principal |
| **Reasoner** | 8001 | http://localhost:8001 | Servicio de razonamiento |
| **Fuseki** | 3030 | http://localhost:3030 | Servidor SPARQL |
| **MongoDB** | 27017 | mongodb://localhost:27017 | Base de datos documentos |
| **Docs** | 80 | http://localhost/docs | Documentación HTML |


## 🧠 Modelo de Ontología AI Act con AIRO

### Estructura de la Ontología (v0.36.0)

<details>
<summary><strong>🏗️ Diagrama 1: Sistema Central y sus Características</strong></summary>

```mermaid
classDiagram
    %% Sistema central como núcleo
    class IntelligentSystem {
        +hasUrn: string
        +hasName: string
        +hasVersion: string
        +hasPurpose: Purpose
        +hasDeploymentContext: DeploymentContext
        +hasTrainingDataOrigin: TrainingDataOrigin
        +hasRiskLevel: RiskLevel
    }
    
    %% Contextos de despliegue
    class DeploymentContext {
        +contextName: string
        +activatesCriterion: Criterion
    }
    class Healthcare
    class Education
    class PublicServices
    class LawEnforcement
    
    %% Propósitos del sistema
    class Purpose {
        +purposeDescription: string
        +expectedRiskLevel: RiskLevel
    }
    class BiometricIdentification
    class EmotionalRecognition
    class RiskAssessmentPurpose
    
    %% Orígenes de datos de entrenamiento
    class TrainingDataOrigin {
        +dataSource: string
        +requiresDataGovernance: ComplianceRequirement
    }
    class ExternalDataset {
        +provenance: string
    }
    class InternalDataset {
        +dataQuality: string
    }
    class SyntheticDataset {
        +generationMethod: string
    }
    
    %% Relaciones del sistema central
    IntelligentSystem --> Purpose : hasPurpose
    IntelligentSystem --> DeploymentContext : hasDeploymentContext
    IntelligentSystem --> TrainingDataOrigin : hasTrainingDataOrigin
    
    %% Jerarquías
    DeploymentContext <|-- Healthcare
    DeploymentContext <|-- Education
    DeploymentContext <|-- PublicServices
    DeploymentContext <|-- LawEnforcement
    
    Purpose <|-- BiometricIdentification
    Purpose <|-- EmotionalRecognition
    Purpose <|-- RiskAssessmentPurpose
    
    TrainingDataOrigin <|-- ExternalDataset
    TrainingDataOrigin <|-- InternalDataset
    TrainingDataOrigin <|-- SyntheticDataset
```

</details>

<details>
<summary><strong>⚠️ Diagrama 2: Evaluación de Riesgo y Criterios</strong></summary>

```mermaid
classDiagram
    %% Clase unión para AIRO
    class ContextOrPurpose {
        <<union class>>
        +triggersCriterion: Criterion
        📎 airo:Context
    }
    
    %% Criterios de evaluación
    class Criterion {
        +assignsRiskLevel: RiskLevel
        +isTriggeredBy: ContextOrPurpose
    }
    class ContextualCriterion {
        +contextSpecific: boolean
    }
    class NormativeCriterion {
        +legalBasis: string
    }
    class TechnicalCriterion {
        +technicalStandard: string
    }
    
    %% Criterios contextuales específicos
    class VulnerablePopulationContext {
        +populationType: string
    }
    class HighStakesDecisionContext {
        +decisionImpact: string
    }
    class SafetyCriticalContext {
        +safetyLevel: string
    }
    class DataGovernanceContext {
        +governanceRequirements: string
    }
    
    %% Niveles de riesgo con mapeo AIRO
    class RiskLevel {
        📎 airo:RiskLevel
    }
    class HighRisk {
        +strictRequirements: boolean
        📎 airo:HighRiskLevel
    }
    class UnacceptableRisk {
        +prohibited: boolean
        📎 airo:CriticalRiskLevel
    }
    class LimitedRisk {
        +transparencyRequired: boolean
    }
    class MinimalRisk {
        +basicCompliance: boolean
    }
    
    %% Evaluación de riesgo
    class RiskAssessment {
        +assignedRiskLevel: RiskLevel
        +assessmentDate: date
        +justificationNote: string
        📎 airo:RiskAssessment
    }
    
    %% Union class para AIRO
    ContextOrPurpose --> DeploymentContext : unionOf
    ContextOrPurpose --> Purpose : unionOf
    
    %% Flujo de evaluación
    ContextOrPurpose --> Criterion : triggersCriterion
    Criterion --> RiskLevel : assignsRiskLevel
    RiskAssessment --> RiskLevel : assignedRiskLevel
    
    %% Jerarquías de criterios
    Criterion <|-- ContextualCriterion
    Criterion <|-- NormativeCriterion
    Criterion <|-- TechnicalCriterion
    
    ContextualCriterion <|-- VulnerablePopulationContext
    ContextualCriterion <|-- HighStakesDecisionContext
    ContextualCriterion <|-- SafetyCriticalContext
    ContextualCriterion <|-- DataGovernanceContext
    
    %% Jerarquía de riesgo
    RiskLevel <|-- HighRisk
    RiskLevel <|-- UnacceptableRisk
    RiskLevel <|-- LimitedRisk
    RiskLevel <|-- MinimalRisk
```

</details>

<details>
<summary><strong>📋 Diagrama 3: Cumplimiento y Requisitos</strong></summary>

```mermaid
classDiagram
    %% Criterios (entrada del proceso)
    class Criterion {
        +assignsRiskLevel: RiskLevel
        +triggersCompliance: ComplianceRequirement
    }
    
    %% Requisitos de cumplimiento
    class ComplianceRequirement {
        +justifiedByCriterion: Criterion
        +mandatoryCompliance: boolean
        +deadlineDate: date
    }
    
    class TechnicalRequirement {
        +technicalStandard: string
        +validationMethod: string
    }
    
    class TransparencyRequirement {
        +disclosureLevel: string
        +userInformation: string
    }
    
    class RobustnessRequirement {
        +testingProtocol: string
        +performanceMetrics: string
    }
    
    class DataGovernanceRequirement {
        +dataProtection: string
        +auditTrail: boolean
    }
    
    class TraceabilityRequirement {
        +documentationLevel: string
        +changeManagement: boolean
    }
    
    class DocumentationRequirement {
        +documentationType: string
        +updateFrequency: string
    }
    
    %% Evaluación de riesgo (conexión con diagrama anterior)
    class RiskAssessment {
        +requiresCompliance: ComplianceRequirement
        +complianceDeadline: date
    }
    
    %% Flujo de cumplimiento
    Criterion --> ComplianceRequirement : triggersComplianceRequirement
    RiskAssessment --> ComplianceRequirement : requiresCompliance
    
    %% Jerarquía de requisitos
    ComplianceRequirement <|-- TechnicalRequirement
    ComplianceRequirement <|-- TransparencyRequirement
    ComplianceRequirement <|-- RobustnessRequirement
    ComplianceRequirement <|-- DataGovernanceRequirement
    ComplianceRequirement <|-- TraceabilityRequirement
    ComplianceRequirement <|-- DocumentationRequirement
```

</details>

<details>
<summary><strong>🔗 Diagrama 4: Flujo de Proceso Completo</strong></summary>

```mermaid
flowchart TD
    %% Sistema central
    A[🏗️ IntelligentSystem] --> B[🎯 Purpose]
    A --> C[📍 DeploymentContext]
    A --> D[📊 TrainingDataOrigin]
    
    %% Unión AIRO
    B --> E{🔗 ContextOrPurpose}
    C --> E
    
    %% Evaluación de criterios
    E --> F[⚖️ Criterion]
    F --> G[⚠️ RiskLevel]
    
    %% Evaluación formal
    G --> H[📋 RiskAssessment]
    
    %% Requisitos de cumplimiento
    F --> I[📝 ComplianceRequirement]
    H --> I
    
    %% Tipos de requisitos
    I --> J[🔧 Technical]
    I --> K[👁️ Transparency] 
    I --> L[🛡️ Robustness]
    I --> M[📊 DataGovernance]
    
    %% Niveles de riesgo específicos
    G --> N[🔴 HighRisk]
    G --> O[⛔ UnacceptableRisk]
    G --> P[🟡 LimitedRisk]
    G --> Q[🟢 MinimalRisk]
    
    %% Mapeo AIRO
    E -.->|📎| R[airo:Context]
    G -.->|📎| S[airo:RiskLevel]
    H -.->|📎| T[airo:RiskAssessment]
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style F fill:#fff3e0
    style G fill:#ffebee
    style I fill:#e8f5e8
    style R fill:#f0f0f0
    style S fill:#f0f0f0
    style T fill:#f0f0f0
```

</details>

<details>
<summary><strong>👥 Diagrama de Clases - Actores del Ecosistema</strong></summary>

```mermaid
classDiagram
    %% Actores del ecosistema AI Act
    class Actor {
        +hasUrn: string
        +hasHttpIri: string
        +providesSystem: IntelligentSystem
        +deploysSystem: IntelligentSystem
        +usesSystem: IntelligentSystem
        +monitorsSystem: IntelligentSystem
    }
    
    class Provider {
        +developmentResponsibilities: string
        +marketingObligations: string
        +conformityAssessment: boolean
    }
    
    class Deployer {
        +deploymentContext: DeploymentContext
        +operationalResponsibilities: string
        +humanOversight: boolean
    }
    
    class User {
        +userType: string
        +accessLevel: string
    }
    
    class EndUser {
        +informationRights: boolean
        +transparencyRequirements: boolean
    }
    
    class ProfessionalUser {
        +professionalCompetence: string
        +trainingRequirements: string
    }
    
    class OversightBody {
        +supervisionScope: string
        +enforcementPowers: string
        +complianceMonitoring: boolean
    }
    
    class Distributor {
        +distributionChannel: string
        +marketingSuppport: string
    }
    
    class Importer {
        +importRegion: string
        +complianceVerification: boolean
    }
    
    %% Jerarquía de actores
    Actor <|-- Provider
    Actor <|-- Deployer
    Actor <|-- User
    Actor <|-- OversightBody
    Actor <|-- Distributor
    Actor <|-- Importer
    
    %% Especialización de usuarios
    User <|-- EndUser
    User <|-- ProfessionalUser
    
    %% Relaciones con sistemas (representativas)
    Provider --> IntelligentSystem : providesSystem
    Deployer --> IntelligentSystem : deploysSystem
    User --> IntelligentSystem : usesSystem
    OversightBody --> IntelligentSystem : monitorsSystem
```
</details>




<details>
<summary><strong>🔗 Integración AIRO (AI Risk Ontology)</strong></summary>

```mermaid
graph TB
    subgraph "AI Act Ontology"
        AI_CTX[ai:ContextOrPurpose]
        AI_RISK[ai:RiskLevel]
        AI_ASSESS[ai:RiskAssessment]
        AI_HIGH[ai:HighRisk]
        AI_UNAC[ai:UnacceptableRisk]
        AI_ASSIGN[ai:assignsRiskLevel]
    end
    
    subgraph "AIRO Ontology"
        AIRO_CTX[airo:Context]
        AIRO_RISK[airo:RiskLevel]
        AIRO_ASSESS[airo:RiskAssessment]
        AIRO_HIGH[airo:HighRiskLevel]
        AIRO_CRIT[airo:CriticalRiskLevel]
        AIRO_HAS[airo:hasRiskLevel]
    end
    
    %% Mapeos AIRO
    AI_CTX -.->|rdfs:seeAlso| AIRO_CTX
    AI_RISK -.->|rdfs:seeAlso| AIRO_RISK
    AI_ASSESS -.->|rdfs:seeAlso| AIRO_ASSESS
    AI_HIGH -.->|rdfs:seeAlso| AIRO_HIGH
    AI_UNAC -.->|rdfs:seeAlso| AIRO_CRIT
    AI_ASSIGN -.->|rdfs:seeAlso| AIRO_HAS
    
    %% Importación
    AI_ONT[AI Act Ontology] -->|owl:imports| AIRO_ONT[AIRO Ontology]
    
    style AI_CTX fill:#e1f5fe
    style AI_RISK fill:#e8f5e8
    style AI_ASSESS fill:#fff3e0
    style AIRO_CTX fill:#f3e5f5
    style AIRO_RISK fill:#f3e5f5
    style AIRO_ASSESS fill:#f3e5f5
```
</details>

<details>
<summary><strong>📊 Estadísticas de la Ontología</strong></summary>

| Elemento | Cantidad | Descripción |
|----------|----------|-------------|
| **Triples totales** | 991 | Incluyendo integración AIRO |
| **Clases OWL** | 31 | Jerarquía completa de conceptos |
| **Propiedades de objeto** | 28 | Relaciones entre entidades |
| **Propiedades de datos** | 8 | Atributos de las entidades |
| **Individuos nombrados** | 45+ | Instancias específicas (criterios, niveles de riesgo) |
| **Criterios contextuales** | 11 | Con asignaciones directas de riesgo |
| **Niveles de riesgo** | 4 | HighRisk, UnacceptableRisk, LimitedRisk, MinimalRisk |
| **Referencias AIRO** | 6 | Mapeos de interoperabilidad |
| **Namespaces importados** | 1 | AIRO (https://w3id.org/airo) |

**Cobertura AI Act**: ✅ Completa (Anexos I-IV)  
**Compatibilidad AIRO**: ✅ 85% implementada  
**Validación sintáctica**: ✅ Aprobada (rapper)  
**Estado**: ✅ Listo para producción  

</details>

## 🏷️ Instancias de la Ontología

### Contextos de Despliegue y Propósitos

<details>
<summary><strong>📍 Instancias: Contextos de Despliegue</strong></summary>

```mermaid
graph TD
    subgraph "DeploymentContext Instances"
        DC[DeploymentContext]
        
        %% Instancias específicas
        EDU[Education<br/>🎓 Educación]
        HEALTH[Healthcare<br/>🏥 Salud]
        PUBLIC[PublicServices<br/>🏛️ Servicios Públicos]
        LAW[LawEnforcement<br/>👮 Aplicación de la Ley]
        FINANCE[Financial<br/>💰 Financiero]
        BORDER[Border<br/>🛂 Control Fronterizo]
        
        %% Relaciones
        DC --> EDU
        DC --> HEALTH
        DC --> PUBLIC
        DC --> LAW
        DC --> FINANCE
        DC --> BORDER
        
        %% Criterios activados
        EDU --> EDUC_CRIT[EducationEvaluationCriterion]
        HEALTH --> ESS_CRIT[EssentialServicesAccessCriterion]
        PUBLIC --> ESS_CRIT
        LAW --> LAW_CRIT[LawEnforcementCriterion]
        BORDER --> MIG_CRIT[MigrationBorderCriterion]
        
        style EDU fill:#e8f5e8
        style HEALTH fill:#e1f5fe
        style PUBLIC fill:#fff3e0
        style LAW fill:#ffebee
        style FINANCE fill:#f3e5f5
        style BORDER fill:#e0f2f1
    end
```

</details>

<details>
<summary><strong>🎯 Instancias: Propósitos de Sistemas</strong></summary>

```mermaid
graph TD
    subgraph "Purpose Instances"
        PURP[Purpose]
        
        %% Instancias reales de la ontología
        BIO_ID[BiometricIdentification<br/>🔍 Identificación Biométrica]
        EDUC_ACC[EducationAccess<br/>📚 Acceso Educativo]
        MIG_CTRL[MigrationControl<br/>🗺️ Control Migratorio]
        PUB_ALLOC[PublicServiceAllocation<br/>📋 Asignación Servicios]
        CRIT_INFRA[CriticalInfrastructureOperation<br/>🏗️ Infraestructura Crítica]
        JUDICIAL[JudicialDecisionSupport<br/>⚖️ Apoyo Judicial]
        LAW_ENF[LawEnforcementSupport<br/>👮 Aplicación de la Ley]
        RECRUIT[RecruitmentOrEmployment<br/>💼 Reclutamiento]
        
        %% Relaciones
        PURP --> BIO_ID
        PURP --> EDUC_ACC
        PURP --> MIG_CTRL
        PURP --> PUB_ALLOC
        PURP --> CRIT_INFRA
        PURP --> JUDICIAL
        PURP --> LAW_ENF
        PURP --> RECRUIT
        
        %% Criterios activados (flujo correcto - solo los que existen)
        BIO_ID --> BIO_CRIT[BiometricIdentificationCriterion]
        EDUC_ACC --> EDUC_CRIT[EducationEvaluationCriterion]
        MIG_CTRL --> MIG_CRIT[MigrationBorderCriterion]
        
        %% Criterios asignan niveles de riesgo (solo los definidos)
        BIO_CRIT --> HIGH_R[HighRisk]
        EDUC_CRIT --> HIGH_R
        MIG_CRIT --> HIGH_R
        
        style BIO_ID fill:#ffebee
        style EDUC_ACC fill:#e8f5e8
        style MIG_CTRL fill:#fff3e0
        style PUB_ALLOC fill:#e1f5fe
        style CRIT_INFRA fill:#f3e5f5
        style JUDICIAL fill:#fce4ec
        style LAW_ENF fill:#e0f2f1
        style RECRUIT fill:#f1f8e9
        style BIO_CRIT fill:#ff9800,color:#ffffff
        style HIGH_R fill:#ff5722,color:#ffffff
    end
```

</details>

### Niveles de Riesgo y Criterios

<details>
<summary><strong>⚠️ Instancias: Niveles de Riesgo</strong></summary>

```mermaid
graph LR
    subgraph "RiskLevel Instances"
        RL[RiskLevel]
        
        %% Instancias con mapeo AIRO
        UNAC[UnacceptableRisk<br/>⛔ Riesgo Inaceptable<br/>📎 airo:CriticalRiskLevel]
        HIGH[HighRisk<br/>🔴 Riesgo Alto<br/>📎 airo:HighRiskLevel]
        LIM[LimitedRisk<br/>🟡 Riesgo Limitado]
        MIN[MinimalRisk<br/>🟢 Riesgo Mínimo]
        
        %% Jerarquía
        RL --> UNAC
        RL --> HIGH
        RL --> LIM
        RL --> MIN
        
        %% Requisitos asociados
        UNAC --> PROHIB[Sistema Prohibido]
        HIGH --> STRICT[Requisitos Estrictos]
        LIM --> TRANSP[Transparencia Requerida]
        MIN --> BASIC[Cumplimiento Básico]
        
        style UNAC fill:#f44336,color:#ffffff
        style HIGH fill:#ff5722,color:#ffffff
        style LIM fill:#ff9800,color:#ffffff
        style MIN fill:#4caf50,color:#ffffff
        style PROHIB fill:#000000,color:#ffffff
        style STRICT fill:#d32f2f,color:#ffffff
        style TRANSP fill:#f57c00,color:#ffffff
        style BASIC fill:#388e3c,color:#ffffff
    end
```

</details>

<details>
<summary><strong>⚖️ Instancias: Criterios Específicos</strong></summary>

```mermaid
graph TD
    subgraph "Criterion Instances"
        CRIT[Criterion]
        
        %% Criterios normativos
        subgraph "NormativeCriterion"
            BIO_CRIT[BiometricIdentificationCriterion<br/>🔍 Identificación Biométrica]
            CRIT_INFRA[CriticalInfrastructureCriterion<br/>🏗️ Infraestructura Crítica]
            LAW_CRIT[LawEnforcementCriterion<br/>👮 Aplicación de la Ley]
            MIG_CRIT[MigrationBorderCriterion<br/>🛂 Control Fronterizo]
            RECRUIT[RecruitmentEmploymentCriterion<br/>💼 Empleo]
        end
        
        %% Criterios contextuales
        subgraph "ContextualCriterion"
            DATA_GOV[DataGovernanceContext<br/>📊 Gobernanza de Datos]
            TRAINING_Q[TrainingDataQualityContext<br/>📈 Calidad de Datos]
            ESSENTIAL[EssentialServicesAccessCriterion<br/>🏥 Servicios Esenciales]
            EDUCATION[EducationEvaluationCriterion<br/>🎓 Evaluación Educativa]
        end
        
        %% Criterios técnicos
        subgraph "TechnicalCriterion"
            ACCURACY[AccuracyRequirement<br/>🎯 Precisión]
            ROBUSTNESS[RobustnessRequirement<br/>🛡️ Robustez]
            SECURITY[SecurityRequirement<br/>🔒 Seguridad]
        end
        
        %% Relaciones con niveles de riesgo
        BIO_CRIT --> HIGH_RISK[HighRisk]
        CRIT_INFRA --> HIGH_RISK
        LAW_CRIT --> HIGH_RISK
        DATA_GOV --> HIGH_RISK
        EDUCATION --> LIM_RISK[LimitedRisk]
        ACCURACY --> MIN_RISK[MinimalRisk]
        
        style BIO_CRIT fill:#ffebee
        style CRIT_INFRA fill:#e1f5fe
        style LAW_CRIT fill:#fff3e0
        style DATA_GOV fill:#f3e5f5
        style EDUCATION fill:#e8f5e8
        style ACCURACY fill:#e0f2f1
    end
```

</details>

### Requisitos de Cumplimiento

<details>
<summary><strong>📋 Instancias: Requisitos Específicos</strong></summary>

```mermaid
graph TD
    subgraph "ComplianceRequirement Instances"
        CR[ComplianceRequirement]
        
        %% Requisitos técnicos
        subgraph "Technical Requirements"
            ACC_EVAL[AccuracyEvaluationRequirement<br/>🎯 Evaluación de Precisión]
            ROBUST[RobustnessRequirement<br/>🛡️ Robustez]
            SECURITY[SecurityRequirement<br/>🔒 Seguridad]
            VALID[ValidationRequirement<br/>✅ Validación]
        end
        
        %% Requisitos de transparencia
        subgraph "Transparency Requirements"
            TRANSP[TransparencyRequirement<br/>👁️ Transparencia]
            DOC[DocumentationRequirement<br/>📝 Documentación]
            TRACE[TraceabilityRequirement<br/>🔍 Trazabilidad]
            DISCLOSURE[DisclosureRequirement<br/>📢 Divulgación]
        end
        
        %% Requisitos de gobernanza
        subgraph "Governance Requirements"
            DATA_GOV_REQ[DataGovernanceRequirement<br/>📊 Gobernanza de Datos]
            HUMAN_OV[HumanOversightRequirement<br/>👤 Supervisión Humana]
            FUND_RIGHTS[FundamentalRightsAssessmentRequirement<br/>⚖️ Derechos Fundamentales]
            QUALITY_MAN[QualityManagementRequirement<br/>📈 Gestión de Calidad]
        end
        
        %% Relaciones con criterios
        ACC_EVAL --> ACCURACY_CRIT[AccuracyCriterion]
        ROBUST --> SAFETY_CRIT[SafetyCriterion]
        TRANSP --> USER_INFO[UserInformationCriterion]
        DATA_GOV_REQ --> DATA_CRIT[DataGovernanceCriterion]
        HUMAN_OV --> HIGH_RISK_CRIT[HighRiskCriterion]
        
        style ACC_EVAL fill:#e8f5e8
        style ROBUST fill:#e1f5fe
        style TRANSP fill:#fff3e0
        style DATA_GOV_REQ fill:#f3e5f5
        style HUMAN_OV fill:#ffebee
        style DOC fill:#e0f2f1
    end
```

</details>



## 🔄 Flujos del Sistema

<details>
<summary><strong>📊 Arquitectura General</strong></summary>

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Frontend]
        UI --> |HTTP Requests| LB[Load Balancer]
    end
    
    subgraph "API Layer"
        LB --> API[FastAPI Backend]
        API --> |SPARQL Queries| FUSEKI[Apache Jena Fuseki]
        API --> |Document Storage| MONGO[MongoDB]
        API --> |Reasoning Requests| REASONER[OWL Reasoner Service]
    end
    
    subgraph "Data Layer"
        FUSEKI --> |RDF Triples| ONTOLOGY[(Ontología AI Act)]
        MONGO --> |JSON Documents| SYSTEMS[(Sistemas IA)]
    end
    
    subgraph "Documentation"
        ONTOLOGY --> |Widoco| DOCS[HTML Documentation]
        DOCS --> |Nginx| WEB[Web Server]
    end
```
</details>

<details>
<summary><strong>🔧 Gestión de Sistemas IA</strong></summary>

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant A as API Backend
    participant M as MongoDB
    participant R as Reasoner
    participant FS as Fuseki
    
    U->>F: Crear/Editar Sistema IA
    F->>A: POST /systems/
    A->>M: Almacenar documento
    A->>FS: Convertir a RDF y almacenar
    A->>R: Ejecutar inferencias SWRL
    R->>A: Retornar conocimiento inferido
    A->>FS: Almacenar inferencias
    A->>F: Confirmación
    F->>U: Sistema creado/actualizado
```
</details>

<details>
<summary><strong>🧠 Razonamiento Semántico</strong></summary>

```mermaid
graph LR
    subgraph "Input Data"
        DATA[Datos del Sistema]
        RULES[Reglas SWRL]
        ONT[Ontología Base]
    end
    
    subgraph "Reasoning Process"
        LOAD[Cargar en Reasoner]
        INFER[Ejecutar Inferencias]
        RESULT[Generar Conclusiones]
    end
    
    subgraph "Output"
        RDF[Grafo RDF Enriquecido]
        STORE[Almacenar en Fuseki]
    end
    
    DATA --> LOAD
    RULES --> LOAD
    ONT --> LOAD
    LOAD --> INFER
    INFER --> RESULT
    RESULT --> RDF
    RDF --> STORE
```
</details>

---

## 🚀 Guías de Uso

### 📖 1. Generar Documentación de la Ontología

```bash
cd tools
./generate_ontology_docs.sh
```

**¿Qué hace este script?**
1. ✅ Lee la versión actual desde `ontologias.env`
2. 🌐 Levanta servidor HTTP local temporal (puerto 8080)
3. 📚 Ejecuta Widoco para generar documentación bilingüe (ES-EN)
4. 🔍 Ejecuta validación automática con OOPS!
5. 🧹 Limpia recursos temporales

**📁 Archivos generados:**
- `index-es.html` / `index-en.html` - Documentación principal
- `ontology.ttl` / `ontology.owl` - Ontología procesada
- `OOPSevaluation/oopsEval.html` - Reporte de validación

### ✅ 2. Validación de la Ontología

La validación se ejecuta **automáticamente** durante la generación de documentación usando **OOPS!** (OntOlogy Pitfall Scanner).

**🔍 Validaciones incluidas:**
- ✅ Consistencia lógica OWL
- ✅ Sintaxis RDF/TTL correcta  
- ✅ Detección de clases desconectadas
- ✅ Propiedades sin uso
- ✅ Circularidad en jerarquías
- ✅ Etiquetas y comentarios faltantes

**📊 Ver resultados:**
- **Reporte completo**: `/ontologias/docs/OOPSevaluation/oopsEval.html`
- **Documentación**: Incluye métricas automáticas de calidad

### 🐳 3. Despliegue con Docker

#### Opción A: Producción (Recomendada)

```bash
# Levantar todos los servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs si hay problemas
docker-compose logs [servicio]
```

#### Opción B: Desarrollo Local

<details>
<summary><strong>Instrucciones detalladas</strong></summary>

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend  
cd frontend
npm install
npm run dev

# Terminal 3: Reasoner Service
cd reasoner_service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Terminal 4: MongoDB (si no tienes Docker)
mongod --port 27017

# Terminal 5: Fuseki (si no tienes Docker)
# Descargar Apache Jena Fuseki y ejecutar
```
</details>

---

## 🔌 API Reference

### 🎯 Endpoints Principales

<details>
<summary><strong>📊 Backend API (Puerto 8000)</strong></summary>

#### Gestión de Sistemas IA
```http
GET    /systems/                    # 📋 Listar sistemas con filtros
POST   /systems/                    # ➕ Crear nuevo sistema
GET    /systems/{system_id}         # 👀 Obtener sistema específico
PUT    /systems/{system_id}         # ✏️ Actualizar sistema
DELETE /systems/{system_id}         # 🗑️ Eliminar sistema
```

#### Consultas SPARQL
```http
POST   /fuseki/sparql/             # 🔍 Ejecutar consulta SPARQL personalizada
GET    /fuseki/vocabulary/         # 📚 Obtener vocabulario de la ontología
GET    /fuseki/classes/            # 🏷️ Listar clases OWL
GET    /fuseki/properties/         # 🔗 Listar propiedades OWL
```

#### Análisis y Estadísticas
```http
GET    /systems/stats/             # 📈 Estadísticas de sistemas
GET    /systems/risks/             # ⚠️ Análisis de riesgos
GET    /ontology/classes/          # 🌳 Explorar jerarquía de clases
```

**📖 Documentación completa**: http://localhost:8000/docs
</details>

<details>
<summary><strong>🧠 Reasoner Service (Puerto 8001)</strong></summary>

#### Razonamiento Semántico
```http
POST   /reason                     # 🔬 Ejecutar inferencias SWRL
```

**Parámetros:**
- `data`: archivo TTL con datos de entrada
- `swrl_rules`: archivo TTL con reglas SWRL
- **Retorna**: grafo RDF enriquecido con inferencias
</details>

<details>
<summary><strong>🔍 Fuseki SPARQL (Puerto 3030)</strong></summary>

```http
GET    /ds/sparql                  # 📖 Consultas SPARQL de lectura
POST   /ds/sparql                  # ✏️ Consultas SPARQL de escritura  
GET    /ds/data                    # 📊 Acceso directo a datos RDF
```

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin`
</details>

### �️ Rutas del Frontend (Puerto 5173)

| Ruta | Descripción |
|------|-------------|
| `/` | 🏠 Dashboard principal |
| `/systems` | 🤖 Gestión de sistemas IA |
| `/graph` | 🕸️ Visualización interactiva RDF |
| `/docs` | 📚 Documentación de ontología |
| `/reasoning` | 🧠 Interfaz de inferencias |

---

## ⚙️ Configuración Avanzada

<details>
<summary><strong>🔧 Variables de Entorno</strong></summary>

```bash
# Versión de ontología
CURRENT_RELEASE=0.36.0

# Conexiones de base de datos
MONGO_URL=mongodb://mongo:27017
FUSEKI_ENDPOINT=http://fuseki:3030
FUSEKI_USER=admin
FUSEKI_PASSWORD=admin
FUSEKI_DATASET=ds
FUSEKI_GRAPH=http://ai-act.eu/ontology

# Rutas de ontología
ONTOLOGY_PATH=/ontologias/ontologia-v0.36.0.ttl
```
</details>

<details>
<summary><strong>📚 Recursos y Enlaces Útiles</strong></summary>

- **📖 Consultas SPARQL**: Ejemplos en `/sparql_queries/consultas.sparqlbook`
- **🔗 Esquemas JSON-LD**: Contexto en `/ontologias/json-ld-context.json`
- **📚 Documentación Ontología**: http://localhost/docs/
- **📋 API Documentation**: http://localhost:8000/docs
- **🔍 SPARQL Interface**: http://localhost:3030/dataset.html
</details>

---

## 🛠 Tecnologías Empleadas

<details>
<summary><strong>🖥️ Stack Tecnológico Completo</strong></summary>

### Backend
- **FastAPI** - Framework web moderno para Python
- **MongoDB** - Base de datos NoSQL para almacenamiento de documentos
- **Apache Jena Fuseki** - Servidor SPARQL y almacén de triples RDF
- **RDFLib** - Biblioteca Python para manejo de datos RDF
- **OwlReady2** - Razonador OWL/SWRL para inferencia semántica
- **Motor** - Driver asíncrono de MongoDB para Python

### Frontend
- **React 19** - Biblioteca de interfaz de usuario
- **TypeScript** - Superset tipado de JavaScript
- **Vite** - Herramienta de build rápida
- **TailwindCSS** - Framework de CSS utilitario
- **D3.js** - Visualización de datos y grafos
- **Vis-network** - Biblioteca para visualización de redes
- **React Router Dom** - Enrutamiento del lado cliente

### Infraestructura
- **Docker & Docker Compose** - Contenerización y orquestación
- **Nginx** - Servidor web para servir documentación
- **Widoco** - Generación automática de documentación de ontologías

### Semántica y Ontologías
- **OWL (Web Ontology Language)** - Lenguaje de ontologías web
- **SWRL (Semantic Web Rule Language)** - Reglas semánticas
- **RDF/Turtle** - Formato de datos semánticos
- **JSON-LD** - Formato JSON para datos enlazados
</details>

---

## 🔧 Troubleshooting

<details>
<summary><strong>❌ Problemas Comunes</strong></summary>

### 🐳 Docker Issues

**Problema**: Error de permisos al generar documentación
```bash
# Solución: El script ya usa puerto 8080 (no requiere root)
cd tools
./generate_ontology_docs.sh
```

**Problema**: Puertos ocupados
```bash
# Verificar puertos en uso
docker-compose ps
netstat -tulpn | grep :5173

# Cambiar puertos en docker-compose.yml si es necesario
```

**Problema**: Servicios no se levantan
```bash
# Ver logs detallados
docker-compose logs [servicio]

# Reconstruir imágenes
docker-compose build --no-cache [servicio]
```

### 🌐 Frontend Issues

**Problema**: Frontend no carga o errores en consola
```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/docs

# Revisar logs del frontend
docker-compose logs frontend
```

### 🔍 SPARQL/Ontología Issues

**Problema**: Error en validación de ontología
```bash
# Validar sintaxis TTL manualmente
rapper -i turtle -c ontologias/ontologia-v0.36.0.ttl
```

**Problema**: Fuseki no responde
```bash
# Reiniciar solo Fuseki
docker-compose restart fuseki

# Verificar endpoint
curl http://localhost:3030/$/ping
```
</details>

---

## 🤝 Contribuir

1. **Fork del repositorio**
2. **Crear rama feature** (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit cambios** (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push a la rama** (`git push origin feature/nueva-funcionalidad`)
5. **Crear Pull Request**

### 📋 Guidelines

- ✅ Seguir convenciones de código existentes
- ✅ Documentar cambios en la ontología
- ✅ Agregar tests para nuevas funcionalidades
- ✅ Actualizar documentación si es necesario

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia Apache 2.0. Ver el archivo [LICENSE](LICENSE) para más detalles.

```
Copyright 2025 AI Act Project Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```