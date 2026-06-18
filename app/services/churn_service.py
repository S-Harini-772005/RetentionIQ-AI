import logging
from uuid import UUID
from typing import List
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.models.churn_prediction import ChurnPrediction
from app.models.customer import Customer
from app.schemas.churn import ChurnPredictionCreate

logger = logging.getLogger(__name__)

class ChurnService:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_prediction(self, customer_id: UUID) -> Optional[ChurnPrediction]:
        """Retrieves the most recent churn score for a customer."""
        return self.db.execute(
            select(ChurnPrediction)
            .where(ChurnPrediction.customer_id == customer_id)
            .order_by(desc(ChurnPrediction.created_at))
            .limit(1)
        ).scalar_one_or_none()

    def get_high_risk_customers(self, threshold: float = 0.7, limit: int = 50) -> List[ChurnPrediction]:
        """Identifies customers with churn probability above a specific threshold."""
        query = (
            select(ChurnPrediction)
            .where(ChurnPrediction.churn_probability >= threshold)
            .order_by(desc(ChurnPrediction.churn_probability))
            .limit(limit)
        )
        return list(self.db.execute(query).scalars().all())

    def record_prediction(self, prediction_in: ChurnPredictionCreate) -> ChurnPrediction:
        """Logs a new machine learning model prediction result."""
        prediction = ChurnPrediction(**prediction_in.model_dump())
        self.db.add(prediction)
        try:
            self.db.commit()
            self.db.refresh(prediction)
            return prediction
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to record prediction: {str(e)}")
            raise HTTPException(status_code=500, detail="Persistence error")

    def get_revenue_at_risk(self) -> float:
        """Calculates total revenue associated with high-risk customers."""
        high_risk_subquery = (
            select(ChurnPrediction.customer_id)
            .where(ChurnPrediction.risk_level.in_(["High", "Critical"]))
            .distinct()
        ).subquery()
        
        total_risk = self.db.execute(
            select(func.sum(Customer.total_spent))
            .where(Customer.id.in_(select(high_risk_subquery)))
        ).scalar()
        
        return float(total_risk or 0.0)