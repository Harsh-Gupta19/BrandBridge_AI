# AGENTS.md

BrandBridge AI is an IIT Bombay capstone project for an AI-powered creator-brand collaboration platform.

Rules for AI coding assistants:

1. Read `README.md` and relevant documentation before modifying code.
2. Do not add unnecessary frameworks.
3. Maintain the modular monolith architecture.
4. Do not introduce microservices without explicit approval.
5. Never commit secrets.
6. Use environment variables.
7. Use Pydantic schemas for FastAPI input/output.
8. Use SQLAlchemy 2 style.
9. Add tests for new backend behavior.
10. Keep notebooks separate from production code.
11. ML experiments belong under notebooks or training modules.
12. Do not directly place experimental notebook logic into production APIs.
13. LangGraph nodes should remain small and testable.
14. Prefer deterministic code over LLM calls where deterministic code is sufficient.
15. RAG should be used only for unstructured knowledge.
16. PostgreSQL should remain the source of truth for structured marketplace data.
17. Human approval is required for important collaboration actions.
18. External social APIs must not become mandatory dependencies for the base application.
19. Preserve backward compatibility where practical.
20. Prefer simple solutions appropriate to a five-person, 2-3 month academic project.
