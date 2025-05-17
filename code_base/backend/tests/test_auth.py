import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_password_hash

client = TestClient(app)

def test_signup():
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "test@example.com"

def test_login():
    # First create a user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test2@example.com",
            "password": "Test123!@#",
            "full_name": "Test User 2"
        }
    )

    # Then try to login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test2@example.com",
            "password": "Test123!@#"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "test2@example.com"

def test_login_wrong_password():
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_login_nonexistent_user():
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "Test123!@#"
        }
    )
    assert response.status_code == 401 