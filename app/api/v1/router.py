"""
API v1 Router
Combines all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1.endpoints import upload, documents

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(upload.router, tags=["Upload"])
api_router.include_router(documents.router, tags=["Documents"])
