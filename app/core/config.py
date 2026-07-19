from functools import lru_cache
from typing import Annotated, Any, Literal
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "postgres"
    name: str = "atlas"
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    ssl_mode: Literal["disable", "allow", "prefer", "require"] = "prefer"

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

    host: str = "localhost"
    port: int = 6379
    username: str | None = None
    password: str | None = None
    db: int = 0
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    decode_responses: bool = True

    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        if self.username:
            auth = f"{self.username}:{self.password}@" if self.password else f"{self.username}@"
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_", extra="ignore")

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072
    max_tokens: int = 8192
    temperature: float = 0.1
    max_retries: int = 3
    timeout: int = 60
    embedding_batch_size: int = 100
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    whisper_model: str = "whisper-1"
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"


class VectorDBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VECTOR_DB_", extra="ignore")

    provider: Literal["pgvector", "pinecone", "weaviate", "qdrant"] = "pgvector"
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "postgres"
    database: str = "atlas"
    index_name: str = "atlas_embeddings"
    dimension: int = 3072
    metric: str = "cosine"
    pinecone_api_key: str | None = None
    pinecone_environment: str | None = None
    weaviate_url: str | None = None
    weaviate_api_key: str | None = None
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STORAGE_", extra="ignore")

    provider: Literal["s3", "gcs", "azure", "local"] = "s3"
    bucket: str = "atlas-uploads"
    region: str = "us-east-1"
    access_key: str | None = None
    secret_key: str | None = None
    endpoint_url: str | None = None
    cdn_url: str | None = None
    max_file_size: int = 50 * 1024 * 1024
    allowed_extensions: list[str] = [
        ".pdf", ".doc", ".docx", ".txt", ".rtf",
        ".jpg", ".jpeg", ".png", ".gif", ".webp",
        ".mp4", ".mov", ".avi", ".webm",
        ".mp3", ".wav", ".ogg", ".m4a",
    ]


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_", extra="ignore")

    provider: Literal["sendgrid", "ses", "smtp", "mailgun", "postmark"] = "sendgrid"
    from_email: str = "noreply@atlas.example.com"
    from_name: str = "ATLAS"
    sendgrid_api_key: str | None = None
    ses_region: str = "us-east-1"
    ses_access_key: str | None = None
    ses_secret_key: str | None = None
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    mailgun_domain: str | None = None
    mailgun_api_key: str | None = None
    postmark_token: str | None = None


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_", extra="ignore")

    secret_key: str = "change-me-in-production-min-32-chars"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    refresh_token_expire_days_remember: int = 90
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True
    bcrypt_rounds: int = 12
    jwt_issuer: str = "atlas"
    jwt_audience: str = "atlas-api"
    jwks_url: str | None = None
    private_key_path: str | None = None
    public_key_path: str | None = None
    mfa_issuer: str = "ATLAS"
    mfa_window: int = 1
    session_timeout_minutes: int = 60
    max_sessions_per_user: int = 5
    password_history_count: int = 5
    lockout_threshold: int = 5
    lockout_duration_minutes: int = 15


class CorsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CORS_", extra="ignore")

    allow_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    allow_origin_regex: str | None = None
    allow_credentials: bool = True
    allow_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    allow_headers: list[str] = ["*"]
    expose_headers: list[str] = ["*"]
    max_age: int = 600


class RateLimitSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RATE_LIMIT_", extra="ignore")

    enabled: bool = True
    default_limit: int = 100
    default_window: int = 60
    login_limit: int = 5
    login_window: int = 300
    register_limit: int = 3
    register_window: int = 3600
    api_limit: int = 1000
    api_window: int = 60
    ai_limit: int = 50
    ai_window: int = 60
    upload_limit: int = 10
    upload_window: int = 3600


class MonitoringSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MONITORING_", extra="ignore")

    enabled: bool = True
    sentry_dsn: str | None = None
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1
    sentry_profiles_sample_rate: float = 0.1
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    health_check_interval: int = 30
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"
    log_file: str | None = None
    log_max_size: int = 100 * 1024 * 1024
    log_backup_count: int = 10


class FeatureFlags(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEATURE_", extra="ignore")

    ai_recruiter: bool = True
    semantic_search: bool = True
    interview_intelligence: bool = True
    workflow_automation: bool = True
    analytics: bool = True
    enterprise_admin: bool = True
    video_interviews: bool = True
    voice_ai: bool = True
    semantic_search_embeddings: bool = True
    reranking: bool = True
    vector_search: bool = True
    workflow_builder: bool = True
    analytics_dashboard: bool = True
    enterprise_sso: bool = True
    audit_logs: bool = True
    webhooks: bool = True
    webhooks_retry: bool = True
    api_rate_limiting: bool = True
    api_versioning: bool = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    app_name: str = "ATLAS"
    app_version: str = "0.1.0"
    app_description: str = "AI-Powered Recruitment Operating System"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    openapi_url: str | None = "/openapi.json"

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    ai: AISettings = AISettings()
    vector_db: VectorDBSettings = VectorDBSettings()
    storage: StorageSettings = StorageSettings()
    email: EmailSettings = EmailSettings()
    auth: AuthSettings = AuthSettings()
    cors: CorsSettings = CorsSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    features: FeatureFlags = FeatureFlags()

    @field_validator("secret_key", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v == "change-me-in-production-min-32-chars" and cls.environment == "production":
            raise ValueError("Secret key must be changed in production")
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> Self:
        if self.environment == "production":
            if self.debug:
                raise ValueError("Debug must be False in production")
            if self.auth.secret_key == "change-me-in-production-min-32-chars":
                raise ValueError("Secret key must be changed in production")
            if not self.auth.private_key_path or not self.auth.public_key_path:
                raise ValueError("RSA keys must be configured in production")
            if self.monitoring.sentry_dsn is None:
                raise ValueError("Sentry DSN must be configured in production")
        return self

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()