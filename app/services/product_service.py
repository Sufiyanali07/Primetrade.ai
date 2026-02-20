"""Product service: CRUD for products."""
from app.database.models import Product
from app.database.schemas import ProductCreate, ProductResponse, ProductUpdate
from app.utils.exceptions import NotFoundException
from sqlalchemy.orm import Session


def create_product(db: Session, data: ProductCreate) -> ProductResponse:
    """Create a new product."""
    product = Product(name=data.name, description=data.description, price=data.price)
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(product)


def get_product_by_id(db: Session, product_id: int) -> Product:
    """Get product by ID or raise 404."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundException("Product not found")
    return product


def list_products(db: Session, skip: int = 0, limit: int = 100) -> list[ProductResponse]:
    """List products with pagination."""
    products = db.query(Product).offset(skip).limit(limit).all()
    return [ProductResponse.model_validate(p) for p in products]


def update_product(db: Session, product_id: int, data: ProductUpdate) -> ProductResponse:
    """Update a product."""
    product = get_product_by_id(db, product_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(product)


def delete_product(db: Session, product_id: int) -> None:
    """Delete a product."""
    product = get_product_by_id(db, product_id)
    db.delete(product)
    db.commit()
