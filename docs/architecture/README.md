# Architecture

BrandBridge AI starts as a monorepo with a React frontend and FastAPI backend.

```text
frontend/ React + TypeScript
backend/  FastAPI modular monolith
database/ PostgreSQL with pgvector
```

The backend owns marketplace APIs, database access, ML modules, AI/RAG/LangGraph modules, and social integrations. These are separated by module boundaries inside one deployable application so the team can move quickly without premature distributed-system complexity.

Future service extraction should require a documented technical reason and an ADR.
