import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from atlas.database.session import get_db
from atlas.database.models import User, SSOConfig, Tenant
from atlas.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Pydantic Schemas ---
class SSOConfigCreate(BaseModel):
    idp_entity_id: str
    idp_sso_url: str
    x509_certificate: str

class SSOConfigResponse(BaseModel):
    id: int
    idp_entity_id: str
    idp_sso_url: str
    x509_certificate: str
    is_active: bool

    class Config:
        from_attributes = True

class SSOLoginRequest(BaseModel):
    email: str
    org_name: str

class SSOLoginResponse(BaseModel):
    access_token: str
    token_type: str


# --- API Routes ---

@router.get("/config", response_model=Optional[SSOConfigResponse])
async def get_sso_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves SAML SSO configuration for the current user's tenant."""
    stmt = select(SSOConfig).where(SSOConfig.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    return res.scalars().first()


@router.post("/config", response_model=SSOConfigResponse)
async def update_sso_config(
    payload: SSOConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates or updates the SAML SSO configuration for the tenant."""
    stmt = select(SSOConfig).where(SSOConfig.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    config = res.scalars().first()

    if config:
        config.idp_entity_id = payload.idp_entity_id
        config.idp_sso_url = payload.idp_sso_url
        config.x509_certificate = payload.x509_certificate
    else:
        config = SSOConfig(
            tenant_id=current_user.tenant_id,
            idp_entity_id=payload.idp_entity_id,
            idp_sso_url=payload.idp_sso_url,
            x509_certificate=payload.x509_certificate,
            is_active=True
        )
        db.add(config)

    await db.commit()
    await db.refresh(config)
    return config


@router.post("/login-mock", response_model=SSOLoginResponse)
async def sso_login_mock(
    payload: SSOLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Simulates SAML authentication, issuing a standard JWT token for the user."""
    # Find user by email
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        # Check if tenant exists
        stmt_t = select(Tenant).where(Tenant.name == payload.org_name)
        res_t = await db.execute(stmt_t)
        tenant = res_t.scalars().first()
        if not tenant:
            tenant = Tenant(name=payload.org_name, subscription_tier="enterprise")
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)

        # Create user
        from atlas.services.auth import AuthService
        user = User(
            email=payload.email,
            hashed_password=AuthService.hash_password("sso_bypass_password"),
            role="recruiter",
            tenant_id=tenant.id
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Generate token
    from atlas.config.settings import settings
    import jwt
    import datetime

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload_jwt = {
        "sub": user.email,
        "exp": expire,
        "role": user.role,
        "tenant_id": user.tenant_id
    }
    token = jwt.encode(payload_jwt, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}
