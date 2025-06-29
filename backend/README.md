# SmartBot Backend

## Overview
SmartBot is an automation backend for OTT streaming detection, IP rotation, and device management. It is designed to work with a web dashboard and supports Playwright-based OTT checks, simulated device/IP rotation, caching, and robust logging. This backend is modular and ready for integration with a dashboard, Telegram alerts, and more.

## Features
- Configurable via `config.json`
- Playwright-based OTT streaming checks (Hotstar, SonyLIV, Zee5, etc.)
- Simulated device/SIM management and IP rotation (for Windows)
- Caching of good/bad IPs
- Fallback to last-known-good IP
- Screenshot capture for each OTT check
- Robust logging to file
- Ready for dashboard/API integration

## Requirements
- Python 3.12+
- pip
- Playwright (`pip install playwright` and `python -m playwright install`)
- requests

## Setup Instructions
1. Clone/download the repository.
2. Navigate to the `backend` directory:
   ```bash
   cd smartbot/backend
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m playwright install
   ```
4. Edit `config.json` to set your paths and OTT services.

## Example `config.json`
```json
{
  "paths": {
    "log": "smartbot.log",
    "screenshots": "screenshots",
    "ipcache": "ip_cache.json"
  },
  "ott_services": {
    "hotstar": "https://www.hotstar.com",
    "sonyliv": "https://www.sonyliv.com",
    "zee5": "https://www.zee5.com"
  },
  "loop_interval": 60
}
```

## Usage
Run the backend with:
```bash
python smartbot.py
```

## How to Check/Test the Backend
- The backend will log all actions to `smartbot.log`.
- Screenshots for each OTT check will be saved in the `screenshots` directory.
- Good/bad IPs are cached in `ip_cache.json`.
- The backend will rotate through simulated IPs and retry on failures.
- To test, check:
  - The log file for status and errors
  - The screenshots directory for captured images
  - The cache file for IP status

## Next Steps
- Integrate with a web dashboard (Flask API)
- Add Telegram alerts and command polling
- Add real device/SIM management for Linux
- Add SQLite logging and advanced error handling

---
For any issues or questions, please contact the developer.
