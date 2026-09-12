from fastapi import APIRouter

from app.api.v1.endpoints._placeholder import planned_module
from app.schemas.placeholder import PlaceholderResponse

router = APIRouter(tags=["auth"])


@router.get("/auth", response_model=PlaceholderResponse)
def auth_placeholder() -> PlaceholderResponse:
    return planned_module("auth")
