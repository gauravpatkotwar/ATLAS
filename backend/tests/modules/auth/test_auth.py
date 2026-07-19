import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from app.modules.auth.domain.entities import User, Tenant, UserStatus, UserRole
from app.modules.auth.domain.repositories import UserRepository, TenantRepository
from app.core.security import create_token_pair, decode_token, verify_password, get_password_hash
from app.core.exceptions import AuthenticationException, AuthorizationException, NotFoundException


class TestUserEntity:
    def test_user_creation(self):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
        )
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.full_name == "John Doe"
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.is_active is False

    def test_user_roles_and_permissions(self):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            roles=[UserRole.RECRUITER],
        )
        assert user.has_role(UserRole.RECRUITER)
        assert not user.has_role(UserRole.ADMIN)

    def test_user_add_remove_role(self):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
        )
        user.add_role(UserRole.RECRUITER)
        assert UserRole.RECRUITER in user.roles
        
        user.remove_role(UserRole.RECRUITER)
        assert UserRole.RECRUITER not in user.roles

    def test_user_password_verification(self):
        password = "SecurePass123!"
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash=get_password_hash(password),
            first_name="John",
            last_name="Doe",
        )
        assert verify_password(password, user.password_hash)
        assert not verify_password("wrong_password", user.password_hash)

    def test_user_lockout(self):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash=get_password_hash("password"),
            first_name="John",
            last_name="Doe",
        )
        for _ in range(5):
            user.record_failed_login()
        assert user.is_locked
        assert user.locked_until is not None

    def test_user_record_login(self):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash=get_password_hash("password"),
            first_name="John",
            last_name="Doe",
            failed_login_attempts=3,
            locked_until=datetime.utcnow() + timedelta(minutes=10),
        )
        user.record_login("127.0.0.1")
        assert user.last_login_at is not None
        assert user.last_login_ip == "127.0.0.1"
        assert user.failed_login_attempts == 0
        assert user.locked_until is None


class TestTenantEntity:
    def test_tenant_creation(self):
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
        )
        assert tenant.id is not None
        assert tenant.name == "Test Company"
        assert tenant.slug == "test-company"
        assert tenant.is_active is True
        assert tenant.subscription_plan == "free"


class TestSecurity:
    def test_create_token_pair(self):
        token_pair = create_token_pair(
            subject=str(uuid4()),
            tenant_id=str(uuid4()),
            email="test@example.com",
            roles=["recruiter"],
            permissions=["candidates:read"],
        )
        assert token_pair.access_token
        assert token_pair.refresh_token
        assert token_pair.token_type == "bearer"
        assert token_pair.expires_in > 0

    def test_decode_token(self):
        token_pair = create_token_pair(
            subject=str(uuid4()),
            tenant_id=str(uuid4()),
            email="test@example.com",
            roles=["recruiter"],
            permissions=["candidates:read"],
        )
        payload = decode_token(token_pair.access_token)
        assert payload.sub
        assert payload.tenant_id
        assert payload.email == "test@example.com"
        assert "recruiter" in payload.roles

    def test_invalid_token(self):
        with pytest.raises(AuthenticationException):
            decode_token("invalid.token.string")

    def test_password_hashing(self):
        password = "SecurePass123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2  # Different salts
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        assert not verify_password("wrong", hash1)


class TestExceptions:
    def test_not_found_exception(self):
        exc = NotFoundException("User", uuid4())
        assert exc.status_code == 404
        assert "not found" in exc.detail.lower()

    def test_authentication_exception(self):
        exc = AuthenticationException("Invalid credentials")
        assert exc.status_code == 401
        assert "WWW-Authenticate" in exc.headers

    def test_authorization_exception(self):
        exc = AuthorizationException("Access denied")
        assert exc.status_code == 403

    def test_conflict_exception(self):
        exc = ConflictException("Resource already exists")
        assert exc.status_code == 409

    def test_business_rule_exception(self):
        exc = BusinessRuleException("Business rule violated")
        assert exc.status_code == 400


class TestTokenPayload:
    def test_token_payload_creation(self):
        from app.core.security import TokenPayload
        payload = TokenPayload(
            sub=str(uuid4()),
            tenant_id=str(uuid4()),
            email="test@example.com",
            roles=["recruiter"],
            permissions=["candidates:read"],
            type="access",
            iat=int(datetime.utcnow().timestamp()),
            exp=int((datetime.utcnow() + timedelta(minutes=15)).timestamp()),
            jti=str(uuid4()),
        )
        assert payload.sub
        assert payload.tenant_id
        assert payload.type == "access"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])