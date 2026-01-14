from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra keys in .env
        case_sensitive=False,
    )

    # Google Sheets configuration
    sheets_id: str = Field(..., description="Google Sheets document ID")
    sheet_name: str = Field(
        default="Feuille 1", description="Name of the sheet to read from"
    )

    # Google Cloud authentication
    google_service_account_json: str = Field(
        ..., description="Path to Google service account credentials JSON file"
    )

    # Leboncoin configuration
    lbc_storage_state: str = Field(
        default="./.state/lbc_storage.json",
        description="Path to Playwright storage state for Leboncoin session",
    )
    lbc_headless: bool = Field(
        default=False, description="Run Playwright in headless mode"
    )


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
