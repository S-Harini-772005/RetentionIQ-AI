from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_unauthorized_access():
    response = client.get("/api/v1/customers/")
    assert response.status_code == 401

def test_swagger_docs_accessible():
    response = client.get("/api/docs")
    assert response.status_code == 200