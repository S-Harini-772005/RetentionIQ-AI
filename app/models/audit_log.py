import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # CREATE, UPDATE, DELETE, LOGIN
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    record_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    old_values: Mapped[dict] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")