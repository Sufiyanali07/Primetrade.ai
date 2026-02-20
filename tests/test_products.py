"""Tests: product CRUD, public vs admin."""
import pytest
from fastapi.testclient import TestClient


def test_list_products_public(client: TestClient) -> None:
    """List products does not require auth."""
    r = client.get("/api/v1/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_product_by_id_public(client: TestClient, db) -> None:
    """Get product by ID is public (after we have one)."""
    # Create via admin first
    from app.database.models import Product
    from decimal import Decimal
    product = Product(name="Test Product", description="Desc", price=Decimal("19.99"))
    db.add(product)
    db.commit()
    db.refresh(product)
    r = client.get(f"/api/v1/products/{product.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Test Product"
    assert data["price"] == 19.99


def test_create_product_requires_admin(client: TestClient, user_token: str) -> None:
    """Create product without admin token returns 403."""
    r = client.post(
        "/api/v1/products",
        json={"name": "P", "description": "D", "price": 10.5},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 403


def test_create_product_admin(client: TestClient, admin_token: str) -> None:
    """Admin can create product."""
    r = client.post(
        "/api/v1/products",
        json={"name": "New Product", "description": "Nice", "price": 29.99},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "New Product"
    assert data["price"] == 29.99
    assert "id" in data


def test_update_product_admin(client: TestClient, admin_token: str, db) -> None:
    """Admin can update product."""
    from app.database.models import Product
    from decimal import Decimal
    product = Product(name="Old", description="D", price=Decimal("10.00"))
    db.add(product)
    db.commit()
    db.refresh(product)
    r = client.put(
        f"/api/v1/products/{product.id}",
        json={"name": "Updated", "price": 15.00},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Updated"
    assert r.json()["price"] == 15.0


def test_delete_product_admin(client: TestClient, admin_token: str, db) -> None:
    """Admin can delete product."""
    from app.database.models import Product
    from decimal import Decimal
    product = Product(name="To Delete", description="D", price=Decimal("5.00"))
    db.add(product)
    db.commit()
    db.refresh(product)
    pid = product.id
    r = client.delete(f"/api/v1/products/{pid}", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 204
    r2 = client.get(f"/api/v1/products/{pid}")
    assert r2.status_code == 404
