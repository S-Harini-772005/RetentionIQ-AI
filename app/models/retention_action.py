import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base

class RetentionAction(Base):
    __tablename__ = "retention_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("churn_predictions.id"), nullable=True
    )
    
    action_type: Mapped[str] = mapped_column(String(100), nullable=False) # Discount, Call, Email
    status: Mapped[str] = mapped_column(String(50), server_default="Pending", index=True) # Pending, Executed, Failed, Converted
    offer_details: Mapped[str] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    customer = relationship("Customer", back_populates="retention_actions")
    prediction = relationship("ChurnPrediction", back_populates="retention_actions")