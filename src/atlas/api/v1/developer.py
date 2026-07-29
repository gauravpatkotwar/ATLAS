import logging
import secrets
import hashlib
from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from atlas.database.session import get_db
from atlas.database.models import User, APIKey, WebhookEndpoint
from atlas.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Pydantic Schemas ---
class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class APIKeyCreateResponse(APIKeyResponse):
    raw_key: str  # Only returned on creation

class WebhookEndpointCreate(BaseModel):
    url: str
    secret_token: str
    events: List[str]

class WebhookEndpointResponse(BaseModel):
    id: int
    url: str
    secret_token: str
    events: List[str]
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- API Routes ---

@router.get("/keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all active API keys for the current tenant."""
    stmt = select(APIKey).where(APIKey.tenant_id == current_user.tenant_id, APIKey.is_active == True)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/keys", response_model=APIKeyCreateResponse)
async def create_api_key(
    payload: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generates a new API key for the tenant and returns it."""
    raw_secret = secrets.token_hex(24)
    key_prefix = "at_"
    full_key = f"{key_prefix}{raw_secret}"
    hashed = hashlib.sha256(full_key.encode()).hexdigest()

    api_key = APIKey(
        tenant_id=current_user.tenant_id,
        name=payload.name,
        key_prefix=key_prefix,
        hashed_key=hashed,
        is_active=True
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    # Convert to response
    resp = APIKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        raw_key=full_key
    )
    return resp


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revokes / deletes an API key."""
    stmt = select(APIKey).where(APIKey.id == key_id, APIKey.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    key = res.scalars().first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    await db.delete(key)
    await db.commit()
    return


@router.get("/webhooks", response_model=List[WebhookEndpointResponse])
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists registered webhook endpoints for the tenant."""
    stmt = select(WebhookEndpoint).where(WebhookEndpoint.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/webhooks", response_model=WebhookEndpointResponse)
async def create_webhook(
    payload: WebhookEndpointCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Registers a new webhook endpoint."""
    webhook = WebhookEndpoint(
        tenant_id=current_user.tenant_id,
        url=payload.url,
        secret_token=payload.secret_token,
        events=payload.events,
        is_active=True
    )
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return webhook


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes a webhook endpoint."""
    stmt = select(WebhookEndpoint).where(WebhookEndpoint.id == webhook_id, WebhookEndpoint.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    webhook = res.scalars().first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    await db.delete(webhook)
    await db.commit()
    return
