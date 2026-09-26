"""DomainError hierarchy and its HTTP mapping.

Planned contents:
- DomainError base plus ValidationError, AuthError, ForbiddenError, NotFoundError, ConflictError
- One mapping from each error type to an HTTP status
- Common error body: {code, message, details, correlation_id}

Layer rule (Build Manual §3.1): services raise these errors; only this module knows about HTTP status codes.
"""
