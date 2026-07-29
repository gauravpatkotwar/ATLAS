import logging
from typing import List
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from atlas.database.session import get_db
from atlas.database.models import User, Integration
from atlas.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Pydantic Schemas ---
class IntegrationToggleRequest(BaseModel):
    provider_name: str  # google_calendar, slack, linkedin

class IntegrationResponse(BaseModel):
    id: int
    provider_name: str
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- API Routes ---

@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all registered third-party integrations for the tenant."""
    stmt = select(Integration).where(Integration.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/toggle", response_model=IntegrationResponse)
async def toggle_integration(
    payload: IntegrationToggleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggles status (connect/disconnect) for a third-party integration."""
    stmt = select(Integration).where(
        Integration.tenant_id == current_user.tenant_id,
        Integration.provider_name == payload.provider_name
    )
    res = await db.execute(stmt)
    integration = res.scalars().first()

    if integration:
        integration.is_active = not integration.is_active
    else:
        integration = Integration(
            tenant_id=current_user.tenant_id,
            provider_name=payload.provider_name,
            is_active=True
        )
        db.add(integration)

    await db.commit()
    await db.refresh(integration)
    return integration
