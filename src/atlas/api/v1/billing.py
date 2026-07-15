from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from atlas.database.session import get_db
from atlas.services.billing import BillingService
from atlas.api.deps import get_current_user
from atlas.database.models import User

router = APIRouter()


class CheckoutRequest(BaseModel):
    provider: str  # stripe or razorpay


class ConfirmRequest(BaseModel):
    provider: str
    reference_id: str


@router.post("/checkout", response_model=Dict[str, Any])
async def create_checkout(
    req: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        billing_service = BillingService(db, current_user.tenant_id)
        session_info = await billing_service.create_checkout_session(
            req.provider
        )
        return session_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Billing error: {e}",
        )


@router.post("/confirm")
async def confirm_checkout(
    req: ConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        billing_service = BillingService(db, current_user.tenant_id)
        success = await billing_service.confirm_payment(
            req.provider, req.reference_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment confirmation failed",
            )
        return {
            "status": "success",
            "message": f"Workspace upgraded to PRO via {req.provider.upper()}.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confirmation error: {e}",
        )
