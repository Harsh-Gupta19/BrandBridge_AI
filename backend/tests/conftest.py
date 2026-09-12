from collections.abc import Generator

from fastapi.testclient import TestClient

from app.main import app


def pytest_configure() -> None:
    app.dependency_overrides.clear()


def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
