## About SERAMIS

**SERAMIS** (**Semantic Regulation Intelligence System**) is a comprehensive platform designed to support organizations in achieving **compliance** with the **EU AI Act** ([Regulation (EU) 2024/1689](http://data.europa.eu/eli/reg/2024/1689)) through intelligent **semantic analysis**.

> **Current Version:** Ontology v0.41.0 (January 2026) - Full support for Article 3(49) Serious Incident Taxonomy and Article 73 Notification Obligations.

### Key Features

- **AI Systems Registry**: Catalog and manage your **AI systems** with detailed **metadata**, **deployment contexts**, and **purpose classifications** aligned with **EU AI Act** requirements.

- **Knowledge Graph**: Visualize and explore the **semantic relationships** between AI systems, regulations, **compliance requirements**, and **risk classifications** using our **ontology-powered** knowledge graph.

- **Ontology Documentation**: Access comprehensive documentation of the **AI Act ontology**, including **classes**, **properties**, and **individuals** that model regulatory concepts.

- **Symbolic Reasoning**: Apply **SWRL rules** and **SHACL validation** to automatically infer compliance requirements, **risk levels**, and **normative criteria** based on your AI system's characteristics.

- **Forensic AI Agent**: Analyze real-world **AI incidents** from the [AIAAIC repository](https://www.aiaaic.org/aiaaic-repository) using **LLM-powered extraction** to identify **compliance gaps** and map **violations** to **EU AI Act** requirements. The agent classifies incidents according to the **Article 3(49) Serious Incident Taxonomy**:
  - `DeathOrHealthHarm` - Art. 3(49)(a)
  - `CriticalInfrastructureDisruption` - Art. 3(49)(b)
  - `FundamentalRightsInfringement` - Art. 3(49)(c)
  - `PropertyOrEnvironmentHarm` - Art. 3(49)(d)

  Incidents are automatically evaluated for **Article 73 notification obligations** (15-day deadline to national authorities).

- **DPV Evidence Plans**: Generate **actionable compliance roadmaps** using the **[Data Privacy Vocabulary (DPV 2.2)](https://w3id.org/dpv)** standard. For each identified compliance gap, SERAMIS generates specific **evidence requirements**, **responsible roles** (Deployer, Provider, DPO, Legal), **collection frequencies**, and **document templates** to demonstrate compliance with **EU AI Act** obligations. The Evidence Planner covers **14 requirement types** with approximately **40 evidence items**.

- **MCP SPARQL Server**: A **[Model Context Protocol](https://modelcontextprotocol.io/)** server built with **FastMCP 2.0** that exposes SPARQL query capabilities and forensic analysis tools to LLM clients. Available tools include: `query_ontology`, `determine_risk_level`, `analyze_incident`, `query_iso_mappings`, `query_nist_mappings`, and more.

### Ontology Interoperability

SERAMIS ontology integrates with established **W3C**, **EU**, and research ontologies:

- **[AIRO (AI Risk Ontology)](https://w3id.org/airo)**: 30+ concept mappings including **risk levels** (`ai:HighRisk ↔ airo:HighRiskLevel`), **purposes** (`ai:Purpose ≡ airo:Purpose`), **evaluation criteria** (`ai:Criterion ≡ airo:EvaluationCriterion`), and **compliance requirements** (`ai:ComplianceRequirement ≡ airo:ComplianceRequirement`).

- **[DPV (Data Privacy Vocabulary)](https://w3id.org/dpv)**: Integration for **evidence plans**, **organizational roles**, and **data processing** concepts aligned with GDPR and AI Act requirements.

- **[ELI (European Legislation Identifier)](https://eur-lex.europa.eu/eli-register/about.html)**: Direct links to **EUR-Lex** official legislation using the EU standard for legislation identifiers. Each requirement and criterion references its **source article** via `eli:cites` (e.g., `art_14/oj` for Human Oversight). This enables **semantic traceability** to the official legal text and ensures **persistent, dereferenceable URIs** following Council Conclusions 2012/C 325/02.

- **[ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)**: 15 bidirectional mappings between **EU AI Act requirements** and **ISO 42001 controls** (Sections 5-10). Enables **multi-framework compliance analysis** and **forensic investigation** of certified systems. Properties: `ai:equivalentToISOControl`, `ai:isoSection`, `ai:mappingConfidence`.

- **[NIST AI RMF 1.0](https://www.nist.gov/itl/ai-risk-management-framework)**: 16 mappings covering all 4 NIST functions (**GOVERN**, **MAP**, **MEASURE**, **MANAGE**) for **global incident forensics** and **US-EU comparative analysis**. Properties: `ai:equivalentToNISTFunction`, `ai:nistCategory`, `ai:nistApplicabilityContext`.

#### Multi-Framework Mapping Statistics

| Framework | Mappings | Confidence | Status |
|-----------|----------|------------|--------|
| ISO 42001 | 15 | 87% HIGH | ✅ Active |
| NIST AI RMF | 16 | 100% HIGH | ✅ Active |
| DPV 2.2 | 14 | - | ✅ Active |
| **Total** | **45** | **94% HIGH** | **Operational** |

### Architecture

SERAMIS integrates multiple components:

- **Semantic Layer**: **Apache Jena Fuseki** for **RDF storage** and **SPARQL querying** with **15 forensic SPARQL queries** for compliance analysis
- **Reasoning Engine**: Custom **reasoner service** with **SWRL rules** for **automated inference**
- **Forensic Analysis**: **LLM-based** (Ollama/Llama) incident extraction with **MCP** (Model Context Protocol) integration via **FastMCP 2.0**
- **Persistence**: **MongoDB** for system data and analysis results
- **Frontend**: **React** application with **Knowledge Graph visualization**, **Evidence Planner**, and **Forensic Agent interface**

### Getting Started

1. Navigate to **AI Systems DB** to register your AI systems
2. Use **AI Knowledge Graph** to explore regulatory relationships
3. Run **AI Symbolic Reasoning** to infer compliance requirements
4. Analyze incidents with **Forensic AI Agent** for compliance insights
5. Generate **DPV Evidence Plans** to create actionable compliance roadmaps

---

### Regulatory Coverage

SERAMIS v0.41.0 ontology provides comprehensive coverage of key EU AI Act provisions:

| Provision | Coverage | Description |
|-----------|----------|-------------|
| **Annex III** | ✅ Complete | High-risk system classification criteria |
| **Article 2** | ✅ Complete | Scope determination with exclusions and overrides |
| **Article 3(49)** | ✅ Complete | Serious incident taxonomy (4 types) |
| **Article 6(3)** | ✅ Complete | Hidden requirements for residual risk |
| **Article 14** | ✅ Complete | Human oversight obligations |
| **Article 73** | ✅ Complete | Notification obligations (15-day deadline) |
| **Articles 9-15** | ✅ Complete | High-risk system requirements |

---

*SERAMIS is developed as part of a Master's Thesis (TFM) project at UNIR - Universidad Internacional de La Rioja.*

**Authors:** David Fernández González and Mariano Ortega de Mues

**Directors:** Xiomara Patricia Blanco Valencia and Sergio Castillo

---

**Last Updated:** January 2026 | **Ontology Version:** 0.41.0 | **Status:** Operational
