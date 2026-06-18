import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base

class ModelMetric(Base):
    """
    SQLAlchemy 2.0 Model for tracking Machine Learning model performance history.
    Stores standard classification metrics and training metadata.
    """
    __tablename__ = "model_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    
    model_name: Mapped[str] = mapped_column(
        String(255), 
        index=True, 
        nullable=False,
    )

    # Classification Metrics (Stored as Numeric for precision, mapped to float)
    accuracy: Mapped[float] = mapped_column(
        Numeric(7, 6), 
        nullable=False,
    )
    
    precision: Mapped[float] = mapped_column(
        Numeric(7, 6), 
        nullable=False,
    )
    
    recall: Mapped[float] = mapped_column(
        Numeric(7, 6), 
        nullable=False,
    )
    
    f1_score: Mapped[float] = mapped_column(
        Numeric(7, 6), 
        nullable=False,
    )
    
    roc_auc: Mapped[float] = mapped_column(
        Numeric(7, 6), 
        nullable=False,
    )

    # Metadata
    training_time_seconds: Mapped[float] = mapped_column(
        Numeric(12, 3), 
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        index=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<ModelMetric(model='{self.model_name}', "
            f"f1={self.f1_score:.4f}, "
            f"roc_auc={self.roc_auc:.4f}, "
            f"created_at='{self.created_at}')>"
        ) 