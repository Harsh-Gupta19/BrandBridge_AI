from fastapi import APIRouter

from app.api.v1.endpoints._placeholder import planned_module
from app.schemas.placeholder import PlaceholderResponse

router = APIRouter(tags=["proposals"])


@router.get("/proposals", response_model=PlaceholderResponse)
def proposals_placeholder() -> PlaceholderResponse:
    return planned_module("proposals")
