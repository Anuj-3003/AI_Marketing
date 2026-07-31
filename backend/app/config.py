from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_REPO_ROOT / ".env"), extra="ignore")

    database_url: str = "sqlite:///./app.db"

    openrouter_api_key: str = ""
    openrouter_competitor_model: str = "perplexity/sonar-pro"
    openrouter_copy_model: str = "openai/gpt-5"
    openrouter_image_model: str = "google/gemini-2.5-flash-image"

    adyntel_api_key: str = ""
    adyntel_email: str = ""
    adyntel_country_code: str = "US"

    max_ads_per_source: int = 25

    google_ads_developer_token: str = ""
    google_ads_client_id: str = ""
    google_ads_client_secret: str = ""
    google_ads_refresh_token: str = ""
    google_ads_login_customer_id: str = ""


settings = Settings()
