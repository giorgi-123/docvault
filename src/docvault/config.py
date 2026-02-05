from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/postgres"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256" # we could use HS512 which would be more secure but trade-off is performance
    access_token_expire_minutes: int = 30

settings = Settings()
    