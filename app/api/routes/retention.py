from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.retention_service import RetentionService
from app.schemas.retention import RetentionActionOut, RetentionActionCreate
from app.auth.roles import allow_analyst

router = APIRouter(prefix="/retention", tags=["Retention Intelligence"])

@router.get("/recommendations", response_model=List[RetentionActionOut])
def get_retention_recommendations(
    db: Session = Depends(get_db),
    current_user = Depends(allow_analyst)
):
    """Retrieves prescriptive retention actions for high-risk customers."""
    service = RetentionService(db)
    return service.get_pending_actions()

@router.post("/actions", response_model=RetentionActionOut)
def create_retention_action(
    action_in: RetentionActionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(allow_analyst)
):
    """Registers a new retention attempt/action in the workflow."""
    service = RetentionService(db)
    return service.create_action(action_in)