from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/docvaultDB"
    test_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5435/docvaultDB_test"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256" # we could use HS512 which would be more secure but trade-off is performance
    access_token_expire_minutes: int = 30
    s3_endpoint: str | None = "http://localhost:4566"
    bucket_name: str | None = "demo-bucket-name"
    aws_region_name: str = "eu-north-1"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"

settings = Settings()
    