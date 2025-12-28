## About SERAMIS

**SERAMIS** (**Semantic Regulation Intelligence System**) is a comprehensive platform designed to support organizations in achieving **compliance** with the **EU AI Act** through intelligent **semantic analysis**.

### Key Features

- **AI Systems Registry**: Catalog and manage your **AI systems** with detailed **metadata**, **deployment contexts**, and **purpose classifications** aligned with **EU AI Act** requirements.

- **Knowledge Graph**: Visualize and explore the **semantic relationships** between AI systems, regulations, **compliance requirements**, and **risk classifications** using our **ontology-powered** knowledge graph.

- **Ontology Documentation**: Access comprehensive documentation of the **AI Act ontology**, including **classes**, **properties**, and **individuals** that model regulatory concepts.

- **Symbolic Reasoning**: Apply **SWRL rules** and **SHACL validation** to automatically infer compliance requirements, **risk levels**, and **normative criteria** based on your AI system's characteristics.

- **Forensic AI Agent**: Analyze real-world **AI incidents** from the [AIAAIC repository](https://www.aiaaic.org/aiaaic-repository) using **LLM-powered extraction** to identify **compliance gaps** and map **violations** to **EU AI Act** requirements.

- **DPV Evidence Plans**: Generate **actionable compliance roadmaps** using the **[Data Privacy Vocabulary (DPV)](https://w3id.org/dpv)** standard. For each identified compliance gap, SERAMIS generates specific **evidence requirements**, **responsible roles** (Deployer, Provider, DPO, Legal), **collection frequencies**, and **document templates** to demonstrate compliance with **EU AI Act** obligations.

### Ontology Interoperability

SERAMIS ontology integrates with established **W3C**, **EU**, and research ontologies:

- **[AIRO (AI Risk Ontology)](https://w3id.org/airo)**: 30+ concept mappings including **risk levels** (`ai:HighRisk ↔ airo:HighRiskLevel`), **purposes** (`ai:Purpose ≡ airo:Purpose`), **evaluation criteria** (`ai:Criterion ≡ airo:EvaluationCriterion`), and **compliance requirements** (`ai:ComplianceRequirement ≡ airo:ComplianceRequirement`).

- **[DPV (Data Privacy Vocabulary)](https://w3id.org/dpv)**: Integration for **evidence plans**, **organizational roles**, and **data processing** concepts aligned with GDPR and AI Act requirements.

- **[ELI (European Legislation Identifier)](https://eur-lex.europa.eu/eli-register/about.html)**: Direct links to **EUR-Lex** official legislation using the EU standard for legislation identifiers. Each requirement and criterion references its **source article** via `eli:cites` (e.g., `art_14/oj` for Human Oversight). This enables **semantic traceability** to the official legal text and ensures **persistent, dereferenceable URIs** following Council Conclusions 2012/C 325/02.

- **[ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)**: 15 bidirectional mappings between **EU AI Act requirements** and **ISO 42001 controls** (Sections 5-10). Enables **multi-framework compliance analysis** and **forensic investigation** of certified systems. Properties: `ai:equivalentToISOControl`, `ai:isoSection`, `ai:mappingConfidence`.

- **[NIST AI RMF 1.0](https://www.nist.gov/itl/ai-risk-management-framework)**: 16 mappings covering all 4 NIST functions (**GOVERN**, **MAP**, **MEASURE**, **MANAGE**) for **global incident forensics** and **US-EU comparative analysis**. Properties: `ai:equivalentToNISTFunction`, `ai:nistCategory`, `ai:nistApplicabilityContext`.

### Architecture

SERAMIS integrates multiple components:

- **Semantic Layer**: **Apache Jena Fuseki** for **RDF storage** and **SPARQL querying**
- **Reasoning Engine**: Custom **reasoner service** with **SWRL rules** for **automated inference**
- **Forensic Analysis**: **LLM-based** incident extraction with **MCP** (Model Context Protocol) integration
- **Persistence**: **MongoDB** for system data and analysis results

### Getting Started

1. Navigate to **AI Systems DB** to register your AI systems
2. Use **AI Knowledge Graph** to explore regulatory relationships
3. Run **AI Symbolic Reasoning** to infer compliance requirements
4. Analyze incidents with **Forensic AI Agent** for compliance insights
5. Generate **DPV Evidence Plans** to create actionable compliance roadmaps

---

*SERAMIS is developed as part of a Master's Thesis (TFM) project at UNIR - Universidad Internacional de La Rioja.*

**Authors:** David Fernández González and Mariano Ortega de Mues

**Directors:** Xiomara Patricia Blanco Valencia and Sergio Castillo
