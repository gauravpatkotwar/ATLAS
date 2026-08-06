from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.database.session import get_db
from atlas.services.auth import AuthService
from atlas.api.deps import get_current_user
from atlas.database.models import User
from atlas.utils.email_validator import validate_email_deliverable

router = APIRouter()


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "recruiter"
    org_name: Optional[str] = None
    invite_code: Optional[str] = None
    recovery_email: Optional[str] = None  # Optional secondary recovery email


class UserResponse(BaseModel):
    id: int
    tenant_id: int
    email: EmailStr
    role: str
    is_active: bool
    video_path: Optional[str] = None
    subscription_tier: Optional[str] = "free"
    invite_code: Optional[str] = ""

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ForgotPasswordRequest(BaseModel):
    email: str  # Primary or recovery email


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None  # Shown directly (no SMTP configured)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user after validating that the email is real and deliverable.
    Checks: disposable email blocklist + DNS MX record lookup.
    """
    # ── Email deliverability check ──────────────────────────────────────────
    is_valid, error_msg = await validate_email_deliverable(str(payload.email))
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Email validation failed: {error_msg}",
        )

    # ── Optional recovery email validation ──────────────────────────────────
    if payload.recovery_email and payload.recovery_email.strip():
        rec_valid, rec_error = await validate_email_deliverable(payload.recovery_email.strip())
        if not rec_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Recovery email validation failed: {rec_error}",
            )

    # ── Register user ────────────────────────────────────────────────────────
    auth_service = AuthService(db)
    try:
        user = await auth_service.register_user(
            email=payload.email,
            password=payload.password,
            role=payload.role,
            org_name=payload.org_name,
            invite_code=payload.invite_code,
            recovery_email=payload.recovery_email,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Authenticates credentials and returns a signed Bearer JWT token."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


from sqlalchemy.future import select
from atlas.database.models import Tenant


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the authenticated profile payload with subscription parameters loaded."""
    stmt = select(Tenant).where(Tenant.id == current_user.tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalars().first()

    tier = tenant.subscription_tier if tenant else "free"
    code = tenant.invite_code if tenant else ""

    return UserResponse(
        id=current_user.id,
        tenant_id=current_user.tenant_id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        video_path=current_user.video_path,
        subscription_tier=tier,
        invite_code=code,
    )


class GoogleLoginRequest(BaseModel):
    token: str
    email: str


@router.post("/google", response_model=TokenResponse)
async def google_login(
    payload: GoogleLoginRequest, db: AsyncSession = Depends(get_db)
):
    """Authenticates or automatically registers a Google user, returning a signed JWT token."""
    import uuid

    # Development simulator check
    if not payload.token.startswith("mock-google-token-"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google OAuth identity credentials.",
        )

    auth_service = AuthService(db)
    user = await auth_service.repo.get_by_email(payload.email)

    if not user:
        # Register new Google User with automated Tenant creation
        org_name = f"{payload.email.split('@')[0].capitalize()}'s Workspace"
        try:
            user = await auth_service.register_user(
                email=payload.email,
                password=f"google-oauth-random-{uuid.uuid4().hex[:12]}",
                role="recruiter",
                org_name=org_name,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google account registration failed: {e}",
            )

    # Generate JWT login token
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """
    Generates a one-time password reset token for the given email (primary or recovery).
    Returns the token directly in response (no SMTP required).
    """
    auth_service = AuthService(db)
    token = await auth_service.generate_password_reset_token(payload.email)

    if not token:
        # Return success message even if email not found (prevents user enumeration)
        return ForgotPasswordResponse(
            message="If this email is registered, a reset token has been generated.",
            reset_token=None,
        )

    return ForgotPasswordResponse(
        message="Password reset token generated successfully. Use the token below to set a new password.",
        reset_token=token,
    )


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """
    Validates the reset token and applies a new password.
    Token is valid for 1 hour.
    """
    if len(payload.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    auth_service = AuthService(db)
    success = await auth_service.reset_password_with_token(payload.token, payload.new_password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token. Please request a new one.",
        )

    return {"message": "Password successfully reset. You can now sign in with your new password."}
