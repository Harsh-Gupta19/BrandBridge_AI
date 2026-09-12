# AI, LangChain, LangGraph, RAG, and Agent Workflow

This document explains how AI features should fit into BrandBridge AI.

Current status: structure and planning only. No real LLM, LangGraph, RAG, or agent workflow is running yet.

## Why This Is Separated

AI code can become messy quickly if prompts, API calls, database queries, and HTTP route code are mixed together.

BrandBridge AI keeps these concerns separate:

```text
API route
  -> service
    -> ML module
    -> AI module
    -> repository/database
```

## Where LangChain Fits

LangChain should be used for LLM-facing building blocks when they become useful.

Planned location:

```text
backend/app/ai/llm/
```

Use LangChain for:

- Calling the selected LLM provider
- Structured output parsing
- Prompt/template execution
- Reusable chains that do one clear task

Do not use LangChain for:

- Simple deterministic validation
- Basic database filtering
- Business rules that can be plain Python

Example future flow:

```text
Campaign brief text
  -> LLM parsing chain
  -> structured campaign requirements
  -> validation service
```

## Where LangGraph Fits

LangGraph should orchestrate multi-step workflows.

Planned location:

```text
backend/app/ai/agents/
```

Use LangGraph when a workflow has multiple steps, state, branching, or human approval.

Planned creator matching graph:

```text
START
  -> Parse Campaign
  -> Validate Requirements
  -> Search Creators
  -> Retrieve Social Metrics
  -> Calculate ML Score
  -> Calculate Semantic Score
  -> Rank Candidates
  -> Retrieve Brand Knowledge using RAG
  -> Generate Explanation
  -> Human Approval
  -> Generate Proposal
  -> END
```

Each node should be small and testable.

Good node examples:

- `parse_campaign_node`
- `validate_requirements_node`
- `calculate_ml_score_node`
- `generate_explanation_node`

Avoid one giant node that does everything.

## Where RAG Fits

RAG should be used only for unstructured knowledge.

Planned location:

```text
backend/app/ai/rag/
```

Good RAG use cases:

- Brand guidelines
- Product documentation
- Campaign briefs
- Creator portfolio documents

Bad RAG use cases:

- Fetching a user by ID
- Filtering campaigns by budget
- Checking proposal status

Those are structured database queries and should use SQLAlchemy repositories.

## Where Embeddings Fit

Embeddings create semantic vectors for text.

Planned location:

```text
backend/app/ai/embeddings/
```

Future examples:

- Embed campaign brief text
- Embed creator bio text
- Embed brand guideline chunks
- Compare creator and campaign text semantically
- Store vectors in PostgreSQL using pgvector

## Where Agent Tools Fit

Agent tools are deterministic functions that a graph node can call.

Planned location:

```text
backend/app/ai/tools/
```

Planned tools:

- `search_creators()`
- `get_creator_profile()`
- `get_youtube_statistics()`
- `get_instagram_statistics()`
- `calculate_ml_match()`
- `calculate_semantic_similarity()`
- `retrieve_brand_guidelines()`
- `generate_match_explanation()`
- `generate_collaboration_proposal()`

Beginner note: tools should be boring Python functions. They should not know about FastAPI request objects.

## Where Prompts Fit

Prompt templates should live in:

```text
backend/app/ai/prompts/
```

Prompts should be version-controlled and reviewed. Do not hide important business rules only inside prompts.

## How The Backend Should Call AI

Recommended future flow:

```text
Route:
  POST /api/v1/recommendations

Service:
  recommendation_service.create_recommendations()

Agent:
  creator_matching_graph.invoke()

Tools:
  search_creators()
  calculate_ml_match()
  retrieve_brand_guidelines()

Database:
  repositories and SQLAlchemy sessions
```

The route should not directly call LangChain, LangGraph, or external LLM APIs.

## Human Approval

Human approval is required before important collaboration actions, such as:

- Sending a brand invitation
- Submitting a proposal
- Accepting or rejecting a proposal
- Sending AI-generated text to another user

The AI can draft, rank, and explain. A user should approve important actions.

## Current Files

Current planning files:

- `backend/app/ai/agents/planned_workflow.py`
- `backend/app/ai/tools/planned_tools.py`
- `docs/architecture/langgraph-workflow.md`

These are placeholders. They describe intended structure without implementing the full workflow.
