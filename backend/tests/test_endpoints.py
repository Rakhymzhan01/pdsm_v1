import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    """Get authentication token for testing"""
    response = client.post(
        "/api/v1/auth/login_nextjs",
        json={"username": "test", "password": "test"}
    )
    return response.json()["access_token"]

def test_wells_endpoint(auth_token):
    """Test wells endpoint"""
    response = client.get(
        "/api/v1/karatobe/wells",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    # Should not be unauthorized
    assert response.status_code != 401

def test_production_endpoint(auth_token):
    """Test production endpoint"""
    response = client.get(
        "/api/v1/karatobe/production",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    # Should not be unauthorized
    assert response.status_code != 401

def test_pvt_endpoint(auth_token):
    """Test PVT endpoint"""
    response = client.get(
        "/api/v1/karatobe/pvt",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    # Should not be unauthorized
    assert response.status_code != 401

def test_invalid_endpoint():
    """Test invalid endpoint returns 404"""
    response = client.get("/api/v1/invalid/endpoint")
    assert response.status_code == 404