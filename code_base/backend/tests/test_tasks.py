import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from PIL import Image
import io

client = TestClient(app)

def create_test_image():
    """Create a test image file."""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_create_task():
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "Test123!@#"
        }
    )
    token = login_response.json()["token"]

    # Create test image
    test_image = create_test_image()

    # Create task
    response = client.post(
        "/api/v1/tasks/",
        files={"image": ("test.png", test_image, "image/png")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"

def test_get_tasks():
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "Test123!@#"
        }
    )
    token = login_response.json()["token"]

    # Get tasks
    response = client.get(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_task():
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "Test123!@#"
        }
    )
    token = login_response.json()["token"]

    # Create a task first
    test_image = create_test_image()
    create_response = client.post(
        "/api/v1/tasks/",
        files={"image": ("test.png", test_image, "image/png")},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]

    # Get the task
    response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id 