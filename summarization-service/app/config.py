from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    KAFKA_HOST: str
    KAFKA_PORT: int

    GIGACHAT_AUTH_KEY: str

    SSL_CERT_FILE: str

    @property
    def kafka_bootstrap_servers(self) -> str:
        return f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"


settings = Settings()
