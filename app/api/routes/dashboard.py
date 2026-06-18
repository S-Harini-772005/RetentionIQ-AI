from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.dashboard_service import DashboardService
from app.auth.roles import allow_executive

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(allow_executive)
):
    """Returns high-level business KPIs for executive view."""
    service = DashboardService(db)
    return service.get_executive_summary()

@router.get("/segments")
def get_segment_stats(
    db: Session = Depends(get_db),
    current_user = Depends(allow_executive)
):
    """Returns customer counts distributed by RFM segments."""
    service = DashboardService(db)
    return service.get_segment_performance()