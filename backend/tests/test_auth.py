import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Petroleum Data Management System API"

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_with_test_credentials():
    """Test login with test credentials"""
    response = client.post(
        "/api/v1/auth/login_nextjs",
        json={"username": "test", "password": "test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["username"] == "test"

def test_login_with_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login_nextjs",
        json={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401

def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/api/v1/karatobe/wells")
    assert response.status_code == 401

def test_protected_endpoint_with_token():
    """Test accessing protected endpoint with valid token"""
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login_nextjs",
        json={"username": "test", "password": "test"}
    )
    token = login_response.json()["access_token"]
    
    # Use token to access protected endpoint
    response = client.get(
        "/api/v1/karatobe/wells",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Note: This might fail if database is not available, but should not be 401
    assert response.status_code != 401