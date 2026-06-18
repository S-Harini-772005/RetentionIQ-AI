import uuid
from datetime import datetime
from sqlalchemy import DateTime, Numeric, String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.base import Base

class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    churn_probability: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), index=True) # Low, Medium, High, Critical
    
    # SHAP Explanations
    top_drivers: Mapped[dict] = mapped_column(JSONB, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), index=True)

    # Relationships
    customer = relationship("Customer", back_populates="churn_predictions")
    retention_actions = relationship("RetentionAction", back_populates="prediction")