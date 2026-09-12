# Backend App Package Guide

This folder contains the actual backend application code.

If you are new, read this file before changing backend code.

## Mental Model

The backend should follow this flow:

```text
HTTP request
  -> API endpoint
  -> service
  -> repository
  -> database
```

AI and ML modules should be called from services, not directly from route functions.

## Folder Responsibilities

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
```

## `main.py`

Creates the FastAPI app.

This is where global app setup happens:

- App title and version
- CORS middleware
- Root `/health` endpoint
- Versioned API router registration

Do not put feature business logic here.

## `core/`

Shared infrastructure used by many backend modules.

Examples:

- Environment settings
- Logging setup
- Security helpers

## `api/`

FastAPI route definitions.

Each endpoint file should:

- Define URL paths
- Validate request/response schemas
- Call service functions
- Stay small

Endpoint files should not:

- Contain large business logic
- Directly train models
- Directly call notebooks
- Directly contain complex SQL queries

## `schemas/`

Pydantic models for API inputs and outputs.

Example future files:

```text
schemas/user.py
schemas/creator.py
schemas/campaign.py
schemas/proposal.py
```

## `services/`

Business logic.

Services answer questions like:

- Can this user create this campaign?
- Which creators should be recommended?
- Should this proposal status change be allowed?
- Which ML or AI module should be called?

## `repositories/`

Database access.

Repositories answer questions like:

- Fetch campaign by ID
- List creators matching filters
- Save a proposal
- Update a user profile

## `models/`

SQLAlchemy database table definitions.

Current models:

- `User`
- `CreatorProfile`
- `BrandProfile`
- `Campaign`
- `Proposal`

## `database/`

Database engine, sessions, and shared base class.

Most developers will use this indirectly through repositories.

## `ml/`

Machine learning modules.

Use this for recommendation feature engineering, training, inference, and evaluation code after experiments are ready to become application code.

## `ai/`

AI modules.

Use this for:

- LangChain LLM wrappers
- Embeddings
- RAG
- LangGraph agents
- Deterministic agent tools
- Prompt templates

Phase 1 has placeholders only.

## `integrations/`

External API modules.

Current placeholders:

- YouTube
- Instagram

External API failures should not stop the base app from working.
