from typing import Any
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}


class ValidationException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            context=context,
        )


class AuthenticationException(AppException):
    def __init__(self, detail: str = "Authentication failed", context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="AUTHENTICATION_ERROR",
            context=context,
        )


class AuthorizationException(AppException):
    def __init__(self, detail: str = "Insufficient permissions", context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR",
            context=context,
        )


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: str | int, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' not found",
            error_code="NOT_FOUND",
            context={"resource": resource, "identifier": str(identifier), **(context or {})},
        )


class ConflictException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
            context=context,
        )


class BusinessRuleException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BUSINESS_RULE_VIOLATION",
            context=context,
        )


class RateLimitException(AppException):
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)},
            error_code="RATE_LIMIT_EXCEEDED",
            context={"retry_after": retry_after},
        )


class ExternalServiceException(AppException):
    def __init__(self, service: str, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External service error ({service}): {detail}",
            error_code="EXTERNAL_SERVICE_ERROR",
            context={"service": service, **(context or {})},
        )


class ConfigurationException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CONFIGURATION_ERROR",
            context=context,
        )


class DatabaseException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}",
            error_code="DATABASE_ERROR",
            context=context,
        )


class TenantNotFoundException(NotFoundException):
    def __init__(self, tenant_id: str):
        super().__init__("Tenant", tenant_id)


class TenantInactiveException(BusinessRuleException):
    def __init__(self, tenant_id: str):
        super().__init__(f"Tenant {tenant_id} is inactive", {"tenant_id": tenant_id})


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: str):
        super().__init__("User", user_id)


class UserInactiveException(BusinessRuleException):
    def __init__(self, user_id: str):
        super().__init__(f"User {user_id} is inactive", {"user_id": user_id})


class CandidateNotFoundException(NotFoundException):
    def __init__(self, candidate_id: str):
        super().__init__("Candidate", candidate_id)


class JobNotFoundException(NotFoundException):
    def __init__(self, job_id: str):
        super().__init__("Job", job_id)


class JobNotPublishedException(BusinessRuleException):
    def __init__(self, job_id: str):
        super().__init__(f"Job {job_id} is not published", {"job_id": job_id})


class PipelineStageNotFoundException(NotFoundException):
    def __init__(self, stage_id: str):
        super().__init__("PipelineStage", stage_id)


class InterviewNotFoundException(NotFoundException):
    def __init__(self, interview_id: str):
        super().__init__("Interview", interview_id)


class WorkflowNotFoundException(NotFoundException):
    def __init__(self, workflow_id: str):
        super().__init__("Workflow", workflow_id)


class WorkflowExecutionNotFoundException(NotFoundException):
    def __init__(self, execution_id: str):
        super().__init__("WorkflowExecution", execution_id)


class AIProviderException(ExternalServiceException):
    def __init__(self, provider: str, detail: str, context: dict[str, Any] | None = None):
        super().__init__(provider, detail, {"provider": provider, **(context or {})})


class EmbeddingException(AIProviderException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__("embedding", detail, context)


class CompletionException(AIProviderException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__("completion", detail, context)


class VectorSearchException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector search error: {detail}",
            error_code="VECTOR_SEARCH_ERROR",
            context=context,
        )


class FileStorageException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File storage error: {detail}",
            error_code="FILE_STORAGE_ERROR",
            context=context,
        )


class FileValidationException(ValidationException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(detail, context)


class WebhookException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook error: {detail}",
            error_code="WEBHOOK_ERROR",
            context=context,
        )


class WebhookSignatureException(AuthenticationException):
    def __init__(self, detail: str = "Invalid webhook signature"):
        super().__init__(detail)


class AuditLogException(AppException):
    def __init__(self, detail: str, context: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit log error: {detail}",
            error_code="AUDIT_LOG_ERROR",
            context=context,
        )