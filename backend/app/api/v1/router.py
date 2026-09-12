from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    brands,
    campaigns,
    creators,
    health,
    proposals,
    recommendations,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(creators.router)
api_router.include_router(brands.router)
api_router.include_router(campaigns.router)
api_router.include_router(proposals.router)
api_router.include_router(recommendations.router)
