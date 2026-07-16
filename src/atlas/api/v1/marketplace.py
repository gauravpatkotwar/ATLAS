import logging
from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from atlas.database.session import get_db
from atlas.database.models import User, MarketplaceProduct, MarketplacePurchase
from atlas.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Pydantic Schemas ---
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str  # "software" or "service"
    download_url: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    download_url: Optional[str]
    author_email: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class PurchaseResponse(BaseModel):
    id: int
    product_id: int
    purchased_at: datetime.datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# --- API Routes ---

@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all published marketplace products."""
    stmt = select(MarketplaceProduct).order_by(MarketplaceProduct.created_at.desc())
    result = await db.execute(stmt)
    products = result.scalars().all()
    return products


@router.post("/products", response_model=ProductResponse)
async def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publishes a new developer software utility or recruitment consulting service."""
    if payload.price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price cannot be negative."
        )

    product = MarketplaceProduct(
        tenant_id=current_user.tenant_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        category=payload.category,
        download_url=payload.download_url,
        author_email=current_user.email
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.post("/products/{product_id}/purchase")
async def purchase_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Simulates a checkout transaction and unlocks the software/service item."""
    # Verify product exists
    prod_stmt = select(MarketplaceProduct).where(MarketplaceProduct.id == product_id)
    prod_res = await db.execute(prod_stmt)
    product = prod_res.scalars().first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace listing not found."
        )

    # Check if already purchased by this tenant
    purch_stmt = select(MarketplacePurchase).where(
        MarketplacePurchase.product_id == product_id,
        MarketplacePurchase.tenant_id == current_user.tenant_id
    )
    purch_res = await db.execute(purch_stmt)
    if purch_res.scalars().first():
        return {"status": "already_purchased", "message": "Product is already in your inventory."}

    purchase = MarketplacePurchase(
        tenant_id=current_user.tenant_id,
        product_id=product_id
    )
    db.add(purchase)
    await db.commit()
    return {"status": "success", "message": f"Successfully purchased {product.name}."}


@router.get("/purchases", response_model=List[PurchaseResponse])
async def list_purchases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all marketplace items acquired by the user's workspace tenant."""
    stmt = select(MarketplacePurchase).where(MarketplacePurchase.tenant_id == current_user.tenant_id).order_by(MarketplacePurchase.purchased_at.desc())
    result = await db.execute(stmt)
    purchases = result.scalars().all()

    response = []
    for purch in purchases:
        # Load product details
        prod_stmt = select(MarketplaceProduct).where(MarketplaceProduct.id == purch.product_id)
        prod_res = await db.execute(prod_stmt)
        product = prod_res.scalars().first()
        
        response.append(PurchaseResponse(
            id=purch.id,
            product_id=purch.product_id,
            purchased_at=purch.purchased_at,
            product=ProductResponse.from_orm(product) if product else None
        ))
    return response
