## About SERAMIS

**SERAMIS** (Semantic Regulation Intelligence System) is a comprehensive platform designed to support organizations in achieving compliance with the **EU AI Act** through intelligent semantic analysis.

### Key Features

- **AI Systems Registry**: Catalog and manage your AI systems with detailed metadata, deployment contexts, and purpose classifications aligned with EU AI Act requirements.

- **Knowledge Graph**: Visualize and explore the semantic relationships between AI systems, regulations, compliance requirements, and risk classifications using our ontology-powered knowledge graph.

- **Ontology Documentation**: Access comprehensive documentation of the AI Act ontology, including classes, properties, and individuals that model regulatory concepts.

- **Symbolic Reasoning**: Apply SWRL rules and SHACL validation to automatically infer compliance requirements, risk levels, and normative criteria based on your AI system's characteristics.

- **Forensic AI Agent**: Analyze real-world AI incidents from the AIAAIC repository using LLM-powered extraction to identify compliance gaps and map violations to EU AI Act requirements.

### Architecture

SERAMIS integrates multiple components:

- **Semantic Layer**: Apache Jena Fuseki for RDF storage and SPARQL querying
- **Reasoning Engine**: Custom reasoner service with SWRL rules for automated inference
- **Forensic Analysis**: LLM-based incident extraction with MCP (Model Context Protocol) integration
- **Persistence**: MongoDB for system data and analysis results

### Getting Started

1. Navigate to **AI Systems DB** to register your AI systems
2. Use **AI Knowledge Graph** to explore regulatory relationships
3. Run **AI Symbolic Reasoning** to infer compliance requirements
4. Analyze incidents with **Forensic AI Agent** for compliance insights

---

*SERAMIS is developed as part of a Master's Thesis (TFM) project at UNIR - Universidad Internacional de La Rioja.*

**Authors:** David Fernández González and Mariano Ortega de Mues

**Directors:** Xiomara Patricia Blanco Valencia and Sergio Castillo
