"""Tests: register, login, token validation, RBAC."""
import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient) -> None:
    """Register returns 200 and user data."""
    r = client.post(
        "/api/v1/auth/register",
        json={"name": "New User", "email": "new@test.com", "password": "securepass123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "new@test.com"
    assert data["name"] == "New User"
    assert data["role"] == "user"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_email(client: TestClient) -> None:
    """Duplicate email returns 409."""
    payload = {"name": "User", "email": "dup@test.com", "password": "password123"}
    client.post("/api/v1/auth/register", json=payload)
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409


def test_login_success(client: TestClient, test_user: None) -> None:
    """Login returns 200 and access_token."""
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "password123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient) -> None:
    """Invalid email/password returns 401."""
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@test.com", "password": "wrong"},
    )
    assert r.status_code == 401


def test_token_validation(client: TestClient, user_token: str) -> None:
    """Valid token allows access to protected route (e.g. users list requires admin)."""
    # Without token: 401 or 403
    r = client.get("/api/v1/users")
    assert r.status_code in (401, 403)
    # With token but non-admin: 403
    r = client.get("/api/v1/users", headers={"Authorization": f"Bearer {user_token}"})
    assert r.status_code == 403


def test_rbac_admin_can_list_users(client: TestClient, admin_token: str) -> None:
    """Admin can list users."""
    r = client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
