from fastapi import APIRouter

from app.api.v1.endpoints._placeholder import planned_module
from app.schemas.placeholder import PlaceholderResponse

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=PlaceholderResponse)
def recommendations_placeholder() -> PlaceholderResponse:
    return planned_module("recommendations")
