"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """AyurVani configuration."""

    # AWS
    aws_region: str = "us-east-1"
    s3_bucket: str = "ayurvani-data"
    dynamodb_table: str = "ayurvani-sessions"
    dynamodb_profiles_table: str = "ayurvani-user-profiles"
    opensearch_endpoint: str = ""

    # Nova model IDs
    nova_lite_model_id: str = "amazon.nova-lite-v1:0"
    nova_sonic_model_id: str = "amazon.nova-sonic-v1:0"
    nova_embed_model_id: str = "amazon.nova-embed-multimodal-v1:0"

    # App
    environment: str = "development"
    log_level: str = "info"
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    allowed_hosts: List[str] = ["*"]

    # Vector search
    embedding_dimension: int = 1024
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()