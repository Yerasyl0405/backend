"""
Application Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./rag.db"
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    VECTOR_DB_HOST: str = "localhost"
    VECTOR_DB_PORT: int = 6333
    VECTOR_DB_COLLECTION_NAME: str = "documents"
    EMBEDDING_DIM: int = 1536


settings = Settings()
