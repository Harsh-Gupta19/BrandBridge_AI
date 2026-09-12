# Embeddings

Future responsibility:

- Generate embeddings for campaign briefs, creator bios, creator categories, portfolio text, and brand documents
- Compare semantic similarity between creators and campaigns
- Store and retrieve vectors through PostgreSQL with pgvector

This module should expose explicit embedding services. It should not own marketplace database models or HTTP concerns.
