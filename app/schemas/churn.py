from uuid import UUID
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.customer import Customer

class ChurnPredictionBase(BaseModel):
    customer_id: UUID
    churn_probability: float = Field(..., ge=0, le=1)
    risk_level: str = Field(..., pattern="^(Low|Medium|High|Critical)$")
    top_drivers: Optional[Dict[str, float]] = None
    model_version: str

class ChurnPredictionCreate(ChurnPredictionBase):
    pass

class ChurnPredictionOut(ChurnPredictionBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChurnBatchRequest(BaseModel):
    customer_ids: List[UUID]

class ChurnSummary(BaseModel):
    high_risk_count: int
    critical_risk_count: int
    average_probability: float
    revenue_at_risk: float

class PredictRequest(BaseModel):
    Revenue: float
    Orders: int
    Recency: int
    Frequency: int
    Monetary: float
    Customer_Segment: str


class PredictResponse(BaseModel):
    churn_probability: float
    is_predicted_churn: bool
    risk_level: str
    revenue_at_risk: float
    
    recommended_action: str
    offer: str
    priority_level: str
    expected_revenue_saved: float
    retention_cost: float
    roi: float