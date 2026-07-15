from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "ATLAS Enterprise AI Recruiting Platform"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(
        default="SUPER_SECRET_SECURITY_KEY_DO_NOT_USE_IN_PRODUCTION",
        validation_alias="SECRET_KEY",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./atlas.db", validation_alias="DATABASE_URL"
    )

    # AI Layer
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL"
    )
    AI_PROVIDER: str = Field(default="ollama", validation_alias="AI_PROVIDER")

    # Models mapping
    MODEL_RESUME_EXTRACTION: str = Field(
        default="phi4-mini", validation_alias="MODEL_RESUME_EXTRACTION"
    )
    MODEL_RECRUITER_CHAT: str = Field(
        default="qwen3:8b", validation_alias="MODEL_RECRUITER_CHAT"
    )
    MODEL_RECOMMENDATION_EXPLANATION: str = Field(
        default="qwen3:8b", validation_alias="MODEL_RECOMMENDATION_EXPLANATION"
    )
    MODEL_RESUME_SUMMARY: str = Field(
        default="phi4-mini", validation_alias="MODEL_RESUME_SUMMARY"
    )
    MODEL_EMBEDDINGS: str = Field(
        default="nomic-embed-text", validation_alias="MODEL_EMBEDDINGS"
    )

    # Storage and Vector Search
    UPLOAD_DIR: str = Field(default="uploads", validation_alias="UPLOAD_DIR")
    FAISS_INDEX_PATH: str = Field(
        default="vector_index.faiss", validation_alias="FAISS_INDEX_PATH"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
