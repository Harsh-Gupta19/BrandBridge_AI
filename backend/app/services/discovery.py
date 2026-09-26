"""The reciprocal discovery pipeline, both directions.

Planned contents:
- generate_for_campaign (brand -> creator)
- refresh_for_creator (creator -> brand)
- Stages: eligibility, retrieval, features, scoring, re-rank, persist
- Match detail and explanation

Layer rule (Build Manual §3.1): the only service that touches ML, AI and repositories at once.
"""
