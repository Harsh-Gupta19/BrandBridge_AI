"""Instagram adapter (refactor of instagramcollector*.py).

Planned contents:
- authorize_url / exchange_code
- fetch_authorized(tokens)
- map to the normalised contract in integrations/base.py

Layer rule (Build Manual §3.1): never writes to the database or leaks a provider-shaped dict.
"""
