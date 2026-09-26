"""Shared FastAPI dependencies used by every router.

Planned contents:
- get_db: yield a SQLAlchemy Session
- get_current_user: decode the JWT and load the user
- require_role(role): check X-Active-Role against user_roles
- active_profile: resolve and assert ownership of the brand/creator profile

Layer rule (Build Manual §3.1): may decode tokens, load the user and assert ownership; must not contain domain logic.
"""
