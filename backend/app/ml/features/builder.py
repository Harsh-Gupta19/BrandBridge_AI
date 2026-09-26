"""The single feature contract shared by training and inference.

Planned contents:
- FEATURE_VERSION
- build_pair_features(campaign, creator) -> dict[str, float]

Layer rule (Build Manual §3.1): takes plain data; never queries the database or imports a service.
"""
