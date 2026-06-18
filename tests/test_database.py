import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.models.customer import Customer

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_customer(db_session):
    customer = Customer(
        external_id="EXT-001",
        email="cust@test.com",
        first_name="John",
        last_name="Doe",
        clv_score=1500.50
    )
    db_session.add(customer)
    db_session.commit()
    
    retrieved = db_session.query(Customer).filter_by(external_id="EXT-001").first()
    assert retrieved is not None
    assert retrieved.clv_score == 1500.50