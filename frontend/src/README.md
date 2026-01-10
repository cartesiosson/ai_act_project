# SERAMIS Frontend - Source Code

Código fuente de la aplicación React para SERAMIS (Semantic Regulation Intelligence System).

## Estructura de Directorios

```
src/
├── App.tsx              # Componente raíz con BrowserRouter
├── main.tsx             # Entry point de React
├── index.css            # Estilos globales (Tailwind CSS)
├── vite-env.d.ts        # Tipos de Vite
├── components/          # Componentes reutilizables
│   └── Navbar.tsx       # Barra de navegación principal
├── pages/               # Páginas de la aplicación
│   ├── DashboardPage.tsx      # Dashboard principal (/)
│   ├── SystemsPage.tsx        # Registro de sistemas IA (/systems)
│   ├── GraphView.tsx          # Knowledge Graph 3D (/graph)
│   ├── OntologyDocs.tsx       # Documentación ontología (/ontology)
│   ├── ReasoningPage.tsx      # Razonamiento simbólico (/reasoning)
│   ├── ForensicAgentPage.tsx  # Agente forense (/forensic)
│   ├── DPVPage.tsx            # Evidence Plans DPV (/dpv)
│   └── SystemCard.tsx         # Componente de tarjeta de sistema
├── routes/              # Configuración de rutas
│   └── AppRoutes.tsx    # Definición de rutas React Router
├── lib/                 # Clientes API y utilidades
│   ├── api.ts           # API cliente para backend principal (8000)
│   └── forensicApi.ts   # API cliente para Forensic Agent (8002)
└── assets/              # Assets estáticos
    └── react.svg
```

## Páginas

### Dashboard (`/`)
Página de bienvenida con documentación del proyecto. Carga el contenido desde `Welcome2SERAMIS.md`.

### AI Systems DB (`/systems`)
Registro y gestión de sistemas de IA:
- Creación de sistemas con metadatos EU AI Act
- Selección de propósitos, contextos de despliegue y capacidades
- Vocabularios cargados dinámicamente desde la ontología

### AI Knowledge Graph (`/graph`)
Visualización 3D del grafo de conocimiento:
- Renderizado con **react-force-graph-3d** y **Three.js**
- Parsing RDF con **rdflib** y **N3**
- Filtrado por categorías: System, Purpose, Deployment, Technical, Capability, Compliance, AIRO
- Controles de visualización: etiquetas, distancia de enlaces

### Ontology Docs (`/ontology`)
Documentación de la ontología EU AI Act v0.41.0:
- Embebida en iframe desde servidor de documentación
- Soporte multiidioma (español/inglés)

### AI Symbolic Reasoning (`/reasoning`)
Ejecución de razonamiento SWRL sobre sistemas:
- Selección de sistemas (manuales y forenses)
- Invocación del Reasoner Service (puerto 8001)
- Visualización de inferencias: criterios, requisitos, nivel de riesgo
- Exportación TTL raw

### Forensic AI Agent (`/forensic`)
Análisis forense de incidentes IA:
- Carga de incidentes AIAAIC (2,139+ casos)
- Filtros: sector, país, año, tecnología, búsqueda textual
- **Modos de análisis**:
  - *Pipeline Mode*: Flujo determinista de 7 pasos
  - *ReAct Agent Mode*: Agente autónomo LangGraph (experimental)
- Streaming SSE en tiempo real
- Resultados:
  - Clasificación de riesgo EU AI Act
  - Tipo de incidente grave Art. 3(49)
  - Obligación notificación Art. 73
  - Mappings ISO 42001 y NIST AI RMF
  - Plan de evidencias DPV (opcional)
- Gestión de sistemas analizados
- Exportación PDF

### DPV Browser (`/dpv`)
Navegador de Evidence Plans basados en DPV 2.2:
- Lista de sistemas con planes de evidencia
- Filtrado por nivel de riesgo
- Visualización de:
  - Items de evidencia por requisito
  - Prioridades (CRITICAL, HIGH, MEDIUM, LOW)
  - Tipos de evidencia (Policy, Technical, Audit, Training, Assessment)
  - Roles responsables (Deployer, Provider, DPO, Legal)
  - Templates y guías

## Clientes API

### `lib/api.ts`
Cliente para el backend principal (puerto 8000):
```typescript
fetchSystems()                    // GET /api/systems
fetchSystemByUrn(urn)             // GET /api/systems/:urn
createSystem(data)                // POST /api/systems
fetchVocabulary(path)             // GET /api/vocab/:path
fetchAlgorithmSubtypes(id)        // GET /api/vocab/algorithmtypes/:id/subtypes
generateEvidencePlan(urn)         // POST /api/systems/:urn/generate-evidence-plan
getEvidencePlan(urn)              // GET /api/systems/:urn/evidence-plan
```

### `lib/forensicApi.ts`
Cliente para el Forensic Agent (puerto 8002):
```typescript
loadIncidents()                   // GET /aiaaic/incidents (CSV parsing)
checkHealth()                     // GET /health
analyzeIncident(request)          // POST /forensic/analyze
analyzeIncidentStream(request)    // POST /forensic/analyze-stream (SSE)
getForensicSystems(limit, offset) // GET /forensic/systems
getForensicSystem(urn)            // GET /forensic/systems/:urn
deleteForensicSystem(urn)         // DELETE /forensic/systems/:urn
```

**Tipos exportados:**
- `Incident` - Datos de incidente AIAAIC
- `ForensicAnalysisResult` - Resultado del análisis forense
- `ForensicSystem` - Sistema forense persistido
- `StreamEvent` - Evento SSE de streaming
- `EvidencePlan`, `EvidenceItem` - Estructuras DPV

## Stack Tecnológico

| Tecnología | Uso |
|------------|-----|
| **React 19** | Framework UI |
| **TypeScript 5.8** | Tipado estático |
| **Vite 6** | Build tool y dev server |
| **Tailwind CSS 3.4** | Framework CSS utility-first |
| **React Router 7** | Routing SPA |
| **react-force-graph-3d** | Visualización 3D de grafos |
| **Three.js** | Renderizado 3D WebGL |
| **rdflib + N3** | Parsing y manipulación RDF |
| **react-markdown** | Renderizado Markdown |

## Variables de Entorno

```bash
VITE_API_URL=http://localhost:8000/api       # Backend principal
VITE_FORENSIC_API_URL=http://localhost:8002  # Forensic Agent
```

## Scripts

```bash
npm run dev       # Inicia servidor de desarrollo (hot reload)
npm run build     # Genera build de producción
npm run preview   # Preview del build de producción
npm run tailwind  # Compila Tailwind CSS en modo watch
```

## Integración con Backend

```
Frontend (3003) ──────► Backend API (8000)
                       ├── /api/systems
                       ├── /api/vocab/*
                       └── /aiaaic/incidents

Frontend (3003) ──────► Forensic Agent (8002)
                       ├── /health
                       ├── /forensic/analyze
                       ├── /forensic/analyze-stream (SSE)
                       └── /forensic/systems

Frontend (3003) ──────► Ontology Docs (80)
                       └── /docs/index-{locale}.html
```

## Convenciones de Código

- Componentes funcionales con hooks
- Nombres de archivos en PascalCase para componentes
- Tipos TypeScript para todas las interfaces API
- Tailwind CSS para estilos (dark mode soportado)
- ESLint + TypeScript-ESLint para linting

---

**Versión:** 1.0.0
**Compatibilidad:** Ontología EU AI Act v0.41.0
**Última Actualización:** Enero 2026
