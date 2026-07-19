from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import AuthenticationException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    sub: str
    tenant_id: str
    email: str
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    type: str = "access"
    iat: int
    exp: int
    jti: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(
    subject: str,
    tenant_id: str,
    email: str,
    roles: list[str],
    permissions: list[str],
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth.access_token_expire_minutes)

    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "email": email,
        "roles": roles,
        "permissions": permissions,
        "type": "access",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.auth.private_key, algorithm=settings.auth.algorithm)


def create_refresh_token(
    subject: str,
    tenant_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.auth.refresh_token_expire_days)

    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "type": "refresh",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.auth.private_key, algorithm=settings.auth.algorithm)


def create_token_pair(
    subject: str,
    tenant_id: str,
    email: str,
    roles: list[str],
    permissions: list[str],
) -> TokenPair:
    access_token = create_access_token(subject, tenant_id, email, roles, permissions)
    refresh_token = create_refresh_token(subject, tenant_id)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.auth.access_token_expire_minutes * 60,
    )


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.auth.public_key,
            algorithms=[settings.auth.algorithm],
            audience=settings.auth.audience,
            issuer=settings.auth.issuer,
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise AuthenticationException(f"Invalid token: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_random_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_verification_token() -> str:
    return generate_random_token(32)


def generate_password_reset_token() -> str:
    return generate_random_token(32)


def generate_api_key(prefix: str = "atlas") -> str:
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    return get_password_hash(api_key)


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    return verify_password(api_key, hashed_key)