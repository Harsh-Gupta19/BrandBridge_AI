"""LLM provider interface with one cloud implementation.

Planned contents:
- LLMProvider protocol
- cloud implementation
- no provider configured -> callers use deterministic fallbacks

Layer rule (Build Manual §3.1): never owns a transaction, decides eligibility or invents a metric.
"""
