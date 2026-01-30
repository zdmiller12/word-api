## NYT-S cookie refresh

This service can refresh the `NYT-S` cookie and write it to a local JSON file.

### Setup

1. Install dependencies (Playwright + Chromium):
   ```bash
   uv sync
   python -m playwright install chromium
   ```

2. (Optional) For automated Google login, set:
   ```bash
   export GOOGLE_EMAIL="you@example.com"
   export GOOGLE_PASSWORD="your-password"
   ```

### Run

Manual login (recommended for the first run):
```bash
python services/scraper/main.py nyt-cookie --headful --manual-login
```

Automated daily refresh (cron-friendly):
```bash
python services/scraper/main.py nyt-cookie
```

Outputs:
- `~/.config/word-api/nyt_cookie.json`
- `~/.config/word-api/nyt_storage_state.json`
