from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    KAFKA_HOST: str
    KAFKA_PORT: int

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    GIGACHAT_AUTH_KEY: str
    GIGACHAT_CA_CERT_FILE: str

    @property
    def kafka_bootstrap_servers(self) -> str:
        return f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
