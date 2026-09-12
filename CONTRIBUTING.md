# Contributing

## Branch Strategy

The protected integration branch is:

- `main`

Create feature branches such as:

- `feature/creator-profile`
- `feature/campaign-management`
- `feature/ml-matching`
- `feature/rag`
- `feature/langgraph-agent`
- `feature/youtube-integration`

Create fix branches as:

- `fix/<issue>`

Do not commit directly to `main`.

## Workflow

```text
Issue
-> Branch
-> Implementation
-> Tests
-> Pull Request
-> Review
-> Merge
```

## Pull Requests

- Keep pull requests focused.
- Add or update tests for changed behavior.
- Update documentation when architecture, APIs, environment variables, or workflows change.
- Request at least one teammate review where practical.
- Confirm that no secrets are committed.

## Code Quality

- Prefer simple, explicit code.
- Keep business logic outside API route functions.
- Use Pydantic schemas for API input and output.
- Use SQLAlchemy 2 style for database models and queries.
- Keep notebooks and experiments separate from production APIs.
