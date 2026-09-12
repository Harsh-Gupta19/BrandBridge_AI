# 005 - Hybrid Recommendation

## Status

Accepted

## Context

Creator-campaign fit depends on structured signals such as platform, budget, geography, categories, and engagement, plus semantic signals from briefs and profile text.

## Decision

Plan a hybrid recommendation approach combining structured ML scores with semantic similarity.

## Alternatives Considered

- Pure rule-based matching
- Pure embedding similarity
- LLM-only ranking

## Consequences

Hybrid ranking should be more explainable and controllable than LLM-only ranking. The team must avoid hardcoded final weights until experiments justify them.
