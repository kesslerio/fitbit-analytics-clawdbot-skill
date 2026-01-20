# Fitbit Analytics Skill for Clawdbot 🦞

Fitbit health and fitness data integration for Clawdbot. Fetch steps, heart rate, sleep, activity, calories, and trends from Fitbit Web API. Generate automated health reports, correlations, and alerts.

## Features

- **Activity Tracking**: Fetch daily steps, distance, calories, and active minutes.
- **Heart Rate**: Access continuous heart rate data and resting heart rate trends.
- **Sleep Analytics**: Analyze sleep stages (Deep, Light, REM, Wake) and efficiency.
- **Reports**: Generate daily/weekly health reports with trend analysis.
- **Automation**: Scripts ready for cron jobs (e.g., daily summaries).

## Setup

### 1. Create a Fitbit Developer App
1.  Go to [dev.fitbit.com/apps](https://dev.fitbit.com/apps) and log in.
2.  Click **"Register an App"**.
3.  Fill in the details:
    *   **Application Name:** `Niemand Assistant` (or your choice)
    *   **Description:** `Personal AI analytics.`
    *   **OAuth 2.0 Application Type:** `Personal`
    *   **Redirect URL:** `http://localhost:8080/`
    *   **Default Access Type:** `Read & Write`
4.  **Save** and note your **Client ID** and **Client Secret**.

### 2. Configure Credentials
Add keys to your `secrets.conf` or environment variables:
```bash
export FITBIT_CLIENT_ID="YOUR_CLIENT_ID"
export FITBIT_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

### 3. Authorization Flow
1.  Construct the URL:
    ```
    https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800
    ```
2.  Authorize in browser.
3.  Copy the `code` from the redirect URL (`http://localhost:8080/?code=...`).
4.  Exchange code for tokens:
    ```bash
    curl -X POST https://api.fitbit.com/oauth2/token \
      -u "CLIENT_ID:CLIENT_SECRET" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "grant_type=authorization_code" \
      -d "code=YOUR_CODE" \
      -d "redirect_uri=http://localhost:8080/"
    ```
5.  Save `access_token` and `refresh_token` to `FITBIT_ACCESS_TOKEN` and `FITBIT_REFRESH_TOKEN`.

## Usage

### Fetch Daily Stats
```bash
# Get steps for today
python scripts/fitbit_api.py steps --days 1

# Get sleep data
python scripts/fitbit_api.py sleep --days 1
```

### Generate Weekly Report
```bash
python scripts/fitbit_api.py report --type weekly
```

## Structure
- `scripts/fitbit_api.py`: Main API wrapper and CLI tool.
- `docs/`: Privacy Policy and Terms of Service.

## License
Apache 2.0
