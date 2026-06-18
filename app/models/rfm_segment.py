import uuid
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base

class RFMSegment(Base):
    __tablename__ = "rfm_segments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    
    recency_score: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency_score: Mapped[int] = mapped_column(Integer, nullable=False)
    monetary_score: Mapped[int] = mapped_column(Integer, nullable=False)
    
    segment_name: Mapped[str] = mapped_column(String(100), index=True) # Champions, Hibernating, etc.
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    # Relationships
    customer = relationship("Customer", back_populates="rfm_segments")