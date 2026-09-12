from app.schemas.placeholder import PlaceholderResponse


def planned_module(module: str) -> PlaceholderResponse:
    return PlaceholderResponse(
        module=module,
        status="planned",
        detail="This API module is reserved for a future implementation phase.",
    )
