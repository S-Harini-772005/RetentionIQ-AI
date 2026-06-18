from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.customer_service import CustomerService
from app.schemas.customer import (
    CustomerOut, 
    CustomerPaginationResponse, 
    CustomerCreate, 
    CustomerUpdate
)
from app.auth.roles import allow_analyst

router = APIRouter(prefix="/customers", tags=["Customer Management"])

@router.get("/", response_model=CustomerPaginationResponse)
def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user = Depends(allow_analyst)
):
    """Retrieves a paginated list of customers."""
    service = CustomerService(db)
    items, total = service.get_customers_paginated(page=page, limit=limit)
    
    return {
        "items": items,
        "meta": {
            "total_records": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }

@router.get("/{id}", response_model=CustomerOut)
def get_customer(
    id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_analyst)
):
    """Retrieves detailed profile for a specific customer."""
    service = CustomerService(db)
    return service.get_customer(id)

@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(allow_analyst)
):
    """Creates a new customer record."""
    service = CustomerService(db)
    return service.create_customer(customer_in)

@router.patch("/{id}", response_model=CustomerOut)
def update_customer(
    id: UUID,
    customer_in: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(allow_analyst)
):
    """Updates an existing customer record."""
    service = CustomerService(db)
    return service.update_customer(id, customer_in)