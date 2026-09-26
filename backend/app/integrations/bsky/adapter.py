"""Bluesky adapter (refactor of bskydatacollector.py).

Planned contents:
- fetch_public(handle)
- map to the normalised contract in integrations/base.py

Layer rule (Build Manual §3.1): never writes to the database or leaks a provider-shaped dict.
"""
