#!/usr/bin/env python3
"""
Fitbit Web API Wrapper

Usage:
    python fitbit_api.py activity --days 7
    python fitbit_api.py heartrate --days 7
    python fitbit_api.py sleep --days 7
    python fitbit_api.py report --type weekly
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import urllib.parse
import base64
from datetime import datetime, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent


class FitbitClient:
    """Fitbit Web API client"""

    BASE_URL = "https://api.fitbit.com"

    def __init__(self, client_id=None, client_secret=None, access_token=None, refresh_token=None):
        self.client_id = client_id or os.environ.get("FITBIT_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("FITBIT_CLIENT_SECRET")
        self.access_token = access_token or os.environ.get("FITBIT_ACCESS_TOKEN")
        self.refresh_token = refresh_token or os.environ.get("FITBIT_REFRESH_TOKEN")

        if not self.access_token:
            raise ValueError("FITBIT_ACCESS_TOKEN not set. Get it from https://dev.fitbit.com/apps")

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def _request(self, endpoint, date_type="date"):
        """Make API request using urllib"""
        url = f"{self.BASE_URL}/{endpoint}"
        req = urllib.request.Request(url, headers=self.headers)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                # Token expired, try to refresh
                if self._refresh_token():
                    return self._request(endpoint, date_type)
                else:
                    raise ValueError("Fitbit token expired. Refresh failed.")
            raise

    def _refresh_token(self):
        """Refresh access token"""
        if not self.client_id or not self.client_secret or not self.refresh_token:
            return False

        # Create basic auth header
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")

        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.fitbit.com/oauth2/token",
            data=data,
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                tokens = json.loads(resp.read().decode("utf-8"))
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
                self.headers["Authorization"] = f"Bearer {self.access_token}"
                return True
        except urllib.error.HTTPError:
            return False

    def get_steps(self, start_date, end_date):
        """Fetch step data"""
        endpoint = f"1/user/-/activities/steps/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_calories(self, start_date, end_date):
        """Fetch calorie data"""
        endpoint = f"1/user/-/activities/calories/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_distance(self, start_date, end_date):
        """Fetch distance data"""
        endpoint = f"1/user/-/activities/distance/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_activity_summary(self, start_date, end_date):
        """Fetch activity summary"""
        endpoint = f"1/user/-/activities/date/{start_date}.json"
        return self._request(endpoint)

    def get_heartrate(self, start_date, end_date):
        """Fetch heart rate data"""
        endpoint = f"1/user/-/activities/heart/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_sleep(self, start_date, end_date):
        """Fetch sleep data (summary)"""
        endpoint = f"1.2/user/-/sleep/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_sleep_stages(self, start_date, end_date):
        """Fetch detailed sleep stages"""
        endpoint = f"1.3/user/-/sleep/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_spo2(self, start_date, end_date):
        """Fetch blood oxygen data"""
        endpoint = f"1/user/-/spo2/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_weight(self, start_date, end_date):
        """Fetch weight data"""
        endpoint = f"1/user/-/body/weight/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_active_zone_minutes(self, start_date, end_date):
        """Fetch Active Zone Minutes (AZM) data
        
        Returns AZM breakdown:
        - activeZoneMinutes (total)
        - fatBurnActiveZoneMinutes (1× credit)
        - cardioActiveZoneMinutes (2× credit)
        - peakActiveZoneMinutes (2× credit)
        """
        # Calculate number of days between start and end
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        # Use period format: 1d, 7d, 30d, etc.
        period = f"{days}d" if days <= 30 else "30d"
        
        endpoint = f"1/user/-/activities/active-zone-minutes/date/{start_date}/{period}.json"
        return self._request(endpoint)


class FitbitAnalyzer:
    """Analyze Fitbit data"""

    def __init__(self, steps_data=None, hr_data=None, sleep_data=None, activity_data=None):
        self.steps = steps_data or []
        self.hr = hr_data or []
        self.sleep = sleep_data or []
        self.activity = activity_data or []

    def average_metric(self, data, key):
        """Calculate average of a metric"""
        if not data:
            return None
        # Convert to float to handle string values from API
        values = []
        for d in data:
            val = d.get(key)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    continue
        return sum(values) / len(values) if values else None

    def trend(self, data, key, days=7):
        """Calculate trend over N days"""
        if len(data) < 2:
            return 0
        recent = data[-days:]
        if len(recent) < 2:
            return 0
        try:
            first = float(recent[0].get(key, 0))
            last = float(recent[-1].get(key, 0))
            return last - first
        except (ValueError, TypeError):
            return 0

    def summary(self):
        """Generate summary"""
        steps_data = self.steps.get("activities-steps", []) if self.steps else []
        hr_data = self.hr.get("activities-heart", []) if self.hr else []

        avg_steps = self.average_metric(steps_data, "value")

        # Extract resting HR
        resting_hrs = []
        for day in hr_data:
            value = day.get("value", {})
            if isinstance(value, dict):
                resting_hrs.append(value.get("restingHeartRate"))
            else:
                resting_hrs.append(value)

        avg_rhr = sum([r for r in resting_hrs if r]) / len([r for r in resting_hrs if r]) if resting_hrs else None

        return {
            "avg_steps": avg_steps,
            "avg_resting_hr": avg_rhr,
            "steps_trend": self.trend(steps_data, "value"),
            "days_tracked": len(steps_data)
        }


class FitbitReporter:
    """Generate Fitbit reports"""

    def __init__(self, client):
        self.client = client

    def generate_report(self, report_type="weekly", days=None):
        """Generate report"""
        if not days:
            days = 7 if report_type == "weekly" else 30

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        steps = self.client.get_steps(start_date, end_date)
        hr = self.client.get_heartrate(start_date, end_date)
        sleep = self.client.get_sleep(start_date, end_date)

        analyzer = FitbitAnalyzer(steps, hr, sleep)
        summary = analyzer.summary()

        return {
            "report_type": report_type,
            "period": f"{start_date} to {end_date}",
            "summary": summary,
            "data": {
                "steps": steps,
                "heartrate": hr,
                "sleep": sleep
            }
        }


def main():
    parser = argparse.ArgumentParser(description="Fitbit Analytics CLI")
    parser.add_argument("command", choices=["activity", "steps", "calories", "heartrate", "sleep", "report", "summary"],
                       help="Data type to fetch or report type")
    parser.add_argument("--days", type=int, default=7, help="Number of days")
    parser.add_argument("--type", default="weekly", help="Report type")
    parser.add_argument("--client-id", help="Fitbit client ID")
    parser.add_argument("--client-secret", help="Fitbit client secret")
    parser.add_argument("--access-token", help="Fitbit access token")

    args = parser.parse_args()

    try:
        client = FitbitClient(
            client_id=args.client_id,
            client_secret=args.client_secret,
            access_token=args.access_token
        )

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

        if args.command in ["activity", "steps"]:
            data = client.get_steps(start_date, end_date)
            print(json.dumps(data, indent=2))

        elif args.command == "calories":
            data = client.get_calories(start_date, end_date)
            print(json.dumps(data, indent=2))

        elif args.command == "heartrate":
            data = client.get_heartrate(start_date, end_date)
            print(json.dumps(data, indent=2))

        elif args.command == "sleep":
            data = client.get_sleep(start_date, end_date)
            print(json.dumps(data, indent=2))

        elif args.command == "summary":
            steps = client.get_steps(start_date, end_date)
            hr = client.get_heartrate(start_date, end_date)
            analyzer = FitbitAnalyzer(steps, hr)
            summary = analyzer.summary()
            print(json.dumps(summary, indent=2))

        elif args.command == "report":
            reporter = FitbitReporter(client)
            report = reporter.generate_report(args.type, args.days)
            print(json.dumps(report, indent=2))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Set FITBIT_ACCESS_TOKEN or use --access-token", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
