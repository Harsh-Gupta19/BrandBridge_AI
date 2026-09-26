"""Campaign service: CRUD, parse-brief, confirm requirements, publish.

Planned contents:
- create / update / list / get
- parse_brief (LLM draft, never writes requirements)
- confirm_requirements
- publish

Layer rule (Build Manual §3.1): orchestrates repositories and owns the transaction; no raw SQL, no fastapi import.
"""
