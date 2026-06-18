from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class RetentionActionBase(BaseModel):
    customer_id: UUID
    prediction_id: Optional[UUID] = None
    action_type: str = Field(..., min_length=1, max_length=100)
    offer_details: Optional[str] = Field(None, max_length=500)

class RetentionActionCreate(RetentionActionBase):
    pass

class RetentionActionUpdate(BaseModel):
    status: str = Field(..., pattern="^(Pending|Executed|Failed|Converted)$")

class RetentionActionOut(RetentionActionBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RetentionActionListResponse(BaseModel):
    items: List[RetentionActionOut]
    total: int