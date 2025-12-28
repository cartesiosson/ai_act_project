# Diagramas de la Ontología AI Act

Este documento contiene los diagramas Mermaid de los cinco módulos principales de la ontología.

---

## 1. Módulo Legal

Representa artículos, anexos, obligaciones y definiciones del AI Act.

```mermaid
classDiagram
    class Criterion {
        <<owl:Class>>
    }
    class ProhibitedPracticeCriterion {
        <<owl:Class>>
        +articleReference: string
        +eli:cites: URI
        +prohibitionScope: string
    }
    class LegalException {
        <<owl:Class>>
        +articleReference: string
        +eli:cites: URI
    }
    class ComplianceRequirement {
        <<owl:Class>>
        +articleReference: string
        +eli:cites: URI
    }

    Criterion <|-- ProhibitedPracticeCriterion
    Criterion <|-- ComplianceRequirement

    ProhibitedPracticeCriterion <|-- SubliminalManipulationCriterion
    ProhibitedPracticeCriterion <|-- VulnerabilityExploitationCriterion
    ProhibitedPracticeCriterion <|-- SocialScoringCriterion
    ProhibitedPracticeCriterion <|-- PredictivePolicingCriterion
    ProhibitedPracticeCriterion <|-- BiometricIdentificationCriterion

    LegalException <|-- VictimSearchException
    LegalException <|-- TerroristThreatException
    LegalException <|-- SeriousCrimeException

    ProhibitedPracticeCriterion "1" --> "*" LegalException : hasException
    ProhibitedPracticeCriterion "1" --> "*" ComplianceRequirement : activatesRequirement
```

---

## 2. Módulo de Nivel de Riesgo

Describe nivel de riesgo, impacto en poblaciones, medidas obligatorias y planes de mitigación.

```mermaid
classDiagram
    class Identifiable {
        <<owl:Class>>
        +hasUrn: string
    }
    class RiskLevel {
        <<owl:Class>>
    }
    class Criterion {
        <<owl:Class>>
    }
    class ComplianceRequirement {
        <<owl:Class>>
    }

    Identifiable <|-- RiskLevel

    RiskLevel <|-- UnacceptableRisk
    RiskLevel <|-- HighRisk
    RiskLevel <|-- LimitedRisk
    RiskLevel <|-- MinimalRisk

    note for UnacceptableRisk "Art. 5 - Prohibido"
    note for HighRisk "Anexo III - Requisitos Arts. 9-15"
    note for LimitedRisk "Art. 50 - Transparencia"
    note for MinimalRisk "Sin requisitos obligatorios"

    Criterion "1" --> "1" RiskLevel : assignsRiskLevel
    Criterion "1" --> "*" ComplianceRequirement : activatesRequirement

    class NormativeCriterion {
        <<owl:Class>>
    }
    class TechnicalCriterion {
        <<owl:Class>>
    }
    class ContextualCriterion {
        <<owl:Class>>
    }

    Criterion <|-- NormativeCriterion
    Criterion <|-- TechnicalCriterion
    Criterion <|-- ContextualCriterion
```

---

## 3. Módulo Técnico

Modela documentación técnica, procedimientos de conformidad y características de sistemas.

```mermaid
classDiagram
    class IntelligentSystem {
        <<owl:Class>>
        +hasUrn: string
        +hasName: string
        +hasVersion: string
    }
    class GeneralPurposeAIModel {
        <<owl:Class>>
        +hasModelScale: ModelScale
    }
    class HighCapabilityGPAIModel {
        <<owl:Class>>
        +hasCapabilityMetric: float
    }

    IntelligentSystem <|-- GeneralPurposeAIModel
    GeneralPurposeAIModel <|-- HighCapabilityGPAIModel

    class AlgorithmType {
        <<owl:Class>>
    }
    AlgorithmType <|-- MachineLearningAlgorithm
    AlgorithmType <|-- KnowledgeBasedAlgorithm
    AlgorithmType <|-- StatisticalAlgorithm
    AlgorithmType <|-- HybridAlgorithm

    class TechnicalRequirement {
        <<owl:Class>>
    }
    class RobustnessRequirement {
        <<owl:Class>>
    }
    class SecurityRequirement {
        <<owl:Class>>
    }
    class LoggingRequirement {
        <<owl:Class>>
    }
    class AccuracyRequirement {
        <<owl:Class>>
    }

    TechnicalRequirement <|-- RobustnessRequirement
    TechnicalRequirement <|-- SecurityRequirement
    TechnicalRequirement <|-- LoggingRequirement
    TechnicalRequirement <|-- AccuracyRequirement

    IntelligentSystem "1" --> "1" AlgorithmType : hasAlgorithmType
    IntelligentSystem "1" --> "*" TechnicalRequirement : mustComplyWith
```

---

## 4. Módulo Organizativo

Representa roles, responsables, registros y procesos de supervisión.

```mermaid
classDiagram
    class Actor {
        <<owl:Class>>
        owl:equivalentClass airo:Stakeholder
    }

    class AIProvider {
        <<airo:AIProvider>>
        Art. 3.3 EU AI Act
    }
    class AIDeployer {
        <<airo:AIDeployer>>
        Art. 3.4 EU AI Act
    }
    class AIUser {
        <<airo:AIUser>>
    }
    class AISubject {
        <<airo:AISubject>>
    }
    class Regulator {
        <<airo:Regulator>>
    }

    Actor <|-- AIProvider
    Actor <|-- AIDeployer
    Actor <|-- AIUser
    Actor <|-- AISubject
    Actor <|-- Regulator

    class IntelligentSystem {
        <<owl:Class>>
    }

    IntelligentSystem "1" --> "1" AIProvider : hasProvider
    IntelligentSystem "1" --> "*" AIDeployer : hasDeployer
    IntelligentSystem "1" --> "*" AIUser : hasUser
    IntelligentSystem "1" --> "*" AISubject : hasSubject
    IntelligentSystem "1" --> "*" Regulator : hasOversightBody

    class VulnerableGroupCategory {
        <<owl:Class>>
    }
    VulnerableGroupCategory <|-- Minor
    VulnerableGroupCategory <|-- Elderly
    VulnerableGroupCategory <|-- Disabled
    VulnerableGroupCategory <|-- Migrant

    AISubject "1" --> "*" VulnerableGroupCategory : belongsTo
```

---

## 5. Módulo de Evidencias

Permite vincular documentos, certificados, informes y artefactos de verificación.

```mermaid
classDiagram
    class Evidence {
        <<owl:Class>>
        +evidenceDescription: string
        +evidencePriority: string
        +evidenceFrequency: string
    }

    Evidence <|-- PolicyEvidence
    Evidence <|-- TechnicalEvidence
    Evidence <|-- AuditEvidence
    Evidence <|-- TrainingEvidence
    Evidence <|-- AssessmentEvidence
    Evidence <|-- ContractualEvidence

    class PolicyEvidence {
        Políticas documentadas
    }
    class TechnicalEvidence {
        Documentación técnica
    }
    class AuditEvidence {
        Logs y auditorías
    }
    class TrainingEvidence {
        Registros formación
    }
    class AssessmentEvidence {
        Evaluaciones impacto
    }
    class ContractualEvidence {
        Contratos y acuerdos
    }

    PolicyEvidence <|-- HumanOversightPolicyEvidence
    PolicyEvidence <|-- SecurityPolicyEvidence
    PolicyEvidence <|-- DataQualityPolicyEvidence

    TechnicalEvidence <|-- TechnicalDocumentationEvidence
    TechnicalEvidence <|-- ModelCardEvidence
    TechnicalEvidence <|-- SystemDescriptionEvidence

    AuditEvidence <|-- BiasAuditReportEvidence
    AuditEvidence <|-- SecurityAuditReportEvidence
    AuditEvidence <|-- AuditLogEvidence

    AssessmentEvidence <|-- FRIAReportEvidence
    AssessmentEvidence <|-- RiskRegisterEvidence

    class ComplianceRequirement {
        <<owl:Class>>
    }

    ComplianceRequirement "1" --> "*" Evidence : requiresEvidence
    Evidence "*" --> "1" DPVMeasure : mapsToDPVMeasure

    class DPVMeasure {
        <<dpv:TechnicalOrganisationalMeasure>>
        W3C DPV 2.2
    }
```

---

## Diagrama General de Integración

Muestra cómo los cinco módulos se relacionan entre sí.

```mermaid
flowchart TB
    subgraph Legal["1. Módulo Legal"]
        Art5[Artículo 5<br/>Prohibiciones]
        Art9_15[Artículos 9-15<br/>Alto Riesgo]
        AnexoIII[Anexo III<br/>Criterios]
        ELI[eli:cites<br/>EUR-Lex]
    end

    subgraph Riesgo["2. Módulo Nivel de Riesgo"]
        Unacceptable[UnacceptableRisk]
        High[HighRisk]
        Limited[LimitedRisk]
        Minimal[MinimalRisk]
    end

    subgraph Tecnico["3. Módulo Técnico"]
        System[IntelligentSystem]
        GPAI[GeneralPurposeAIModel]
        Algorithm[AlgorithmType]
        TechReq[TechnicalRequirement]
    end

    subgraph Organizativo["4. Módulo Organizativo"]
        Provider[AIProvider]
        Deployer[AIDeployer]
        Subject[AISubject]
        Regulator[Regulator]
    end

    subgraph Evidencias["5. Módulo de Evidencias"]
        Policy[PolicyEvidence]
        Technical[TechnicalEvidence]
        Audit[AuditEvidence]
        Assessment[AssessmentEvidence]
    end

    Art5 -->|assignsRiskLevel| Unacceptable
    AnexoIII -->|assignsRiskLevel| High

    High -->|activatesRequirement| Art9_15
    Art9_15 -->|requiresEvidence| Evidencias

    System -->|hasProvider| Provider
    System -->|hasDeployer| Deployer
    System -->|hasSubject| Subject

    Provider -->|mustProvide| Evidencias
    Deployer -->|mustProvide| Evidencias

    Regulator -->|verifies| Evidencias

    ELI -.->|links| Art5
    ELI -.->|links| Art9_15
```

---

## Leyenda

| Símbolo | Significado |
|---------|-------------|
| `<<owl:Class>>` | Clase OWL definida en nuestra ontología |
| `<<airo:*>>` | Clase reutilizada de AIRO (AI Risk Ontology) |
| `<<dpv:*>>` | Clase referenciada de W3C DPV 2.2 |
| `-->` | Propiedad de objeto (ObjectProperty) |
| `--|>` | Herencia (rdfs:subClassOf) |
| `-.->` | Referencia externa (rdfs:seeAlso, eli:cites) |

---

**Versión:** 0.37.5
**Fecha:** 2025-12-23
**Namespace:** `http://ai-act.eu/ai#`
