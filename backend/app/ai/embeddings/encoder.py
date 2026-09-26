"""Text encoder: sentence-transformers, cached singleton.

Planned contents:
- get_encoder()
- encode(texts) -> 384-dim normalised vectors

Layer rule (Build Manual §3.1): never owns a transaction.
"""
