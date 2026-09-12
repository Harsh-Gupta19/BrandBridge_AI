# Data Model Roadmap

Initial model placeholders:

- `User`
- `CreatorProfile`
- `BrandProfile`
- `Campaign`
- `Proposal`

User roles:

- `CREATOR`
- `BRAND`
- `ADMIN`

Planned future entities:

- `SocialAccount`
- `CreatorMetric`
- `RateCard`
- `CampaignRequirement`
- `Recommendation`
- `Collaboration`
- `Message`
- `Document`
- `DocumentChunk`
- `AIExecutionLog`

PostgreSQL remains the source of truth for structured marketplace data. pgvector will support embedding storage for semantic retrieval and matching.
