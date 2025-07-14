from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    FERNET_KEY: str
    BOT_TOKEN: str
    model_config = SettingsConfigDict(env_file=".env")
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "notification_db"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()

