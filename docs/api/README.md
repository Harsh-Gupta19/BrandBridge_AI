# API

Current Phase: Phase 1 - Engineering Foundation

Implemented endpoints:

- `GET /health`
- `GET /api/v1/health`

Reserved placeholder modules:

- `/api/v1/auth`
- `/api/v1/creators`
- `/api/v1/brands`
- `/api/v1/campaigns`
- `/api/v1/proposals`
- `/api/v1/recommendations`

Future API development should follow:

```text
Routes -> Services -> Repositories/DB
```

Business logic should not live directly in route functions.
