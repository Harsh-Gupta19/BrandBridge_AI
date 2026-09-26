"""Document routes: upload, list, knowledge query.

Planned contents:
- POST /brands/{id}/documents and /campaigns/{id}/documents (multipart upload)
- GET /documents/{id}
- POST /campaigns/{id}/knowledge/query

Layer rule (Build Manual §3.1): declare path, method, schema and dependencies, then call exactly one service function.
"""
