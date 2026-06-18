from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.database.session import get_db
from app.models.model_metrics import ModelMetric
from app.auth.roles import allow_admin

router = APIRouter(prefix="/metrics", tags=["Model Observability"])

@router.get("/model/performance")
def get_model_metrics(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin)
):
    """Retrieves history of model training performance metrics."""
    query = select(ModelMetric).order_by(desc(ModelMetric.created_at)).limit(limit)
    metrics = db.execute(query).scalars().all()
    return metrics

@router.post("/predict")
def trigger_batch_prediction(
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin)
):
    """Simulates triggering a new ML batch prediction run (background job)."""
    # Logic to trigger celery worker or similar would go here
    return {"status": "Batch prediction task queued", "model_version": "v1.2.0"}