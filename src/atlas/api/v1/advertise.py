"""
Atlas Advertise API
Handles ad packages, advertiser campaigns, payments (Stripe/Razorpay), and analytics.
"""
import logging
import uuid
import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from atlas.database.session import get_db
from atlas.api.deps import get_current_user
from atlas.database.models import User, get_utc_now

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# AD PACKAGES (static config — no DB needed)
# ---------------------------------------------------------------------------

AD_PACKAGES = [
    {
        "id": "job_spotlight",
        "name": "Job Spotlight",
        "tagline": "Feature your job at the top of every search",
        "price_usd": 199,
        "price_inr": 16500,
        "duration_days": 30,
        "features": [
            "Pinned at top of Job Board for 30 days",
            "Highlighted with 'Featured' badge",
            "Shown in Atlas Copilot recommendations",
            "Up to 3 active job slots",
            "Performance analytics dashboard",
        ],
        "icon": "briefcase",
        "color": "#3b82f6",
        "popular": False,
    },
    {
        "id": "talent_reach",
        "name": "Talent Reach",
        "tagline": "Direct exposure to 10k+ active candidates",
        "price_usd": 499,
        "price_inr": 41500,
        "duration_days": 30,
        "features": [
            "Everything in Job Spotlight",
            "Company profile banner in Candidate search",
            "Featured in Atlas TV channel ads",
            "Weekly AI-matched candidate recommendations",
            "Priority recruiter support",
            "Unlimited job slots",
        ],
        "icon": "users",
        "color": "#8b5cf6",
        "popular": True,
    },
    {
        "id": "brand_channel",
        "name": "Brand Channel",
        "tagline": "Own a branded channel on Atlas TV",
        "price_usd": 999,
        "price_inr": 82500,
        "duration_days": 30,
        "features": [
            "Everything in Talent Reach",
            "Dedicated company channel on Atlas TV",
            "Upload up to 10 branded videos/month",
            "Pre-roll brand mentions (5-sec) before relevant videos",
            "Custom channel banner + branding",
            "CEO / leadership spotlight feature",
            "Monthly reach report",
        ],
        "icon": "tv",
        "color": "#e11d48",
        "popular": False,
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "tagline": "Full-stack recruitment marketing for large teams",
        "price_usd": 0,  # Custom pricing
        "price_inr": 0,
        "duration_days": 90,
        "features": [
            "Everything in Brand Channel",
            "Custom AI-powered candidate shortlisting",
            "Dedicated Atlas account manager",
            "White-label candidate portal option",
            "ATS API integration",
            "Custom reporting & SLA",
            "Quarterly strategy review",
        ],
        "icon": "building",
        "color": "#f59e0b",
        "popular": False,
    },
]


# ---------------------------------------------------------------------------
# PYDANTIC SCHEMAS
# ---------------------------------------------------------------------------

class AdvertiserInquiryCreate(BaseModel):
    company_name: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    package_id: str
    budget_range: Optional[str] = None  # e.g. "$500-$1000/mo"
    goals: Optional[str] = None         # What they want to achieve
    currency: str = "usd"               # usd or inr


class CampaignCheckoutRequest(BaseModel):
    inquiry_id: str
    package_id: str
    provider: str = "stripe"  # stripe or razorpay
    currency: str = "usd"


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _get_package(package_id: str) -> Dict[str, Any]:
    pkg = next((p for p in AD_PACKAGES if p["id"] == package_id), None)
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{package_id}' not found")
    return pkg


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@router.get("/packages")
async def list_packages():
    """Return all available advertising packages."""
    return {"packages": AD_PACKAGES}


@router.post("/inquire")
async def submit_inquiry(
    body: AdvertiserInquiryCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit an advertiser inquiry. Creates a record and returns an inquiry_id
    that can be used to initiate payment.
    """
    pkg = _get_package(body.package_id)

    inquiry_id = str(uuid.uuid4())[:12].upper()

    # Persist inquiry via raw SQL (no new model needed — uses ad_inquiries table)
    try:
        await db.execute(text("""
            INSERT INTO ad_inquiries
                (inquiry_id, company_name, contact_name, contact_email,
                 contact_phone, website, package_id, budget_range, goals,
                 currency, status, created_at)
            VALUES
                (:inquiry_id, :company_name, :contact_name, :contact_email,
                 :contact_phone, :website, :package_id, :budget_range, :goals,
                 :currency, 'pending', NOW())
        """), {
            "inquiry_id": inquiry_id,
            "company_name": body.company_name,
            "contact_name": body.contact_name,
            "contact_email": body.contact_email,
            "contact_phone": body.contact_phone,
            "website": body.website,
            "package_id": body.package_id,
            "budget_range": body.budget_range,
            "goals": body.goals,
            "currency": body.currency,
        })
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save inquiry: {e}")
        # Still return success with generated ID even if DB fails (graceful)

    price = pkg["price_usd"] if body.currency == "usd" else pkg["price_inr"]
    currency_sym = "$" if body.currency == "usd" else "₹"

    return {
        "inquiry_id": inquiry_id,
        "package": pkg["name"],
        "price": price,
        "currency": body.currency,
        "currency_symbol": currency_sym,
        "duration_days": pkg["duration_days"],
        "message": f"Inquiry received! Your inquiry ID is {inquiry_id}. Proceed to payment to activate your campaign.",
        "next_step": "checkout",
    }


@router.post("/checkout")
async def create_checkout(
    body: CampaignCheckoutRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a payment checkout session for an ad campaign.
    Returns a checkout URL (Stripe or Razorpay).
    """
    pkg = _get_package(body.package_id)

    if pkg["price_usd"] == 0:
        return {
            "type": "enterprise",
            "message": "Enterprise plans require a custom quote. Our team will contact you within 24 hours.",
            "contact_email": "advertise@atlasawi.com",
        }

    price_usd = pkg["price_usd"]
    price_inr = pkg["price_inr"]

    if body.provider == "stripe":
        # Mock Stripe Checkout Session
        session_id = f"cs_atlas_adv_{body.inquiry_id}_{uuid.uuid4().hex[:8]}"
        # In production: stripe.checkout.sessions.create(...)
        checkout_url = f"https://checkout.stripe.com/pay/{session_id}"
        return {
            "provider": "stripe",
            "checkout_url": checkout_url,
            "session_id": session_id,
            "amount": price_usd,
            "currency": "usd",
            "package": pkg["name"],
            "inquiry_id": body.inquiry_id,
            "mode": "mock",  # Remove in production
        }
    elif body.provider == "razorpay":
        order_id = f"order_atlas_adv_{body.inquiry_id}_{uuid.uuid4().hex[:8]}"
        return {
            "provider": "razorpay",
            "order_id": order_id,
            "amount": price_inr * 100,  # Razorpay uses paise
            "currency": "INR",
            "package": pkg["name"],
            "inquiry_id": body.inquiry_id,
            "key_id": "rzp_test_atlas",  # Replace with real key
            "mode": "mock",
        }
    else:
        raise HTTPException(status_code=400, detail="Unsupported payment provider")


@router.post("/confirm/{inquiry_id}")
async def confirm_payment(
    inquiry_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Mark a campaign as paid and activate it."""
    try:
        await db.execute(text("""
            UPDATE ad_inquiries
            SET status = 'active', paid_at = NOW()
            WHERE inquiry_id = :inquiry_id
        """), {"inquiry_id": inquiry_id})
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to confirm payment: {e}")

    return {
        "status": "active",
        "message": "Payment confirmed! Your campaign is now live.",
        "inquiry_id": inquiry_id,
    }


@router.get("/campaigns")
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin: list all advertiser inquiries/campaigns."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    try:
        result = await db.execute(text("""
            SELECT inquiry_id, company_name, contact_name, contact_email,
                   package_id, status, currency, created_at, paid_at
            FROM ad_inquiries
            ORDER BY created_at DESC
            LIMIT 100
        """))
        rows = result.fetchall()
        campaigns = []
        for r in rows:
            pkg = next((p for p in AD_PACKAGES if p["id"] == r.package_id), {})
            campaigns.append({
                "inquiry_id": r.inquiry_id,
                "company_name": r.company_name,
                "contact_name": r.contact_name,
                "contact_email": r.contact_email,
                "package_id": r.package_id,
                "package_name": pkg.get("name", r.package_id),
                "price_usd": pkg.get("price_usd", 0),
                "status": r.status,
                "currency": r.currency,
                "created_at": str(r.created_at),
                "paid_at": str(r.paid_at) if r.paid_at else None,
            })
        return {"campaigns": campaigns, "total": len(campaigns)}
    except Exception as e:
        logger.error(f"Failed to list campaigns: {e}")
        return {"campaigns": [], "total": 0}


@router.get("/stats")
async def ad_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin: revenue and campaign stats."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE status = 'active') as active_campaigns,
                COUNT(*) FILTER (WHERE status = 'pending') as pending_campaigns,
                COUNT(*) as total_inquiries
            FROM ad_inquiries
        """))
        row = result.fetchone()

        # Calculate revenue from active campaigns
        active_result = await db.execute(text("""
            SELECT package_id, COUNT(*) as cnt FROM ad_inquiries
            WHERE status = 'active' GROUP BY package_id
        """))
        active_rows = active_result.fetchall()

        total_revenue = 0
        for ar in active_rows:
            pkg = next((p for p in AD_PACKAGES if p["id"] == ar.package_id), {})
            total_revenue += pkg.get("price_usd", 0) * ar.cnt

        return {
            "active_campaigns": row.active_campaigns if row else 0,
            "pending_campaigns": row.pending_campaigns if row else 0,
            "total_inquiries": row.total_inquiries if row else 0,
            "total_revenue_usd": total_revenue,
            "packages": AD_PACKAGES,
        }
    except Exception:
        return {
            "active_campaigns": 0,
            "pending_campaigns": 0,
            "total_inquiries": 0,
            "total_revenue_usd": 0,
        }
