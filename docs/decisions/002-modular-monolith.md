# 002 - Modular Monolith

## Status

Accepted

## Context

BrandBridge AI needs marketplace APIs, database access, recommendation logic, AI modules, RAG, LangGraph orchestration, and social integrations. Splitting these too early would create operational overhead.

## Decision

Build the backend as a modular monolith with clearly separated packages.

## Alternatives Considered

- Microservices
- Serverless functions per feature
- Separate ML and API services from day one

## Consequences

The project stays easy to run and reason about. Module boundaries must be maintained so future extraction remains possible if there is a genuine need.
