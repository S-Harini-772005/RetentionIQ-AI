import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.session import get_db, Base

# Setup Test Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_user_registration():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@enterprise.com",
            "password": "securepassword123",
            "full_name": "Test User",
            "role": "Analyst"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@enterprise.com"

def test_login_success():
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "password123", "full_name": "User", "role": "Admin"}
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401