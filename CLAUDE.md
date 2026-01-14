# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation tool that publishes classified ads to Leboncoin (French marketplace) from a Google Sheets inventory. It reads product data from a Google Sheet, downloads images from Google Drive, and automatically creates ads on Leboncoin using Playwright browser automation.

## Development Commands

**Package Management:**
This project uses `uv` for dependency management.

```bash
# To add a new dependency
uv add <package-name>

# Install dependencies
uv sync

# Install with dev dependencies
uv sync --all-groups

# Run the main script
uv run python -m src.main
```

**Code Quality:**

```bash
# Format code with Black
uv run black src/

# Lint with Ruff (auto-fixes enabled)
uv run ruff check src/

# Run both
uv run ruff check src/ && uv run black src/
```

**Testing:**

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_<name>.py

# Run with verbose output
uv run pytest -v
```

## Architecture

### Data Flow

1. **Sheet Reading (`sheet.py`)**: Reads inventory from Google Sheets using service account credentials
2. **Data Filtering**: Identifies rows marked for publication (via `should_publish()` method)
3. **Image Handling (`drive.py`)**: Downloads images from Google Drive folders
4. **Ad Publishing (`lbc.py`)**: Uses Playwright to automate Leboncoin form submission
5. **Status Updates**: Updates the Google Sheet with published ad URLs or error messages

### Module Responsibilities

- **`models.py`**: Data models (`SheetRow`, `AdPayload`) and business logic (price parsing, title/description building)
- **`sheet.py`**: Google Sheets API integration for reading rows and updating cells
- **`drive.py`**: Google Drive API integration for folder ID extraction, image listing, and downloads
- **`lbc.py`**: Playwright automation for Leboncoin ad submission
- **`main.py`**: Orchestration layer that ties all components together
- **`settings.py`**: Pydantic Settings-based configuration with validation and defaults

### Configuration Management

The project uses **Pydantic Settings** for configuration management. All settings are defined in `src/settings.py` and loaded from environment variables or a `.env` file.

**Key features:**
- Type-safe configuration with validation
- Automatic loading from `.env` file
- Default values for optional settings
- `extra="ignore"` allows additional keys in `.env` without errors
- `case_sensitive=False` for flexible environment variable naming

**Settings access:**
```python
from src.settings import get_settings

settings = get_settings()  # Singleton pattern
print(settings.sheets_id)
```

### Authentication

The project requires two Google Cloud credentials:
- **Service Account JSON**: Set via `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable
- **Scopes**: `spreadsheets` and `drive.readonly`

Leboncoin authentication uses Playwright's `storage_state` to persist login sessions.

### Environment Variables

Required in `.env` file:
- `SHEETS_ID`: Google Sheets document ID (required)
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Path to service account credentials (required)
- `SHEET_NAME`: Sheet name (optional, defaults to "Feuille 1")
- `LBC_STORAGE_STATE`: Playwright session storage path (optional, defaults to "./.state/lbc_storage.json")
- `LBC_HEADLESS`: Run browser in headless mode (optional, defaults to false)

See `.env.example` for a complete template.

### Google Sheets Schema

The expected column headers are defined in `sheet.py:HEADERS`:
- Annonce LBC (custom title)
- Lien de l'annonce (published URL, populated by script)
- Photos, Dossier photos (Drive folder URL)
- Catégorie, Pièces, Objet, Marques, Modèle, Quantité, État
- Prix neuf à l'unité, Prix total, Prix demandé à l'unité, Prix total demandé
- Status (updated to "PUBLISHED" or "ERROR: ...")
- A publier (flag: "oui"/"true"/"1"/"x"/"yes")

### Playwright Automation Notes

- **Selectors**: Uses role-based and label-based selectors for robustness
- **Login**: First run requires manual login via `page.pause()` if not authenticated
- **Session Persistence**: Storage state saved to `./.state/lbc_storage.json`
- **Headless Mode**: Bot detection may occur; use `headless=false` for initial runs
- **Selector Updates**: Leboncoin changes UI frequently; update selectors in `lbc.py:_fill_form()` and `_submit_and_get_url()` as needed

### Error Handling

Errors during ad publication are caught and written to the Google Sheet's "Status" column (truncated to 120 chars). The script continues processing remaining rows after errors.

## Important Implementation Details

### Price Parsing

`parse_eur_amount()` handles French number formatting (comma as decimal separator, spaces/non-breaking spaces). Returns integer euros, not cents.

### Title/Description Building

- Title: Uses "Annonce LBC" column if present, otherwise auto-generates from Objet + Marques + Modèle (max 70 chars)
- Description: Structured format with all product metadata, filters out empty/dash values

### Image Handling

- Maximum 10 images per ad (enforced in `main.py:42`)
- Images sorted alphabetically by filename
- Downloaded to temporary directory, cleaned up automatically after publication
- Requires Drive folder URL in "Dossier photos" column

### Publication Logic

Row is published when:
- "A publier" = "oui"/"true"/"1"/"x"/"yes" (case-insensitive)
- "Status" = "en vente" or empty
- "Lien de l'annonce" is empty

Implemented in `models.py:SheetRow.should_publish()`