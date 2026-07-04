from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    llm_provider: str = "fake"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/briefs"

settings = Settings()
