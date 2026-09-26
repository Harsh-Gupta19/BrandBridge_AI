"""Structured ranker: load the active artifact, score, return feature_version.

Planned contents:
- load artifact from ml/artifacts
- score a batch of feature rows
- rule-based fallback before a model is trained

Layer rule (Build Manual §3.1): takes plain data; never queries the database or imports a service.
"""
