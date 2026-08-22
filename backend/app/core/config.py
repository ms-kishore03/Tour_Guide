from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.secrets import load_secrets_into_env

load_secrets_into_env()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # external services (shared with the legacy Streamlit app's .env)
    groq_api_key: str = ""
    gemini_api_key: str = ""
    mongodb_uri: str = "mongodb://localhost:27017"
    accomodation_api_key: str = ""
    openweathermap_api_key: str = ""
    geoapify_api_key: str = ""
    serpapi_api_key: str = ""

    # auth
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    # cors
    cors_origins: list[str] = ["http://localhost:5173"]

    # observability
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "tour-guide-backend"

    mongo_db_name: str = "Tour_Guide"


@lru_cache
def get_settings() -> Settings:
    return Settings()
