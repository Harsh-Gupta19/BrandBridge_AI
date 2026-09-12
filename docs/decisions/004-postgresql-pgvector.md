# 004 - PostgreSQL With pgvector

## Status

Accepted

## Context

The platform needs structured marketplace data and future semantic retrieval. A separate vector database would add operational complexity.

## Decision

Use PostgreSQL as the source of truth and pgvector for vector similarity.

## Alternatives Considered

- PostgreSQL plus a separate vector database
- A document database as the primary store
- In-memory vector search only

## Consequences

Structured records and embeddings can live in one operational database for the capstone phase. Retrieval design must still distinguish relational queries from vector search.
