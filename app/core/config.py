from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Set
import os

# Allowed image content types for the /evaluate endpoint
ALLOWED_IMAGE_TYPES: Set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

# Maximum file size for image uploads (in bytes)
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    FIREBASE_PROJECT_ID: str = Field(default="", env="FIREBASE_PROJECT_ID")
    FIREBASE_SERVICE_ACCOUNT_KEY: str = Field(default="", env="FIREBASE_SERVICE_ACCOUNT_KEY")
    FAISS_INDEX_PATH: str = Field(default="./data/knowledge_base.index", env="FAISS_INDEX_PATH")
    VECTOR_STORE_PATH: str = Field(default="./data/vector_store", env="VECTOR_STORE_PATH")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
