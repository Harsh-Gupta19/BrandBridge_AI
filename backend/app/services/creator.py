"""Creator service: profile, preferences, rate card, availability, representation rebuild.

Planned contents:
- create_profile / update_profile
- compute_completeness
- set_preferences / replace_rate_card / set_availability
- rebuild_representation

Layer rule (Build Manual §3.1): orchestrates repositories and owns the transaction; no raw SQL, no fastapi import.
"""
