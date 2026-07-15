import datetime
import logging
from typing import Optional, Dict, Any
import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from atlas.config.settings import settings
from atlas.database.models import User, Tenant
from atlas.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Service handling registration, password authentication, and JWT authorization for multi-tenant SaaS."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes raw password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies plain password against stored hash."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    def create_access_token(
        self, data: dict, expires_delta: Optional[datetime.timedelta] = None
    ) -> str:
        """Generates access token payload and signs with config Secret."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
        else:
            expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": int(expire.timestamp())})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Parses JWT token, returning content payload or None if invalid."""
        try:
            return jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.PyJWTError as e:
            logger.debug(f"JWT Token decode failed: {e}")
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Validates credentials, returning User if match, else None."""
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def register_user(
        self,
        email: str,
        password: str,
        role: str = "recruiter",
        org_name: Optional[str] = None,
        invite_code: Optional[str] = None,
    ) -> User:
        """Registers a user globally and binds them to a new or existing Tenant organization."""
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError(f"Email {email} is already registered.")

        tenant: Optional[Tenant] = None

        if org_name:
            # Create a brand new tenant organization on Free tier
            tenant = Tenant(name=org_name, subscription_tier="free")
            self.db.add(tenant)
            await self.db.commit()
            await self.db.refresh(tenant)
            logger.info(
                f"Created new Tenant organization '{org_name}' with invite code '{tenant.invite_code}'"
            )
        elif invite_code:
            # Resolve existing tenant by invite code
            result = await self.db.execute(
                select(Tenant).filter(Tenant.invite_code == invite_code.strip().upper())
            )
            tenant = result.scalars().first()
            if not tenant:
                raise ValueError(
                    "Invalid invitation code. Organization workspace not found."
                )
            logger.info(f"Began mapping user {email} to existing Tenant: {tenant.name}")
        else:
            raise ValueError(
                "Authentication context missing: either 'org_name' or 'invite_code' must be provided."
            )

        hashed_password = self.hash_password(password)
        new_user = User(
            tenant_id=tenant.id,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=True,
        )

        # User repo links user to db
        return await self.repo.create(new_user)
