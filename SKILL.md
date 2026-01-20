---
name: fitbit-analytics
description: Fitbit health and fitness data integration. Fetch steps, heart rate, sleep, activity, calories, and trends from Fitbit Web API. Generate automated health reports, correlations, and alerts for inactivity or abnormal metrics.
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
python /home/art/.clawdbot/skills/fitbit-analytics/scripts/fitbit_api.py activity --days 7

# Get heart rate data
python /home/art/.clawdbot/skills/fitbit-analytics/scripts/fitbit_api.py heartrate --days 7

# Sleep summary
python /home/art/.clawdbot/skills/fitbit-analytics/scripts/fitbit_api.py sleep --days 7

# Generate weekly health report
python /home/art/.clawdbot/skills/fitbit-analytics/scripts/fitbit_api.py report --type weekly
```

## When to Use

Use this skill when:
- Fetching Fitbit metrics (steps, calories, heart rate, sleep, activity)
- Analyzing activity trends over time
- Correlating fitness data with sleep/productivity
- Setting up alerts for inactivity or abnormal heart rate
- Generating daily/weekly/monthly health reports

## Core Workflows

### 1. Data Fetching
```python
from fitbit_api import FitbitClient

client = FitbitClient(
    client_id=fitbit_client_id,
    client_secret=fitbit_client_secret,
    access_token=fitbit_access_token,
    refresh_token=fitbit_refresh_token
)
steps_data = client.get_activity(start_date="2026-01-01", end_date="2026-01-16")
hr_data = client.get_heartrate(start_date="2026-01-01", end_date="2026-01-16")
sleep_data = client.get_sleep(start_date="2026-01-01", end_date="2026-01-16")
```

### 2. Trend Analysis
```python
from analyzer import FitbitAnalyzer

analyzer = FitbitAnalyzer(steps_data, hr_data, sleep_data)
avg_steps = analyzer.average_metric("steps")
resting_hr = analyzer.average_metric("resting_heart_rate")
sleep_score = analyzer.calculate_sleep_score()
```

### 3. Alerts
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

- `scripts/fitbit_api.py` - Fitbit Web API wrapper
- `scripts/analyzer.py` - Trend analysis and correlations
- `scripts/alerts.py` - Threshold-based notifications
- `scripts/report.py` - Report generation

## References

- `references/api.md` - Fitbit Web API documentation
- `references/metrics.md` - Metric definitions and interpretations

## Authentication

Fitbit API requires OAuth 2.0 authentication:
1. Create app at: https://dev.fitbit.com/apps
2. Get client_id and client_secret
3. Complete OAuth flow to get access_token and refresh_token
4. Set environment variables or pass to scripts
