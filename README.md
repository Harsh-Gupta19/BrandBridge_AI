# BrandBridge AI

"Connecting creators and brands through intelligent matching, explainable AI, and agentic collaboration."

## Project Overview

BrandBridge AI is an IIT Bombay AI/Data Science capstone project. It is a two-sided creator-brand collaboration platform where brands can discover creators for campaigns and creators can find relevant collaboration opportunities.

Current Phase: **Phase 1 - Engineering Foundation**

This repository currently provides the production-oriented monorepo foundation. It does not yet implement live marketplace workflows, AI recommendations, RAG, LangGraph agents, or social-media API integrations.

## Problem Statement

Creator-brand collaboration is often manual, fragmented, and difficult to evaluate objectively. Brands need creators who match campaign goals, audience, budget, platform, and content format. Creators need relevant opportunities and clear proposal workflows. BrandBridge AI will evolve toward an explainable matching system that combines structured marketplace data, ML scoring, semantic similarity, and human approval.

## Key Features

Planned capabilities include:

- Brand and creator registration
- Brand and creator profile management
- Campaign creation and discovery
- Creator search and invitation workflows
- Creator proposal workflows
- ML-based matching and ranking
- Semantic creator-campaign similarity
- RAG over brand guidelines, briefs, documents, and portfolios
- LangGraph-based assisted workflows
- Optional YouTube and Instagram integrations

## Architecture

BrandBridge AI uses a monorepo and a modular monolith backend:

```text
React Frontend
      |
      | REST API
      v
FastAPI Backend
      |
      +-- PostgreSQL with pgvector
      +-- ML modules
      +-- AI/RAG/LangGraph modules
      +-- Social API integration modules
```

The initial architecture intentionally avoids microservices, Kafka, Kubernetes, Redis, and a separate vector database. PostgreSQL remains the source of truth for structured marketplace data, with pgvector planned for embeddings.

## Technology Stack

- Frontend: React, TypeScript, Vite, React Router, TanStack Query, ESLint, Prettier
- Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, psycopg, pytest, Ruff
- Database: PostgreSQL, pgvector
- ML: pandas, numpy, scikit-learn, XGBoost
- AI: sentence-transformers, LangChain, LangGraph
- Infrastructure: Docker, Docker Compose
- CI: GitHub Actions

## Repository Structure

```text
frontend/       React + TypeScript application
backend/        FastAPI modular monolith
notebooks/      Exploratory analysis and experiments
data/           Development-only sample and synthetic data
docs/           Architecture, API, ML, RAG, ADRs, and demo docs
infra/          Deployment and infrastructure notes
scripts/        Local development utility scripts
.github/        CI, pull request template, and issue templates
```

For a beginner-friendly folder-by-folder explanation, read `docs/project-structure.md`.

## Local Development

Copy the example environment file before running services:

```bash
cp .env.example .env
```

Install backend and frontend dependencies separately while the project is in early foundation mode.

## Docker Setup

The intended local Docker workflow is:

```bash
docker compose up --build
```

This starts:

- Frontend on `http://localhost:5173`
- Backend on `http://localhost:8000`
- PostgreSQL on `localhost:5432`

The PostgreSQL image includes pgvector support.

## Environment Configuration

Configuration is environment-driven. Secrets must never be committed. Use `.env.example` as a template and keep `.env` local.

Important variables include:

- `APP_ENV`
- `APP_NAME`
- `API_V1_PREFIX`
- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `CORS_ORIGINS`
- `LLM_PROVIDER`
- `LLM_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `META_APP_ID`
- `META_APP_SECRET`

## Backend Development

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Health endpoints:

- `GET /health`
- `GET /api/v1/health`

Run tests and linting:

```bash
pytest
ruff check .
```

## Frontend Development

From `frontend/`:

```bash
npm install
npm run dev
```

Run linting and build:

```bash
npm run lint
npm run build
```

## AI/ML Roadmap

The AI/ML modules are placeholders in Phase 1. Planned work includes:

- Baseline feature engineering for creator-campaign compatibility
- Logistic Regression, Random Forest, and XGBoost comparison
- Embedding generation for semantic similarity
- RAG over unstructured brand and creator knowledge
- LangGraph workflows with human approval steps
- Explainable ranking outputs for marketplace users

## Testing

Current test foundation:

- Backend pytest tests for health endpoints
- Frontend Vitest smoke test for the home page
- CI workflow for linting, building, and tests

Test scope should grow with implemented behavior.

## Contribution Workflow

Use issues, feature branches, pull requests, tests, and teammate review. Do not commit directly to `main`.

See `CONTRIBUTING.md` for the full workflow.

## Current Project Status

Phase 1 establishes:

- Monorepo structure
- FastAPI application shell
- React application shell
- PostgreSQL and Alembic setup
- AI, ML, RAG, agent, and integration module boundaries
- Docker Compose for local development
- Documentation and ADRs
- CI foundation

## Future Work

- Implement authentication and authorization
- Build creator and brand profile CRUD
- Implement campaign and proposal workflows
- Add real database migrations as schemas mature
- Build ML recommendation baselines
- Add embeddings and pgvector retrieval
- Introduce LangGraph workflows
- Integrate YouTube and Instagram with optional failure-tolerant behavior

## Current Non-Goals

These are not implemented in Phase 1:

- MCP server or MCP client tools
- Helix integration
- Real LangGraph execution
- Real LangChain LLM calls

The repository already has folders where LangChain, LangGraph, RAG, embeddings, tools, and prompts will live later. See `docs/architecture/ai-agent-workflow.md`.
