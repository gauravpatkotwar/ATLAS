import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.auth.domain.entities import User, Tenant, UserStatus, UserRole, Permission
from app.modules.auth.domain.repositories import UserRepository, TenantRepository
from app.core.security import create_token_pair, decode_token, verify_password, get_password_hash
from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    ValidationException,
    BusinessRuleException,
)


class TestUserEntity:
    """Test User domain entity"""

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
        assert user.has_any_role([UserRole.RECRUITER, UserRole.ADMIN])

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

    def test_user_permissions(self):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            roles=[UserRole.RECRUITER],
        )
        # RECRUITER should have CANDIDATES_READ permission
        assert Permission.CANDIDATES_READ in user.get_all_permissions()

    def test_user_lockout(self):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
        )
        # Record 5 failed logins (threshold is 5)
        for _ in range(5):
            user.record_failed_login()
        assert user.is_locked
        assert user.locked_until is not None

    def test_user_record_login_resets_lockout(self):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            failed_login_attempts=3,
            locked_until=datetime.utcnow() + timedelta(minutes=10),
        )
        user.record_login("127.0.0.1")
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.last_login_at is not None
        assert user.last_login_ip == "127.0.0.1"


class TestTenantEntity:
    """Test Tenant domain entity"""

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

    def test_tenant_subscription_limits(self):
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            max_users=10,
            max_jobs=50,
            max_candidates=1000,
        )
        assert tenant.max_users == 10
        assert tenant.max_jobs == 50
        assert tenant.max_candidates == 1000


class TestSecurity:
    """Test security utilities"""

    def test_password_hashing(self):
        password = "SecurePass123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2  # Different salts
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        assert not verify_password("wrong_password", hash1)

    def test_token_pair_creation(self):
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

    def test_token_decoding(self):
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
        assert "candidates:read" in payload.permissions

    def test_invalid_token_raises_exception(self):
        with pytest.raises(AuthenticationException):
            decode_token("invalid.token.string")

    def test_expired_token_raises_exception(self):
        # Create a token that expires immediately
        from datetime import timedelta
        token = create_token_pair(
            subject=str(uuid4()),
            tenant_id=str(uuid4()),
            email="test@example.com",
            roles=[],
            permissions=[],
            expires_delta=timedelta(seconds=-1),  # Already expired
        )
        # This tests the decode_token which checks exp
        # The token created above is already expired
        with pytest.raises(AuthenticationException):
            decode_token(token.access_token)


class TestExceptions:
    """Test custom exceptions"""

    def test_not_found_exception(self):
        exc = NotFoundException("User", uuid4())
        assert exc.status_code == 404
        assert "not found" in exc.detail.lower()

    def test_authentication_exception(self):
        exc = AuthenticationException("Invalid credentials")
        assert exc.status_code == 401
        assert exc.headers.get("WWW-Authenticate") == "Bearer"

    def test_authorization_exception(self):
        exc = AuthorizationException("Access denied")
        assert exc.status_code == 403

    def test_conflict_exception(self):
        exc = ConflictException("Resource already exists")
        assert exc.status_code == 409

    def test_validation_exception(self):
        exc = ValidationException("Validation failed", {"field": "error"})
        assert exc.status_code == 422
        assert exc.details.get("field") == "error"

    def test_business_rule_exception(self):
        exc = BusinessRuleException("Business rule violated", "RULE_VIOLATION")
        assert exc.status_code == 400
        assert exc.error_code == "RULE_VIOLATION"


class TestRepositoryPattern:
    """Test repository pattern implementation"""

    @pytest_asyncio.fixture
    async def mock_session(self):
        return AsyncMock()

    @pytest_asyncio.fixture
    def user_repo(self, mock_session):
        from app.domain.repositories import SQLAlchemyTenantRepository
        from app.modules.auth.domain.entities import User
        return SQLAlchemyTenantRepository(mock_session, User, uuid4())

    @pytest.mark.asyncio
    async def test_repository_add(self, user_repo, mock_session):
        user = User(
            tenant_id=uuid4(),
            email="test@example.com",
            password_hash="hash",
            first_name="John",
            last_name="Doe",
        )
        result = await user_repo.add(user)
        assert result == user
        mock_session.add.assert_called_once_with(user)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_get(self, user_repo, mock_session):
        user_id = uuid4()
        mock_user = MagicMock()
        mock_session.get.return_value = mock_user

        result = await user_repo.get(user_id)
        assert result == mock_user
        mock_session.get.assert_called_once_with(user_repo.model_class, user_id)

    @pytest.mark.asyncio
    async def test_repository_soft_delete(self, user_repo, mock_session):
        user_id = uuid4()
        mock_user = MagicMock()
        mock_user.is_deleted = False
        mock_session.get.return_value = mock_user

        result = await user_repo.soft_delete(user_id)
        assert result is True
        assert mock_user.deleted_at is not None

    @pytest.mark.asyncio
    async def test_repository_list_with_filters(self, user_repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [MagicMock(), MagicMock()]
        mock_session.execute.return_value = mock_result

        result = await user_repo.list(filters={"status": "active"}, limit=10, offset=0)
        assert len(result) == 2
        mock_session.execute.assert_called_once()


# Pytest fixtures
@pytest.fixture
def sample_user():
    return User(
        tenant_id=uuid4(),
        email="test@example.com",
        password_hash=get_password_hash("SecurePass123!"),
        first_name="John",
        last_name="Doe",
        roles=[UserRole.RECRUITER],
    )


@pytest.fixture
def sample_tenant():
    return Tenant(
        name="Test Company",
        slug="test-company",
        subscription_plan="professional",
    )