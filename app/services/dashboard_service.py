from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.customer import Customer
from app.models.churn_prediction import ChurnPrediction
from app.models.rfm_segment import RFMSegment

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_executive_summary(self) -> Dict[str, Any]:
        """Aggregates top-level KPIs for the executive dashboard."""
        total_customers = self.db.execute(select(func.count(Customer.id))).scalar() or 0
        
        risk_counts = self.db.execute(
            select(ChurnPrediction.risk_level, func.count(ChurnPrediction.id))
            .group_by(ChurnPrediction.risk_level)
        ).all()
        
        risk_map = {level: count for level, count in risk_counts}
        
        avg_churn = self.db.execute(
            select(func.avg(ChurnPrediction.churn_probability))
        ).scalar() or 0.0
        
        # Calculate revenue at risk (High + Critical)
        revenue_at_risk = self.db.execute(
            select(func.sum(Customer.total_spent))
            .join(ChurnPrediction, Customer.id == ChurnPrediction.customer_id)
            .where(ChurnPrediction.risk_level.in_(["High", "Critical"]))
        ).scalar() or 0.0

        return {
            "total_customers": total_customers,
            "high_risk_customers": risk_map.get("High", 0) + risk_map.get("Critical", 0),
            "average_churn_probability": round(float(avg_churn), 4),
            "total_revenue_at_risk": round(float(revenue_at_risk), 2),
            "risk_distribution": risk_map
        }

    def get_segment_performance(self) -> Dict[str, int]:
        """Calculates customer counts per RFM segment."""
        segments = self.db.execute(
            select(RFMSegment.segment_name, func.count(RFMSegment.id))
            .group_by(RFMSegment.segment_name)
        ).all()
        
        return {name: count for name, count in segments}