import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, Numeric, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    clv_score: Mapped[float] = mapped_column(Numeric(15, 2), server_default="0.00")
    total_spent: Mapped[float] = mapped_column(Numeric(15, 2), server_default="0.00")
    is_deleted: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    churn_predictions = relationship("ChurnPrediction", back_populates="customer", cascade="all, delete-orphan")
    rfm_segments = relationship("RFMSegment", back_populates="customer", cascade="all, delete-orphan")
    retention_actions = relationship("RetentionAction", back_populates="customer", cascade="all, delete-orphan")