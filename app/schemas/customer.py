from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class CustomerBase(BaseModel):
    """Base schema with shared customer attributes."""
    external_id: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""
    pass

class CustomerUpdate(BaseModel):
    """Schema for updating an existing customer."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    clv_score: Optional[Decimal] = Field(None, ge=0)
    total_spent: Optional[Decimal] = Field(None, ge=0)

class CustomerOut(CustomerBase):
    """Standardized output schema for customer entities."""
    id: UUID
    clv_score: Decimal
    total_spent: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginationMeta(BaseModel):
    """Metadata for paginated API responses."""
    total_records: int
    page: int
    limit: int
    total_pages: int

class CustomerPaginationResponse(BaseModel):
    """Standardized wrapper for paginated customer lists."""
    items: List[CustomerOut]
    meta: PaginationMeta

    model_config = ConfigDict(from_attributes=True)