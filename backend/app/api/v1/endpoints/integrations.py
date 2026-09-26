"""Social integration routes: OAuth connect, callback, sync, disconnect.

Planned contents:
- GET /integrations/{platform}/connect
- GET /integrations/{platform}/callback
- POST /integrations/{platform}/{account_id}/sync
- DELETE /integrations/{platform}/{account_id}
- GET /integrations/youtube/public-lookup

Layer rule (Build Manual §3.1): declare path, method, schema and dependencies, then call exactly one service function.
"""
