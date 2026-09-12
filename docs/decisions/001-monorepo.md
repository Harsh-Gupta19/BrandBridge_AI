# 001 - Monorepo

## Status

Accepted

## Context

The project has a React frontend, FastAPI backend, ML code, AI/RAG modules, documentation, infrastructure, and sample data. The team is small and will work over a 2-3 month academic timeline.

## Decision

Use a single monorepo for all project code and documentation.

## Alternatives Considered

- Multiple repositories for frontend, backend, ML, and infrastructure
- A separate repository for notebooks and experiments

## Consequences

The team gets simpler onboarding, shared pull requests, consistent documentation, and easier local development. Repository boundaries must be kept clean through folders and conventions.
