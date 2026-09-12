# Infrastructure Guide

This folder contains infrastructure notes.

Current status:

- Docker Compose is the local development target.
- Kubernetes is intentionally not included.
- Redis is intentionally not included.
- Production deployment is not implemented yet.

## `docker/`

Use this folder for Docker-specific notes and helper files.

The main Compose file currently lives at the repository root:

```text
docker-compose.yml
```

It defines:

- `frontend`
- `backend`
- `postgres`

## `deployment/`

Use this folder for future deployment documentation.

Do not add production deployment scripts until the team has agreed on a target platform.
