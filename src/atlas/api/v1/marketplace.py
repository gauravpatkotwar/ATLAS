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
    category: str  # "hardware", "apparel", "gear", "software", "ai_agents", "media", "enterprise"
    product_type: str = "digital"  # "physical" or "digital"
    icon: Optional[str] = "📦"
    badge: Optional[str] = "STORE EXCLUSIVE"
    download_url: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    product_type: str
    icon: Optional[str]
    badge: Optional[str]
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


DEFAULT_STORE_PRODUCTS = [
    # 📦 PHYSICAL PRODUCTS
    {
        "name": "Atlas AI Smart Desk Terminal",
        "description": "Stand-alone 5-inch IPS desktop console with tactile hotkeys, ambient RGB status ring, and real-time candidate queue stream.",
        "price": 299.00,
        "category": "hardware",
        "product_type": "physical",
        "icon": "🖥️",
        "badge": "📦 PHYSICAL HARDWARE",
        "download_url": None,
        "author_email": "store@atlas.ai"
    },
    {
        "name": "Atlas Hardware Security Passkey (FIDO2)",
        "description": "Biometric USB-C hardware passkey with encrypted secure element for 2-factor authentication & Control Center admin verification.",
        "price": 49.00,
        "category": "hardware",
        "product_type": "physical",
        "icon": "🔑",
        "badge": "📦 PHYSICAL HARDWARE",
        "download_url": None,
        "author_email": "store@atlas.ai"
    },
    {
        "name": "Atlas Executive Hoodie (Matte Black)",
        "description": "Heavyweight 450GSM organic cotton hoodie featuring embroidered metallic silver Atlas emblem, hidden zipper pocket, & thumbhole cuffs.",
        "price": 89.00,
        "category": "apparel",
        "product_type": "physical",
        "icon": "👕",
        "badge": "📦 PHYSICAL MERCH",
        "download_url": None,
        "author_email": "store@atlas.ai"
    },
    {
        "name": "Atlas Cyber Hardshell Tech Backpack",
        "description": "Waterproof Kevlar-reinforced laptop vault with TSA combination lock, USB-C pass-through port, and magnetic tech gear organizers.",
        "price": 149.00,
        "category": "gear",
        "product_type": "physical",
        "icon": "🎒",
        "badge": "📦 PHYSICAL GEAR",
        "download_url": None,
        "author_email": "store@atlas.ai"
    },
    {
        "name": "Atlas Insulated Stainless Tumbler (750ml)",
        "description": "Double-walled vacuum insulated matte black flask with laser-etched metallic silver logo. Keeps drinks cold 24h or hot 12h.",
        "price": 34.00,
        "category": "gear",
        "product_type": "physical",
        "icon": "🥤",
        "badge": "📦 PHYSICAL GEAR",
        "download_url": None,
        "author_email": "store@atlas.ai"
    },

    # 💻 DIGITAL PRODUCTS & SOFTWARE ADDONS
    {
        "name": "Atlas AI Voice Copilot Expansion (5,000 Mins)",
        "description": "5,000 AI voice interview minutes, custom voice cloning studio, multi-language speech-to-text, and automated sentiment scoring.",
        "price": 199.00,
        "category": "ai_credits",
        "product_type": "digital",
        "icon": "🎙️",
        "badge": "💻 DIGITAL UNLOCK",
        "download_url": "https://localhost/docs/voice-copilot-guide.pdf",
        "author_email": "store@atlas.ai"
    },
    {
        "name": "Automated Background & Degree Verification API",
        "description": "Instant automated background check, criminal record audit, employment verification, and university degree validation API.",
        "price": 249.00,
        "category": "software",
        "product_type": "digital",
        "icon": "🛡️",
        "badge": "💻 DIGITAL API",
        "download_url": "https://localhost/docs/verification-api-sdk.zip",
        "author_email": "store@atlas.ai"
    },
    {
        "name": "Atlas Autonomous Sourcing Agent (24/7)",
        "description": "Autonomous AI agent that searches LinkedIn, GitHub, & StackOverflow 24/7 to engage passive candidates with personalized outreach.",
        "price": 299.00,
        "category": "ai_agents",
        "product_type": "digital",
        "icon": "🤖",
        "badge": "💻 DIGITAL AGENT",
        "download_url": "https://localhost/docs/sourcing-agent-manifest.json",
        "author_email": "store@atlas.ai"
    },
    {
        "name": "Atlas TV Sponsored Hiring Reel Broadcast Pack",
        "description": "Broadcast 3 company recruitment video reels across 58+ Atlas TV channels reaching 50,000+ active tech and AI candidates.",
        "price": 399.00,
        "category": "media",
        "product_type": "digital",
        "icon": "📺",
        "badge": "💻 DIGITAL MEDIA",
        "download_url": "https://localhost/docs/atlas-tv-ad-specs.pdf",
        "author_email": "store@atlas.ai"
    },
    {
        "name": "Atlas Enterprise White-Label & Custom Domain Suite",
        "description": "Full white-label branding removal, custom domain routing, custom email SMTP server integration, and SAML SSO enforcement.",
        "price": 499.00,
        "category": "enterprise",
        "product_type": "digital",
        "icon": "🌐",
        "badge": "💻 DIGITAL LICENSE",
        "download_url": "https://localhost/docs/white-label-license-key.txt",
        "author_email": "store@atlas.ai"
    }
]


# --- API Routes ---

@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all Atlas Store products (physical & digital)."""
    stmt = select(MarketplaceProduct)
    if type and type != 'all':
        stmt = stmt.where(MarketplaceProduct.product_type == type)
    stmt = stmt.order_by(MarketplaceProduct.id.asc())
    result = await db.execute(stmt)
    products = result.scalars().all()
    
    # Auto seed if store is empty
    if not products:
        for pdata in DEFAULT_STORE_PRODUCTS:
            prod = MarketplaceProduct(
                tenant_id=current_user.tenant_id,
                name=pdata["name"],
                description=pdata["description"],
                price=pdata["price"],
                category=pdata["category"],
                product_type=pdata["product_type"],
                icon=pdata["icon"],
                badge=pdata["badge"],
                download_url=pdata["download_url"],
                author_email=pdata["author_email"]
            )
            db.add(prod)
        await db.commit()
        res = await db.execute(select(MarketplaceProduct).order_by(MarketplaceProduct.id.asc()))
        products = res.scalars().all()
        
    return products


@router.post("/seed")
async def seed_store(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Admin endpoint to re-seed the Atlas Store product line."""
    # Delete existing items to avoid duplicates
    existing = await db.execute(select(MarketplaceProduct))
    for item in existing.scalars().all():
        await db.delete(item)
    await db.commit()

    created_items = []
    for pdata in DEFAULT_STORE_PRODUCTS:
        prod = MarketplaceProduct(
            tenant_id=current_user.tenant_id,
            name=pdata["name"],
            description=pdata["description"],
            price=pdata["price"],
            category=pdata["category"],
            product_type=pdata["product_type"],
            icon=pdata["icon"],
            badge=pdata["badge"],
            download_url=pdata["download_url"],
            author_email=pdata["author_email"]
        )
        db.add(prod)
        created_items.append(prod)
    await db.commit()
    return {"status": "success", "count": len(created_items)}


@router.post("/products", response_model=ProductResponse)
async def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publishes a new Atlas Store product listing."""
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
        product_type=payload.product_type,
        icon=payload.icon or "📦",
        badge=payload.badge or "STORE PRODUCT",
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
    """Simulates checkout transaction for a physical or digital product."""
    prod_stmt = select(MarketplaceProduct).where(MarketplaceProduct.id == product_id)
    prod_res = await db.execute(prod_stmt)
    product = prod_res.scalars().first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atlas Store product not found."
        )

    purch_stmt = select(MarketplacePurchase).where(
        MarketplacePurchase.product_id == product_id,
        MarketplacePurchase.tenant_id == current_user.tenant_id
    )
    purch_res = await db.execute(purch_stmt)
    if purch_res.scalars().first():
        return {"status": "already_purchased", "message": f"{product.name} is already in your inventory."}

    purchase = MarketplacePurchase(
        tenant_id=current_user.tenant_id,
        product_id=product_id
    )
    db.add(purchase)
    await db.commit()

    if product.product_type == 'physical':
        tracking_num = f"ATLAS-TRACK-88{product.id}992X"
        return {
            "status": "success",
            "message": f"Order Confirmed! Your physical product '{product.name}' is being processed for dispatch.",
            "tracking_number": tracking_num,
            "estimated_delivery": "2-4 Business Days"
        }
    else:
        return {
            "status": "success",
            "message": f"License Unlocked! Digital product '{product.name}' is now active in your workspace inventory.",
            "download_url": product.download_url or "https://localhost/docs/active-license.pdf"
        }


@router.get("/purchases", response_model=List[PurchaseResponse])
async def list_purchases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all products purchased by the user's workspace tenant."""
    stmt = select(MarketplacePurchase).where(MarketplacePurchase.tenant_id == current_user.tenant_id).order_by(MarketplacePurchase.purchased_at.desc())
    result = await db.execute(stmt)
    purchases = result.scalars().all()

    response = []
    for purch in purchases:
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
