from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.ml.churn.predict import ChurnPredictor
from app.schemas.churn import PredictRequest, PredictResponse

from app.database.session import get_db
from app.services.churn_service import ChurnService
from app.schemas.churn import ChurnPredictionOut, ChurnSummary
from app.auth.roles import allow_analyst, allow_executive

router = APIRouter(prefix="/churn", tags=["Churn Analytics"])

@router.get("/high-risk", response_model=List[ChurnPredictionOut])
def get_high_risk_predictions(
    threshold: float = 0.7,
    db: Session = Depends(get_db),
    current_user = Depends(allow_analyst)
):
    """Lists customers identified as high churn risk."""
    service = ChurnService(db)
    return service.get_high_risk_customers(threshold=threshold)

@router.get("/revenue-at-risk", response_model=dict)
def get_total_revenue_at_risk(
    db: Session = Depends(get_db),
    current_user = Depends(allow_executive)
):
    """Calculates cumulative monetary value at risk from high-risk segments."""
    service = ChurnService(db)
    at_risk = service.get_revenue_at_risk()
    return {"total_revenue_at_risk": at_risk}
predictor = ChurnPredictor()
@router.post(
    "/predict",
    response_model=PredictResponse
)
def predict(request: PredictRequest):

    data = {
        "Revenue": request.Revenue,
        "Orders": request.Orders,
        "Recency": request.Recency,
        "Frequency": request.Frequency,
        "Monetary": request.Monetary,

        # IMPORTANT: space, not underscore
        "Customer Segment": request.Customer_Segment
    }

    return predictor.predict_single(data)
