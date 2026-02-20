"""Products API: CRUD. Create/Update/Delete admin only; List/Get public."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_admin
from app.database.connection import get_db
from app.database.models import User
from app.database.schemas import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import (
    create_product,
    delete_product,
    get_product_by_id,
    list_products,
    update_product,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def list_products_route(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
):
    """List products (public)."""
    return list_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_route(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID (public)."""
    return ProductResponse.model_validate(get_product_by_id(db, product_id))


@router.post("", response_model=ProductResponse, status_code=201)
def create_product_route(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create product (admin only)."""
    return create_product(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_route(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update product (admin only)."""
    return update_product(db, product_id, data)


@router.delete("/{product_id}", status_code=204)
def delete_product_route(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete product (admin only)."""
    delete_product(db, product_id)
