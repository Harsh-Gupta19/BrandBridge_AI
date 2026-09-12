from fastapi import APIRouter

from app.api.v1.endpoints._placeholder import planned_module
from app.schemas.placeholder import PlaceholderResponse

router = APIRouter(tags=["creators"])


@router.get("/creators", response_model=PlaceholderResponse)
def creators_placeholder() -> PlaceholderResponse:
    return planned_module("creators")
