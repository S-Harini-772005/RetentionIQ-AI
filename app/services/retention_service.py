import logging
from uuid import UUID
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.retention_action import RetentionAction
from app.schemas.retention import RetentionActionCreate, RetentionActionUpdate

logger = logging.getLogger(__name__)

class RetentionService:
    def __init__(self, db: Session):
        self.db = db

    def create_action(self, action_in: RetentionActionCreate) -> RetentionAction:
        """Initializes a retention workflow for a customer."""
        action = RetentionAction(**action_in.model_dump())
        self.db.add(action)
        try:
            self.db.commit()
            self.db.refresh(action)
            return action
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating retention action: {str(e)}")
            raise HTTPException(status_code=500, detail="Action creation failed")

    def update_action_status(self, action_id: UUID, status_in: RetentionActionUpdate) -> RetentionAction:
        """Updates the status of a retention attempt (e.g., Converted)."""
        action = self.db.execute(
            select(RetentionAction).where(RetentionAction.id == action_id)
        ).scalar_one_or_none()
        
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
            
        action.status = status_in.status
        self.db.commit()
        self.db.refresh(action)
        return action

    def get_pending_actions(self) -> List[RetentionAction]:
        """Retrieves all retention tasks awaiting execution."""
        return list(self.db.execute(
            select(RetentionAction).where(RetentionAction.status == "Pending")
        ).scalars().all())