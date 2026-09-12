# MCP Planning

MCP means Model Context Protocol.

## Have We Added MCP To This Project?

No. MCP has not been added as an implementation in this repository.

Currently there is:

- No MCP server
- No MCP client
- No MCP dependency in `backend/requirements.txt`
- No `backend/app/mcp/` folder
- No MCP Docker service

## Why MCP Is Not Added Yet

Phase 1 is focused on the core monorepo foundation:

- FastAPI backend
- React frontend
- PostgreSQL with pgvector
- AI, ML, RAG, and agent module boundaries
- Docker and CI setup

MCP should be added only if the team has a clear use case.

## Possible Future MCP Use Cases

MCP could be useful later for controlled tool access, such as:

- Exposing creator search as a tool to an AI assistant
- Exposing campaign lookup as a tool
- Connecting development tools to project documentation
- Allowing approved local tools to inspect sample data or docs

## Where MCP Would Go If Added

Recommended future structure:

```text
backend/app/mcp/
|-- __init__.py
|-- server.py
|-- tools/
|   |-- creators.py
|   |-- campaigns.py
|   |-- recommendations.py
|-- schemas.py
|-- README.md
```

If MCP is added, keep it separate from FastAPI routes. MCP tools can call the same service layer used by REST APIs.

Recommended flow:

```text
MCP tool -> service -> repository -> database
REST API -> service -> repository -> database
```

This avoids duplicating business logic.

## Decision Needed Before Implementation

Before adding MCP, create an ADR answering:

- What exact problem does MCP solve for the project?
- Who will use the MCP server?
- Which tools will be exposed?
- What data is safe to expose?
- How will authentication and permissions work?
- Is this required for the capstone demo?
