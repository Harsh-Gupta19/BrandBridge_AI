"""Schema-constrained extraction with one repair retry.

Planned contents:
- extract(schema, text) -> validated object or parse_failed

Layer rule (Build Manual §3.1): never owns a transaction, decides eligibility or invents a metric.
"""
