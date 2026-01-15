# LBC Publisher

Automation tool to publish classified ads to Leboncoin from a Google Sheets inventory.

## Features

- 📊 Read product inventory from Google Sheets
- 📁 Download images from Google Drive
- 🤖 Automated ad publication on Leboncoin using Playwright
- 🛡️ **Advanced anti-detection** with Playwright-Stealth & Ghost Cursor
- 🖱️ **Realistic mouse movements** using Bézier curves (bypasses Datadome)
- 🔒 **Proxy support** for residential proxies (critical against IP detection)
- 📝 **Beautiful logging** with Loguru (colorized console + file rotation)
- ✅ Type-safe configuration with Pydantic Settings
- 🧪 Comprehensive unit tests
- 🪝 Git hooks for code quality (Ruff, Black, tests)

## Quick Start

## ⚠️ Important: Datadome Detection

Leboncoin uses **Datadome**, one of the most sophisticated anti-bot systems in 2026. This tool implements multiple bypass techniques, but **responsible use is critical**:

- ✅ Use your **real account** and legitimate content
- ✅ Limit volume (recommended: 2-5 ads per run)
- ✅ Use **residential proxies** (highly recommended)
- ✅ Respect delays and avoid patterns
- ❌ Do NOT mass-publish or abuse the system

**Note**: Even with all protections, detection is possible. See [ANTI_DETECTION.md](ANTI_DETECTION.md) for detailed strategies.

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Google Cloud service account with Sheets and Drive access
- Leboncoin account
- (Recommended) Residential proxy service (e.g., Smartproxy, Bright Data)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd lbc-publisher

# Install dependencies
uv sync

# Install Git hooks
bash .githooks/install.sh

# Install Playwright browsers (Chrome for better TLS fingerprint)
uv run playwright install chrome
```

### Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure your environment variables:
   ```env
   # Google Sheets & Drive
   SHEETS_ID=your_google_sheets_id
   GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
   SHEET_NAME=Feuille 1

   # Leboncoin Configuration
   LBC_STORAGE_STATE=./.state/lbc_storage.json
   LBC_HEADLESS=false
   LBC_DELAY_MIN=8          # Increase if detected (recommended: 8-15)
   LBC_DELAY_MAX=15
   LBC_MAX_ADS_PER_RUN=2    # Start conservatively

   # Proxy (HIGHLY RECOMMENDED to avoid IP detection)
   PROXY_SERVER=http://gate.smartproxy.com:7000
   PROXY_USERNAME=your_username
   PROXY_PASSWORD=your_password
   ```

   **Proxy Configuration** (Strongly Recommended):
   - Datadome detects datacenter IPs and VPNs instantly
   - Use residential proxies for best results (90%+ success rate)
   - **Recommended**: Smartproxy (~15€ for 2GB = 300 ads) - See [SMARTPROXY_SETUP.md](SMARTPROXY_SETUP.md) for setup guide
   - See [ANTI_DETECTION.md](ANTI_DETECTION.md#1-critique--proxies-résidentiels) for other provider options

   **Conservative Settings** (if experiencing detection):
   - Increase delays: `LBC_DELAY_MIN=8`, `LBC_DELAY_MAX=15`
   - Reduce volume: `LBC_MAX_ADS_PER_RUN=2`
   - Wait 24-48h between runs if IP is flagged

### Usage

```bash
uv run python -m src.main
```

On first run, you'll need to log in to Leboncoin manually (the browser will pause automatically).

## 🛡️ Anti-Detection Features

This tool implements **14 sophisticated techniques** to bypass Datadome's bot detection:

### Key Technologies

1. **Playwright-Stealth**
   - Masks 200+ automation signals
   - Patches `navigator.webdriver`, CDP commands, browser fingerprints
   - Essential for avoiding JavaScript-based detection

2. **Ghost Cursor (Bézier Curves)**
   - Ultra-realistic mouse movements using mathematical Bézier curves
   - Variable speed and natural acceleration
   - Bypasses Datadome's real-time trajectory analysis
   - **Critical**: Addresses "superhuman clicking speed" detection

3. **Proxy Support**
   - Optional residential proxy configuration
   - Bypasses IP-based detection and datacenter flagging
   - **Strongly recommended** for production use

4. **Chrome Browser (Better TLS Fingerprint)**
   - Uses Chrome instead of Chromium for realistic JA3 fingerprint
   - Bypasses TLS fingerprinting detection
   - Combined with proxies for maximum effectiveness

5. **Additional Protections**
   - Character-by-character typing (80-200ms delays)
   - Random scrolling and mouse movements
   - Rate limiting and human-like delays
   - French locale, timezone, and geolocation
   - Session persistence

### Detection Indicators

If you see these messages, you've been detected:
- ❌ "Comportement du navigateur nous a intrigué"
- ❌ CAPTCHA challenges
- ❌ "Trop de tentatives, réessayez plus tard"

**Actions**:
1. Stop immediately and wait 24-48h
2. Configure a residential proxy
3. Increase delays significantly
4. Reduce `LBC_MAX_ADS_PER_RUN` to 2

### Documentation

For comprehensive anti-detection strategies, see:
- **[ANTI_DETECTION.md](ANTI_DETECTION.md)**: Complete guide with 14 techniques
- Datadome analysis and ML detection patterns
- Proxy provider recommendations and pricing
- Configuration examples and troubleshooting

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
│   ├── logger.py       # Loguru logging configuration
│   └── lbc.py          # Leboncoin automation with anti-detection
├── tests/              # Unit tests
├── .githooks/          # Git hooks for code quality
├── ANTI_DETECTION.md   # Anti-Datadome strategies (14 techniques)
├── SMARTPROXY_SETUP.md # Smartproxy configuration guide (recommended)
├── CLAUDE.md           # AI assistant documentation
└── README.md           # This file
```

## Documentation

- **[SMARTPROXY_SETUP.md](SMARTPROXY_SETUP.md)**: Step-by-step Smartproxy setup guide (recommended for production)
- **[ANTI_DETECTION.md](ANTI_DETECTION.md)**: Comprehensive anti-Datadome strategies and techniques
- **[CLAUDE.md](CLAUDE.md)**: Detailed architecture and implementation notes for AI assistants
- **[.githooks/README.md](.githooks/README.md)**: Git hooks documentation

## License

[Your License Here]