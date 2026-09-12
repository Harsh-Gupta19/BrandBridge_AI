from fastapi import APIRouter

from app.api.v1.endpoints._placeholder import planned_module
from app.schemas.placeholder import PlaceholderResponse

router = APIRouter(tags=["brands"])


@router.get("/brands", response_model=PlaceholderResponse)
def brands_placeholder() -> PlaceholderResponse:
    return planned_module("brands")
