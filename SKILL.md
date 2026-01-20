---
name: fitbit-analytics
description: Fitbit health and fitness data integration. Fetch steps, heart rate, sleep, activity, calories, and trends from Fitbit Web API. Generate automated health reports and alerts.
---

# Fitbit Analytics

## Quick Start

```bash
# Set Fitbit API credentials
export FITBIT_CLIENT_ID="your_client_id"
export FITBIT_CLIENT_SECRET="your_client_secret"
export FITBIT_ACCESS_TOKEN="your_access_token"
export FITBIT_REFRESH_TOKEN="your_refresh_token"

# Fetch daily steps
python scripts/fitbit_api.py steps --days 7

# Get heart rate data
python scripts/fitbit_api.py heartrate --days 7

# Sleep summary
python scripts/fitbit_api.py sleep --days 7

# Generate weekly health report
python scripts/fitbit_api.py report --type weekly

# Get activity summary
python scripts/fitbit_api.py summary --days 7
```

## When to Use

Use this skill when:
- Fetching Fitbit metrics (steps, calories, heart rate, sleep)
- Analyzing activity trends over time
- Setting up alerts for inactivity or abnormal heart rate
- Generating daily/weekly health reports

## Core Workflows

### 1. Data Fetching (CLI)
```bash
# Available commands:
python scripts/fitbit_api.py steps --days 7
python scripts/fitbit_api.py calories --days 7
python scripts/fitbit_api.py heartrate --days 7
python scripts/fitbit_api.py sleep --days 7
python scripts/fitbit_api.py summary --days 7
python scripts/fitbit_api.py report --type weekly
```

### 2. Data Fetching (Python API)
```python
from fitbit_api import FitbitClient

client = FitbitClient()  # Uses env vars for credentials

# Fetch data (requires start_date and end_date)
steps_data = client.get_steps(start_date="2026-01-01", end_date="2026-01-16")
hr_data = client.get_heartrate(start_date="2026-01-01", end_date="2026-01-16")
sleep_data = client.get_sleep(start_date="2026-01-01", end_date="2026-01-16")
activity_summary = client.get_activity_summary(start_date="2026-01-01", end_date="2026-01-16")
```

### 3. Analysis
```python
from fitbit_api import FitbitAnalyzer

analyzer = FitbitAnalyzer(steps_data, hr_data)
summary = analyzer.summary()
# Returns: avg_steps, avg_resting_hr, step_trend
```

### 4. Alerts
```python
from alerts import FitbitAlerts

alerts = FitbitAlerts(thresholds={
    "steps": 8000,
    "resting_hr": 80,
    "sleep_hours": 7
})
low_days = alerts.find_low_days(steps_data)
```

## Scripts

- `scripts/fitbit_api.py` - Fitbit Web API wrapper, CLI, and analysis
- `scripts/alerts.py` - Threshold-based notifications

## Available API Methods

| Method | Description |
|--------|-------------|
| `get_steps(start, end)` | Daily step counts |
| `get_calories(start, end)` | Daily calories burned |
| `get_distance(start, end)` | Daily distance |
| `get_activity_summary(start, end)` | Activity summary |
| `get_heartrate(start, end)` | Heart rate data |
| `get_sleep(start, end)` | Sleep data |
| `get_sleep_stages(start, end)` | Detailed sleep stages |
| `get_spo2(start, end)` | Blood oxygen levels |
| `get_weight(start, end)` | Weight measurements |

## References

- `references/api.md` - Fitbit Web API documentation
- `references/metrics.md` - Metric definitions and interpretations

## Authentication

Fitbit API requires OAuth 2.0 authentication:
1. Create app at: https://dev.fitbit.com/apps
2. Get client_id and client_secret
3. Complete OAuth flow to get access_token and refresh_token
4. Set environment variables or pass to scripts
