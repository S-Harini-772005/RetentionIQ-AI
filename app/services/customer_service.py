import logging
from uuid import UUID
from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def get_customer(self, customer_id: UUID) -> Customer:
        """Retrieves a customer by UUID with error handling."""
        query = select(Customer).where(Customer.id == customer_id, Customer.is_deleted == False)
        customer = self.db.execute(query).scalar_one_or_none()
        
        if not customer:
            logger.warning(f"Customer lookup failed for ID: {customer_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer not found"
            )
        return customer

    def get_customers_paginated(
        self, page: int = 1, limit: int = 100
    ) -> Tuple[List[Customer], int]:
        """SQLAlchemy 2.0 implementation for paginated results."""
        offset = (page - 1) * limit
        
        # Count query
        count_query = select(func.count()).select_from(Customer).where(Customer.is_deleted == False)
        total = self.db.execute(count_query).scalar() or 0
        
        # Data query
        data_query = (
            select(Customer)
            .where(Customer.is_deleted == False)
            .order_by(Customer.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        customers = self.db.execute(data_query).scalars().all()
        
        return list(customers), total

    def create_customer(self, customer_in: CustomerCreate) -> Customer:
        """Standardized customer creation."""
        # Check for external_id conflicts
        existing_query = select(Customer).where(Customer.external_id == customer_in.external_id)
        if self.db.execute(existing_query).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this external ID already exists"
            )

        customer = Customer(**customer_in.model_dump())
        self.db.add(customer)
        try:
            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            self.db.rollback()
            logger.error(f"Persistence error during customer creation: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def update_customer(self, customer_id: UUID, customer_in: CustomerUpdate) -> Customer:
        """Updates customer metrics and metadata."""
        customer = self.get_customer(customer_id)
        
        update_data = customer_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)
            
        try:
            self.db.commit()
            self.db.refresh(customer)
            return customer
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating customer {customer_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database update failed")