# SERAMIS Frontend

Aplicación React para SERAMIS (Semantic Regulation Intelligence System) - Plataforma de cumplimiento EU AI Act.

## Descripción

Frontend SPA que proporciona una interfaz visual para:
- Registro y gestión de sistemas de IA
- Visualización del Knowledge Graph semántico
- Razonamiento simbólico SWRL
- Análisis forense de incidentes IA
- Navegación de Evidence Plans DPV

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── App.tsx              # Componente raíz con BrowserRouter
│   ├── main.tsx             # Entry point de React
│   ├── index.css            # Estilos globales (Tailwind CSS)
│   ├── components/          # Componentes reutilizables
│   │   └── Navbar.tsx       # Barra de navegación principal
│   ├── pages/               # Páginas de la aplicación
│   │   ├── DashboardPage.tsx      # Dashboard principal (/)
│   │   ├── SystemsPage.tsx        # Registro de sistemas IA (/systems)
│   │   ├── GraphView.tsx          # Knowledge Graph 3D (/graph)
│   │   ├── OntologyDocs.tsx       # Documentación ontología (/ontology)
│   │   ├── ReasoningPage.tsx      # Razonamiento simbólico (/reasoning)
│   │   ├── ForensicAgentPage.tsx  # Agente forense (/forensic)
│   │   ├── DPVPage.tsx            # Evidence Plans DPV (/dpv)
│   │   └── SystemCard.tsx         # Componente de tarjeta de sistema
│   ├── routes/
│   │   └── AppRoutes.tsx    # Definición de rutas React Router
│   └── lib/                 # Clientes API
│       ├── api.ts           # API cliente para backend principal (8000)
│       └── forensicApi.ts   # API cliente para Forensic Agent (8002)
├── public/
│   ├── Welcome2SERAMIS.md   # Contenido del Dashboard
│   ├── seramis-logo.svg     # Logo SERAMIS
│   └── logo-unir.png        # Logo UNIR
└── dist/                    # Build de producción
```

## Páginas

| Ruta | Página | Descripción |
|------|--------|-------------|
| `/` | Dashboard | Bienvenida y documentación del proyecto |
| `/systems` | AI Systems DB | Registro de sistemas de IA con metadatos EU AI Act |
| `/graph` | AI Knowledge Graph | Visualización 3D del grafo semántico |
| `/ontology` | Ontology Docs | Documentación de la ontología v0.41.0 |
| `/reasoning` | AI Symbolic Reasoning | Ejecución de inferencia SWRL |
| `/forensic` | Forensic AI Agent | Análisis forense de incidentes AIAAIC |
| `/dpv` | DPV Browser | Navegador de Evidence Plans |

## Características Principales

### Knowledge Graph 3D
- Renderizado con **react-force-graph-3d** y **Three.js**
- Parsing RDF con **rdflib** y **N3**
- Filtrado por categorías: System, Purpose, Deployment, Technical, Capability, Compliance, AIRO

### Forensic AI Agent
- Carga de incidentes AIAAIC (2,139+ casos)
- **Pipeline Mode**: Flujo determinista de 7 pasos
- **ReAct Agent Mode**: Agente autónomo LangGraph (experimental)
- Streaming SSE en tiempo real
- Clasificación Art. 3(49) y detección Art. 73
- Exportación PDF

### DPV Evidence Plans
- 14 tipos de requisitos con ~40 items de evidencia
- Prioridades: CRITICAL, HIGH, MEDIUM, LOW
- Roles: Deployer, Provider, DPO, Legal
- Templates y guías de cumplimiento

## Stack Tecnológico

| Tecnología | Versión | Uso |
|------------|---------|-----|
| React | 19.1 | Framework UI |
| TypeScript | 5.8 | Tipado estático |
| Vite | 6.3 | Build tool y dev server |
| Tailwind CSS | 3.4 | Framework CSS utility-first |
| React Router | 7.6 | Routing SPA |
| react-force-graph-3d | 1.29 | Visualización 3D de grafos |
| Three.js | 0.181 | Renderizado 3D WebGL |
| rdflib | 2.2 | Manipulación RDF |
| N3 | 1.26 | Parsing N3/Turtle |
| react-markdown | 9.0 | Renderizado Markdown |

## Instalación

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Build de producción
npm run build

# Preview del build
npm run preview
```

## Variables de Entorno

Crear archivo `.env` o `.env.local`:

```bash
VITE_API_URL=http://localhost:8000/api       # Backend principal
VITE_FORENSIC_API_URL=http://localhost:8002  # Forensic Agent
```

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Inicia servidor de desarrollo con hot reload |
| `npm run build` | Genera build de producción en `dist/` |
| `npm run preview` | Preview local del build de producción |
| `npm run tailwind` | Compila Tailwind CSS en modo watch |

## Integración con Servicios

```
Frontend (3003) ────► Backend API (8000)
                     ├── /api/systems
                     ├── /api/vocab/*
                     └── /aiaaic/incidents

Frontend (3003) ────► Forensic Agent (8002)
                     ├── /health
                     ├── /forensic/analyze
                     ├── /forensic/analyze-stream (SSE)
                     └── /forensic/systems

Frontend (3003) ────► Ontology Docs (80)
                     └── /docs/index-{locale}.html
```

## Clientes API

### `lib/api.ts` - Backend Principal
```typescript
fetchSystems()                    // Lista sistemas registrados
createSystem(data)                // Crea nuevo sistema
fetchVocabulary(path)             // Obtiene vocabularios de la ontología
generateEvidencePlan(urn)         // Genera Evidence Plan DPV
```

### `lib/forensicApi.ts` - Forensic Agent
```typescript
loadIncidents()                   // Carga incidentes AIAAIC (CSV)
analyzeIncident(request)          // Analiza incidente
analyzeIncidentStream(request)    // Análisis con streaming SSE
getForensicSystems()              // Lista sistemas forenses
deleteForensicSystem(urn)         // Elimina sistema forense
```

## Configuración ESLint

El proyecto usa ESLint con TypeScript-ESLint para linting:

```bash
# Ejecutar linter
npx eslint src/
```

## Dark Mode

La aplicación soporta dark mode mediante clases de Tailwind CSS (`dark:*`). El modo se detecta automáticamente del sistema operativo.

---

**Versión:** 1.0.0
**Compatibilidad:** Ontología EU AI Act v0.41.0
**Puerto por defecto:** 3003
**Última Actualización:** Enero 2026
