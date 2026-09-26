"""LangGraph campaign-match workflow with a human-approval interrupt.

Planned contents:
- CampaignMatchState
- nodes: parse -> validate -> search -> score -> explain -> HUMAN_APPROVAL -> draft

Layer rule (Build Manual §3.1): wraps existing tools only; never takes a commercial action.
"""
