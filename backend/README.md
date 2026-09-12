# Backend Guide

The backend is a FastAPI modular monolith.

It owns:

- REST API endpoints
- Database models and sessions
- Business services
- Repository/database access code
- ML modules
- AI, RAG, and LangGraph modules
- Social API integration modules

## Current Status

Implemented now:

- FastAPI app in `app/main.py`
- CORS setup
- Central settings in `app/core/config.py`
- Health endpoints:
  - `GET /health`
  - `GET /api/v1/health`
- Placeholder routers for auth, creators, brands, campaigns, proposals, and recommendations
- SQLAlchemy model placeholders
- Alembic setup with an initial migration
- pytest health endpoint tests

Not implemented yet:

- Real authentication
- Real CRUD endpoints
- Recommendation models
- LangGraph execution
- RAG retrieval
- External social API calls

## Run Locally

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open:

- `http://localhost:8000/health`
- `http://localhost:8000/api/v1/health`
- `http://localhost:8000/docs`

## Test and Lint

From `backend/`:

```bash
pytest
ruff check .
```

## Folder Structure

```text
app/
|-- main.py
|-- core/
|-- api/
|-- database/
|-- models/
|-- schemas/
|-- repositories/
|-- services/
|-- ml/
|-- ai/
|-- integrations/
tests/
alembic/
```

## `app/main.py`

This is where the FastAPI application object is created.

It configures:

- Application title
- Application version
- CORS middleware
- Root health endpoint
- Versioned API router

Beginner note: if the backend server starts, it is because `uvicorn app.main:app --reload` loads the `app` variable from this file.

## `app/core/`

Shared application setup.

- `config.py` reads environment variables.
- `logging.py` configures logs.
- `security.py` contains security helpers.

Do not hardcode secrets. Use `.env` locally and `.env.example` as the template.

## `app/api/v1/`

Versioned REST API layer.

- `router.py` combines all v1 endpoint modules.
- `endpoints/health.py` has the API health endpoint.
- Other endpoint files are placeholders for future modules.

Route functions should stay thin. They should call services instead of holding business logic directly.

## `app/schemas/`

Pydantic models for API input and output.

Use schemas for:

- Request bodies
- Response bodies
- API validation

Do not reuse SQLAlchemy database models directly as API response contracts.

## `app/models/`

SQLAlchemy 2 database models.

Current models:

- `User`
- `CreatorProfile`
- `BrandProfile`
- `Campaign`
- `Proposal`

These models describe database tables. They are not the same thing as Pydantic schemas.

## `app/database/`

Database configuration.

- `base.py` defines the shared SQLAlchemy base class.
- `session.py` creates the database engine and session factory.

Future endpoints that need the database should use dependency injection and repository functions.

## `app/repositories/`

Database query layer.

Use repositories for:

- Fetching rows
- Creating rows
- Updating rows
- Query-specific database logic

Keep raw SQLAlchemy queries out of API route functions.

## `app/services/`

Business logic layer.

Services should coordinate:

- Input validation beyond simple schema validation
- Calls to repositories
- Calls to ML or AI modules
- Workflow decisions

Example flow:

```text
API route -> service function -> repository function -> database
```

## `app/ml/`

Machine learning code lives here after it graduates from notebooks.

Subfolders:

- `features/`: convert raw data into model features
- `training/`: train Logistic Regression, Random Forest, XGBoost, or other approved models
- `inference/`: load approved models and calculate scores
- `evaluation/`: compare model quality
- `artifacts/`: local model artifacts, ignored by Git except README

Do not call notebooks directly from backend APIs.

## `app/ai/`

AI, RAG, LangChain, and LangGraph-related code lives here.

Subfolders:

- `llm/`: LLM provider wrappers and text generation services
- `embeddings/`: embedding generation and semantic similarity
- `rag/`: retrieval over unstructured documents using pgvector
- `agents/`: LangGraph workflows and graph state
- `tools/`: deterministic tool functions callable by agents
- `prompts/`: version-controlled prompt templates

Phase 1 includes structure and docs only. Real LLM calls and graph execution are future work.

## `app/integrations/`

External APIs live here.

Current placeholders:

- `youtube/`
- `instagram/`

Important rule: the base platform should continue working even if external social APIs are unavailable.

## Alembic

Alembic manages database migrations.

Important files:

- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/0001_initial_foundation.py`

The initial migration creates foundation tables and enables `pgvector`.

## Adding A New Endpoint

Example: `GET /api/v1/creators`.

1. Define response schema in `app/schemas/`.
2. Add service function in `app/services/`.
3. Add repository function in `app/repositories/` if database access is needed.
4. Add route in `app/api/v1/endpoints/creators.py`.
5. Register router in `app/api/v1/router.py` if it is a new endpoint module.
6. Add tests in `tests/unit/` or `tests/integration/`.

## Dependency Notes

`requirements.txt` includes runtime packages:

- FastAPI and Uvicorn for the API
- Pydantic and pydantic-settings for typed config
- SQLAlchemy, Alembic, and psycopg for PostgreSQL
- pandas, numpy, scikit-learn, and XGBoost for ML
- sentence-transformers for embeddings
- LangChain and LangGraph for future AI workflows

`requirements-dev.txt` adds development tools such as pytest, httpx, and Ruff.
