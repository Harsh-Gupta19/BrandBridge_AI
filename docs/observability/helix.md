# Helix Planning

## Have We Added Helix To This Project?

No. Helix has not been added to this repository.

Currently there is:

- No Helix package
- No Helix API key
- No Helix Docker service
- No Helix-specific backend module
- No Helix workflow code

## Important Clarification

The term "Helix" can refer to different tools depending on the team context. Before implementation, the team should confirm exactly which Helix is intended and what problem it should solve.

Possible meanings might include:

- LLM observability or tracing
- Agent workflow monitoring
- A deployment/runtime platform
- A separate project-specific tool

This repository currently treats Helix as a future integration decision, not as part of Phase 1.

## If Helix Is For LLM Or Agent Observability

If the team means an LLM tracing or observability tool, it should be integrated around:

- LLM calls in `backend/app/ai/llm/`
- LangGraph runs in `backend/app/ai/agents/`
- RAG retrieval in `backend/app/ai/rag/`
- Token usage and latency tracking
- Error tracking for failed AI calls

Recommended future structure:

```text
backend/app/core/observability.py
backend/app/ai/llm/tracing.py
backend/app/ai/agents/tracing.py
```

## What Not To Do

- Do not put Helix calls directly inside FastAPI route functions.
- Do not require Helix credentials to start the local app.
- Do not send private user data to external systems without approval.
- Do not add Helix packages until the team confirms the tool and use case.

## Recommended Future Decision

Create an ADR before implementation:

```text
docs/decisions/008-ai-observability.md
```

That ADR should decide:

- Which Helix tool is meant
- What data can be traced
- What must be redacted
- Whether tracing is enabled locally, in demo, or only in production
- What happens when Helix is unavailable
