# LBC Publisher

Automation tool to publish classified ads to Leboncoin from a Google Sheets inventory.

## Features

- 📊 Read product inventory from Google Sheets
- 📁 Download images from Google Drive
- 🤖 Automated ad publication on Leboncoin using Playwright
- ✅ Type-safe configuration with Pydantic Settings
- 🧪 Comprehensive unit tests
- 🪝 Git hooks for code quality (Ruff, Black, tests)

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Google Cloud service account with Sheets and Drive access
- Leboncoin account

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd lbc-publisher

# Install dependencies
uv sync

# Install Git hooks
bash .githooks/install.sh

# Install Playwright browsers
uv run playwright install chromium
```

### Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure your environment variables:
   ```env
   SHEETS_ID=your_google_sheets_id
   GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
   SHEET_NAME=Feuille 1
   LBC_STORAGE_STATE=./.state/lbc_storage.json
   LBC_HEADLESS=false
   ```

### Usage

```bash
uv run python -m src.main
```

On first run, you'll need to log in to Leboncoin manually (the browser will pause automatically).

## Development

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/ --fix

# Run tests
uv run pytest -v
```

### Git Hooks

Hooks are automatically enforced after installation:

- **pre-commit**: Runs Ruff and Black with auto-fix
- **pre-push**: Runs all tests before pushing

See `.githooks/README.md` for details.

## Project Structure

```
lbc-publisher/
├── src/
│   ├── main.py         # Main orchestration
│   ├── settings.py     # Pydantic Settings configuration
│   ├── models.py       # Data models and business logic
│   ├── sheet.py        # Google Sheets integration
│   ├── drive.py        # Google Drive integration
│   └── lbc.py          # Leboncoin automation
├── tests/              # Unit tests
├── .githooks/          # Git hooks for code quality
├── CLAUDE.md          # AI assistant documentation
└── README.md          # This file
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)**: Detailed architecture and implementation notes for AI assistants
- **[.githooks/README.md](.githooks/README.md)**: Git hooks documentation

## License

[Your License Here]