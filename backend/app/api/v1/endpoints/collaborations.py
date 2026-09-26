"""Collaboration routes: list, detail, status, messages, agreement.

Planned contents:
- GET /collaborations (kanban grouped by status)
- GET/PATCH /collaborations/{id}
- POST /collaborations/{id}/messages
- POST /collaborations/{id}/agreement/draft and /approve

Layer rule (Build Manual §3.1): declare path, method, schema and dependencies, then call exactly one service function.
"""
