# Project Structure Guide

This guide is written for beginner developers joining BrandBridge AI.

The most important idea: this is a monorepo. That means frontend, backend, ML, AI, documentation, Docker, and scripts live in one Git repository.

## Top-Level Folders

```text
BrandBridge_AI/
|-- frontend/        React + TypeScript user interface
|-- backend/         FastAPI backend API and Python application code
|-- docs/            Architecture, API, AI, ML, RAG, and planning documents
|-- data/            Development-only sample and synthetic data
|-- notebooks/       Data analysis and ML experiment notebooks
|-- infra/           Docker and deployment notes
|-- scripts/         Small local development helper scripts
|-- .github/         GitHub Actions, PR template, and issue templates
|-- docker-compose.yml
|-- .env.example
|-- README.md
|-- CONTRIBUTING.md
|-- AGENTS.md
```

## What To Work On First

If you are building a React page:

- Start in `frontend/src/pages/`.
- Put reusable UI in `frontend/src/components/`.
- Put feature-specific code in `frontend/src/features/<feature-name>/`.
- Use `frontend/src/services/` when calling backend APIs.

If you are building a backend API:

- Start in `backend/app/api/v1/endpoints/`.
- Put request and response schemas in `backend/app/schemas/`.
- Put business logic in `backend/app/services/`.
- Put database queries in `backend/app/repositories/`.
- Put database tables in `backend/app/models/`.

If you are building ML features:

- Explore ideas in `notebooks/`.
- Put reusable feature code in `backend/app/ml/features/`.
- Put training code in `backend/app/ml/training/`.
- Put model loading or scoring code in `backend/app/ml/inference/`.

If you are building AI/RAG/agent features:

- Read `docs/architecture/ai-agent-workflow.md`.
- Put LLM wrappers in `backend/app/ai/llm/`.
- Put embeddings code in `backend/app/ai/embeddings/`.
- Put RAG retrieval code in `backend/app/ai/rag/`.
- Put LangGraph workflow code in `backend/app/ai/agents/`.
- Put deterministic tool functions in `backend/app/ai/tools/`.
- Put prompt templates in `backend/app/ai/prompts/`.

## Backend Folder Details

```text
backend/
|-- app/
|   |-- main.py                  FastAPI app object and middleware
|   |-- core/                    Settings, logging, security helpers
|   |-- api/v1/                  API routers and endpoint files
|   |-- schemas/                 Pydantic request and response models
|   |-- services/                Business logic
|   |-- repositories/            Database access layer
|   |-- models/                  SQLAlchemy database models
|   |-- database/                Engine, sessions, shared database base
|   |-- ml/                      ML features, training, inference, evaluation
|   |-- ai/                      LLM, embeddings, RAG, agents, tools, prompts
|   |-- integrations/            External APIs such as YouTube and Instagram
|-- tests/                       Pytest tests
|-- alembic/                     Database migration files
|-- requirements.txt             Runtime dependencies
|-- requirements-dev.txt         Runtime plus developer/test dependencies
|-- Dockerfile                   Backend container
```

Backend rule of thumb:

```text
Endpoint -> Service -> Repository -> Database
```

Do not put database queries or large business logic directly inside route functions.

## Frontend Folder Details

```text
frontend/
|-- src/
|   |-- app/                     App-level providers and router
|   |-- components/              Shared UI components
|   |-- features/                Feature-specific UI and logic
|   |-- pages/                   Route-level page components
|   |-- services/                API client and server calls
|   |-- hooks/                   Shared React hooks
|   |-- types/                   Shared TypeScript types
|   |-- utils/                   Small helper functions
|   |-- config/                  Frontend environment config
|   |-- mocks/                   UI development mock data
|-- tests/                       Vitest and Testing Library tests
|-- public/                      Static files served by Vite
|-- package.json                 Frontend dependencies and scripts
|-- Dockerfile                   Frontend container
```

Frontend rule of thumb:

```text
Page -> Feature components -> Hooks/services -> Backend API
```

Keep pages simple. Move reusable or feature-specific pieces into `components/` or `features/`.

## Documentation Folder Details

```text
docs/
|-- architecture/                System design and workflow plans
|-- api/                         API conventions and endpoint notes
|-- ml/                          ML roadmap and feature notes
|-- rag/                         RAG retrieval planning
|-- integrations/                External integration planning
|-- observability/               Logging, tracing, monitoring planning
|-- diagrams/                    Mermaid or image diagrams
|-- decisions/                   ADR documents
|-- demo-scenario.md             Future target demo flow
```

Docs should clearly say whether something is:

- Implemented now
- Planned later
- A proposal that needs approval

## Data Folder Details

```text
data/
|-- samples/                     Small JSON examples for local UI/API testing
|-- synthetic/                   Generated fake datasets for experiments
```

Do not put real user data, private data, or secrets here.

## Notebooks Folder Details

```text
notebooks/
|-- data_analysis/               Explore available data
|-- feature_engineering/         Try matching features
|-- model_experiments/           Compare model approaches
|-- evaluation/                  Measure model quality
```

Notebook code is experimental. Before using it in the app, convert it into reviewed Python modules under `backend/app/ml/`.

## Current vs Future

Currently implemented:

- FastAPI app foundation
- Health endpoints
- Placeholder API routers
- SQLAlchemy model placeholders
- Alembic setup
- React routing foundation
- Docker Compose foundation
- AI/ML/RAG/agent folder boundaries

Not implemented yet:

- Real authentication
- Creator and brand CRUD
- Campaign and proposal workflows
- Real recommendations
- Real LangGraph execution
- Real RAG retrieval
- MCP server or MCP client tools
- Helix integration
- YouTube or Instagram API calls

## How To Add A New Backend Feature

Example: adding creator profile creation.

1. Add or update SQLAlchemy model fields in `backend/app/models/`.
2. Add a database migration in `backend/alembic/versions/`.
3. Add Pydantic schemas in `backend/app/schemas/`.
4. Add repository functions in `backend/app/repositories/`.
5. Add business logic in `backend/app/services/`.
6. Add route functions in `backend/app/api/v1/endpoints/`.
7. Register the router in `backend/app/api/v1/router.py`.
8. Add tests in `backend/tests/`.

## How To Add A New Frontend Feature

Example: adding a creator profile form.

1. Create route page in `frontend/src/pages/`.
2. Add feature-specific components in `frontend/src/features/creators/`.
3. Add API function in `frontend/src/services/`.
4. Add TypeScript types in `frontend/src/types/`.
5. Wire the route in `frontend/src/app/router.tsx`.
6. Add a small test in `frontend/tests/`.

## Naming Guidance

- Use clear, boring names.
- Avoid short unclear names like `mgr`, `tmp`, or `x`.
- Keep files focused.
- Avoid giant files.
- Add comments only when they explain something non-obvious.
