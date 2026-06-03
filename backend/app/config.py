import warnings
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "GWEB_", "env_file": ".env"}

    # App
    debug: bool = False
    secret_key: str = "dev-secret-change-in-production"

    @model_validator(mode="after")
    def validate_secret_key(self):
        if self.secret_key == "dev-secret-change-in-production":
            warnings.warn("Using default GWEB_SECRET_KEY — set GWEB_SECRET_KEY in production!", stacklevel=2)
        return self

    # Database
    database_url: str = "postgresql+asyncpg://gweb:gweb@localhost:5432/gweb"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "gweb-media"
    minio_secure: bool = False

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "gweb_knowledge"

    # LLM mock mode (for testing only)
    llm_mock: str = ""

    # LLM defaults
    llm_provider: str = "deepseek"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    embedding_provider: str = "openai"
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"


settings = Settings()
