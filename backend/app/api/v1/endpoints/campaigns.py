from fastapi import APIRouter

from app.api.v1.endpoints._placeholder import planned_module
from app.schemas.placeholder import PlaceholderResponse

router = APIRouter(tags=["campaigns"])


@router.get("/campaigns", response_model=PlaceholderResponse)
def campaigns_placeholder() -> PlaceholderResponse:
    return planned_module("campaigns")
