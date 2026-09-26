# Database migrations — Build Manual §5.2

The backend implements the manual's complete migration sequence. Migration
`0001_initial_foundation` is unchanged. The new revisions form one linear chain,
and the SQLAlchemy 2 models describe its final schema. This is database foundation
work; the routes, services, ranking pipeline and social integrations remain separate
implementation tasks.

| Revision | Schema changes |
| --- | --- |
| `0002_dual_role_identity` | Role membership, existing-role backfill, account status; remove `users.role` |
| `0003_creator_commercial` | Creator fields, preferences, historical rate cards, availability |
| `0004_social_evidence` | Social accounts, dated metric snapshots, content, sync logs |
| `0005_campaign_requirements` | Raw briefs and lifecycle, confirmed requirements, discovery policy, competitor registry/policies, products |
| `0006_representations_vectors` | Versioned creator representations, content clusters, 384-dimensional vectors and cosine HNSW indexes |
| `0007_matching_and_labels` | Reciprocal scores, evidence, exclusions, model versions, pair labels, experiments |
| `0008_collaboration_knowledge` | Two-way proposals and versions, collaborations, agreements, messages, outcomes, documents/chunks, AI logs |
| `0009_wall` | Community posts, comments, reactions, follows |

The enumerated tables total **38**, including the five foundation tables. The manual's
“37 tables” headline does not match its complete list. Both `brand_products` and
`integration_sync_logs` are named in §5.2 but have no detailed DDL later in Part 5;
their minimal schemas follow the documented ownership and audit requirements:

- Products: brand owner, name, description, category and timestamps.
- Sync logs: optional account reference, platform, request class, outcome, error
  category/detail, latency, correlation ID and timestamp. Token values do not belong here.

## Apply

Use PostgreSQL 16 with the `vector` extension available (the existing Compose image
already provides it). From `backend/`, in the project's Python environment:

```bash
pip install -r requirements-dev.txt
alembic upgrade head
alembic current
```

`DATABASE_URL` is read from the environment or the project/backend `.env` files.
Migration configuration reads only database settings, so unrelated API/provider
settings cannot prevent a schema upgrade. No migration imports live ORM models;
future model edits cannot change historical migration behavior.

To inspect SQL without connecting:

```bash
alembic upgrade head --sql
alembic downgrade 0009_wall:base --sql
```

## Existing data and compatibility

- Every existing user receives their original role in `user_roles`, retaining the
  original creation time as `activated_at`. Inactive users become `status=INACTIVE`.
  `is_active` is retained for compatibility. Future identity-service writes must keep
  the legacy flag consistent with account status until that flag is retired.
- `User.roles` replaces the former `User.role` ORM attribute. Both existing profile
  relationships remain one-to-one through their unique user references.
- Creator categories and audience summaries convert from JSON to JSONB without
  discarding values. Categories receive a GIN index.
- Campaign `brief` and `budget_amount` are retained; their values initialize
  `raw_brief` and `budget_max`. Existing campaigns remain drafts. Migration does not
  claim that a human confirmed their requirements or publish them.
- Legacy proposals default to creator initiation, consistent with their existing
  creator-profile reference. A version-1 record preserves their offer, message,
  creator author and creation time. No collaboration or approval is synthesized.
- The proposal status column is widened for `REVIEWING`, `COUNTER_OFFER` and
  `WITHDRAWN`.
- `DocumentChunk.chunk_metadata` maps to the database column `metadata`, since
  `metadata` is reserved by SQLAlchemy's declarative base.

## Downgrade behavior

Downgrades remove the tables/columns introduced by each revision, in dependency
order. As usual, data in removed features is lost; retain a database backup when
rolling back an environment containing useful data. The shared vector extension is
kept when downgrading to base, matching `0001`.

Two explicit guards prevent silently changing account/commercial meaning:

- `0002 → 0001` refuses if any user has zero or multiple roles. Select the intended
  legacy role deliberately before attempting that downgrade.
- `0008 → 0007` refuses while proposals use a status unavailable in the old schema.
  For representable statuses, the current proposal version's amount and message
  are copied back into the legacy fields before version history is removed.

A PostgreSQL transactional migration failure rolls back the attempted changes.

## Validate

The integration tests require an explicitly supplied `TEST_DATABASE_URL`; they do
not default to the application's database. Use a disposable PostgreSQL/pgvector
instance. The test role needs extension and schema creation permission. Tests create
unique schemas and roll back their contents; pgvector is installed in `public` if
needed.

```bash
TEST_DATABASE_URL=postgresql+psycopg://brandbridge_test:brandbridge_test@localhost:5432/brandbridge_test \
  pytest tests/integration/test_migrations.py tests/unit/test_migration_contract.py
```

The suite checks fresh upgrades, full downgrade/re-upgrade, seeded foundation-data
preservation, ORM/schema drift (including defaults), dual-role persistence and
rollback guards, historical-rate uniqueness, vector dimensions/indexes, score
uniqueness in both directions, proposal evidence references, generated mutual labels,
proposal-version and collaboration uniqueness, and Wall cascade behavior.

GitHub Actions supplies a PostgreSQL 16/pgvector service and runs these tests as part
of the backend suite. Without `TEST_DATABASE_URL`, PostgreSQL tests are explicitly
skipped and the offline migration test still runs.

## Boundaries still owned by services

The schema stores history, audit evidence and approvals. It does not implement
append-only application policies, owner authorization, proposal state transitions,
role validation, document visibility, or automatic Wall counters. Those belong in
the later service/repository implementations. Polymorphic document owners and Wall
profile references require explicit ownership checks there.

Other manual flows mention fields beyond the §5.2 DDL, including campaign query
embeddings, a “not interested” log and Wall-to-proposal context. Those should be
specified in later migrations alongside the corresponding feature, rather than
silently added to this sequence.

## Complete Part 5 contracts

`app/models/enums.py` defines all ten enumerations from §5.3. The mapped scalar
fields use those enums while retaining the manual's VARCHAR storage and column
lengths. `User.has_role()` provides the membership predicate shown in §5.4.
`app/integrations/base.py` implements §5.7's `NormalisedMetrics`,
`NormalisedAccount` and `SocialAdapter`, with supporting content and OAuth token
models. Missing metrics remain `None`; engagement rates are fractions, timestamps
are timezone-aware, and provider-specific field names are rejected outside the
explicit extension dictionaries. OAuth secrets are redacted in representations.
Adapter implementations and persistence services are separate work.

## Local database created on 26 September 2026

All revisions have been applied to `brandbridge` at `localhost:5432`, using the
credentials already configured in `.env`. It contains 38 application tables plus
`alembic_version`, at revision `0009_wall`. The vector extension and all three HNSW
indexes are installed. `alembic check` reports no pending schema changes.

Because Docker was unavailable, this workspace has a project-local PostgreSQL 16
runtime in `.local/postgres-runtime` and persistent database files in
`.local/postgres-data`. Both are excluded from Git. The server is running; it does
not automatically restart after a reboot. From the repository root:

```bash
# Check whether the local server is running
./.local/postgres-runtime/bin/pg_ctl -D .local/postgres-data status

# Start it again after a reboot or explicit stop
mkdir -p -m 700 /tmp/brandbridge-local-pgsocket
./.local/postgres-runtime/bin/pg_ctl -D .local/postgres-data -l .local/postgres.log start

# Stop it, for example before starting Compose's PostgreSQL on the same port
./.local/postgres-runtime/bin/pg_ctl -D .local/postgres-data stop -m fast
```

This local instance and Compose's `postgres_data` volume are separate databases.
The connection settings did not change. Future schema changes should be new Alembic
revisions; the applied `0001`–`0009` chain must now remain immutable.

Validation: 25 migration/contract/unit tests passed against a separate test
database, which was removed afterwards. Project database contents were not used as
test fixtures.
