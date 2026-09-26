"""RAG ingestion: PDF -> pages -> chunks -> embeddings.

Planned contents:
- extract pages
- split into chunks (keeping page numbers)
- embed chunks

Layer rule (Build Manual §3.1): returns plain data; persistence happens in the service.
"""
