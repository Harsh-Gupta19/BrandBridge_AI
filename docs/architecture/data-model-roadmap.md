# Data Model Roadmap

The database schema now implements Build Manual §5.2 through `0009_wall`, with
SQLAlchemy 2 models for all 38 named tables. See
[database migrations](database-migrations.md) for the complete revision map,
compatibility decisions and validation commands. Services and APIs using these
tables remain future work.

The five original models are retained and extended:

- `User`
- `CreatorProfile`
- `BrandProfile`
- `Campaign`
- `Proposal`

User roles:

- `CREATOR`
- `BRAND`
- `ADMIN`

Additional implemented entity groups:

- Dual-role membership (`UserRoleRow`)
- Creator preferences, rate-card history and availability
- Social accounts, metric snapshots, content and sync logs
- Campaign requirements, discovery/competitor policies and brand products
- Creator representations and content clusters
- Match scores/evidence, exclusions, model versions, pair labels and experiment runs
- Proposal versions, collaborations, agreements, messages and outcomes
- Documents, document chunks and AI execution logs
- Wall posts, comments, reactions and follows

PostgreSQL remains the source of truth for structured marketplace data. pgvector
columns and HNSW indexes are present for creator representations, content clusters
and document chunks; embedding generation and retrieval services are not yet implemented.
