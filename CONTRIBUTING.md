# Contributing to SERAMIS

First off, thank you for taking the time to contribute! 🎉

SERAMIS is an academic and open-source project. Contributions of all kinds are
welcome: bug reports, feature proposals, documentation improvements, ontology
refinements and code.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How can I contribute?](#how-can-i-contribute)
- [Development setup](#development-setup)
- [Branching and commits](#branching-and-commits)
- [Pull request process](#pull-request-process)
- [Coding guidelines](#coding-guidelines)
- [Reporting security issues](#reporting-security-issues)

## Code of Conduct

This project and everyone participating in it is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to
uphold it.

## How can I contribute?

- **Reporting bugs** — open an issue using the *Bug report* template. Include
  steps to reproduce, the affected service, and logs where possible.
- **Suggesting features** — open an issue using the *Feature request* template.
- **Improving the ontology** — changes under `ontologias/` should preserve
  backwards compatibility where possible and update `ontologias/CHANGELOG.md`.
- **Code** — pick an open issue (or open one first to discuss) and submit a PR.

## Development setup

The full stack runs via Docker Compose:

```bash
cp .env.example .env      # adjust values; never commit your .env
docker compose up --build
```

Services and ports:

| Service          | Port  | Description                          |
|------------------|-------|--------------------------------------|
| Frontend (Vite)  | 5173  | React UI                             |
| Backend (FastAPI)| 8000  | Core derivation & requirements API   |
| Reasoner         | 8001  | SWRL/Pellet inference                 |
| Forensic agent   | 8002  | LLM incident analysis (ReAct)        |
| MCP SPARQL       | 8080  | Model Context Protocol SPARQL server |
| Ontology docs    | 80    | Static ontology documentation        |
| Fuseki           | 3030  | RDF triple store                     |
| MongoDB          | 27017 | Document persistence                 |
| Ollama           | 11434 | Local LLM provider                   |

For frontend-only work:

```bash
cd frontend
npm ci
npm run dev
```

## Branching and commits

- Branch from `main` using a descriptive prefix:
  `feat/...`, `fix/...`, `docs/...`, `chore/...`, `refactor/...`.
- Write clear, imperative commit messages (e.g. `fix: escape IRIs in SPARQL delete`).
- Keep commits focused; avoid mixing unrelated changes.

## Pull request process

1. Ensure the project builds (`npm run build` in `frontend/`; services start
   under `docker compose`).
2. Update documentation and `CHANGELOG` entries where relevant.
3. Fill in the PR template and link the related issue.
4. At least one maintainer review is required before merge.

## Coding guidelines

- **Python**: follow PEP 8. Prefer explicit error handling over bare `except`.
  Validate and sanitize any user input that reaches a SPARQL or database query.
- **TypeScript/React**: keep `strict` mode clean; avoid `any`; prefer small,
  composable components.
- Do not commit secrets. Use `.env` (git-ignored) and keep `.env.example`
  populated with safe placeholder values only.

## Reporting security issues

Please do **not** open public issues for security vulnerabilities. See
[SECURITY.md](SECURITY.md) for responsible disclosure instructions.
