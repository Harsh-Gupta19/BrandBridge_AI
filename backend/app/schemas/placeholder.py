from pydantic import BaseModel


class PlaceholderResponse(BaseModel):
    module: str
    status: str
    detail: str
