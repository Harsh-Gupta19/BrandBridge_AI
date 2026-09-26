"""Identity service: register, login, refresh, me, role activation.

Planned contents:
- register
- login
- refresh
- get_me
- activate_role

Layer rule (Build Manual §3.1): orchestrates repositories and owns the transaction; no raw SQL, no fastapi import.
"""
