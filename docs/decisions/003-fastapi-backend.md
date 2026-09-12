# 003 - FastAPI Backend

## Status

Accepted

## Context

The backend needs typed APIs, Python ML compatibility, async-friendly web support, OpenAPI documentation, and a low-friction developer experience.

## Decision

Use FastAPI with Pydantic v2 for the backend API.

## Alternatives Considered

- Django
- Flask
- Node.js backend

## Consequences

FastAPI aligns well with Python ML and typed API development. The team must keep route functions thin and place business logic in services.
