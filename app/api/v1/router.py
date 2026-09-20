from fastapi import APIRouter
from app.api.v1.complaints import router as complaints_router
from app.api.v1.departments import router as departments_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(complaints_router)
api_router.include_router(departments_router)
api_router.include_router(webhooks_router)
api_router.include_router(analytics_router)
