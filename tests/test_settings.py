"""Tests for settings module."""

from __future__ import annotations

import os
from unittest.mock import patch

from pydantic import ValidationError
import pytest

from src.settings import Settings, get_settings


class TestSettings:
    """Test Settings class."""

    def test_settings_with_all_required_fields(self):
        """Test Settings initialization with all required fields."""
        with patch.dict(
            os.environ,
            {
                "SHEETS_ID": "test_sheet_id",
                "GOOGLE_SERVICE_ACCOUNT_JSON": "/path/to/credentials.json",
            },
            clear=True,
        ):
            # Use _env_file parameter to disable reading .env file
            settings = Settings(_env_file=None)
            assert settings.sheets_id == "test_sheet_id"
            assert settings.google_service_account_json == "/path/to/credentials.json"
            assert settings.sheet_name == "Feuille 1"  # Default value
            assert settings.lbc_storage_state == "./.state/lbc_storage.json"  # Default
            assert settings.lbc_headless is False  # Default

    def test_settings_with_custom_values(self):
        """Test Settings with custom values."""
        with patch.dict(
            os.environ,
            {
                "SHEETS_ID": "custom_id",
                "GOOGLE_SERVICE_ACCOUNT_JSON": "/custom/path.json",
                "SHEET_NAME": "Custom Sheet",
                "LBC_STORAGE_STATE": "/custom/storage.json",
                "LBC_HEADLESS": "true",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            assert settings.sheets_id == "custom_id"
            assert settings.sheet_name == "Custom Sheet"
            assert settings.lbc_storage_state == "/custom/storage.json"
            assert settings.lbc_headless is True

    def test_settings_missing_required_field(self):
        """Test Settings fails with missing required field."""
        with patch.dict(os.environ, {"SHEETS_ID": "test"}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
            assert "google_service_account_json" in str(exc_info.value)

    def test_settings_ignores_extra_keys(self):
        """Test Settings ignores extra keys in environment."""
        with patch.dict(
            os.environ,
            {
                "SHEETS_ID": "test_id",
                "GOOGLE_SERVICE_ACCOUNT_JSON": "/path/to/creds.json",
                "EXTRA_KEY": "should_be_ignored",
                "ANOTHER_RANDOM_KEY": "also_ignored",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            assert settings.sheets_id == "test_id"
            assert not hasattr(settings, "extra_key")
            assert not hasattr(settings, "another_random_key")

    def test_settings_boolean_parsing(self):
        """Test boolean parsing for lbc_headless."""
        test_cases = [
            ("true", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("off", False),
        ]

        for value, expected in test_cases:
            with patch.dict(
                os.environ,
                {
                    "SHEETS_ID": "test",
                    "GOOGLE_SERVICE_ACCOUNT_JSON": "/path.json",
                    "LBC_HEADLESS": value,
                },
                clear=True,
            ):
                settings = Settings(_env_file=None)
                assert settings.lbc_headless is expected

    def test_settings_case_insensitive(self):
        """Test case insensitivity of environment variables."""
        with patch.dict(
            os.environ,
            {
                "sheets_id": "test_lower",  # lowercase
                "GOOGLE_SERVICE_ACCOUNT_JSON": "/path.json",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            assert settings.sheets_id == "test_lower"


class TestGetSettings:
    """Test get_settings function."""

    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns the same instance."""
        # Reset the global settings
        import src.settings

        src.settings._settings = None

        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
        assert isinstance(settings1, Settings)
