from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.complaint import DashboardMetricsResponse
from app.services.complaint_service import complaint_service

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])

@router.get("/dashboard-metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Returns aggregated metrics, category counts, priority distribution, and district breakdown.
    """
    metrics = complaint_service.get_dashboard_metrics(db=db)
    return DashboardMetricsResponse(**metrics)
