#!/usr/bin/env python3
"""
Fitbit Alerts - Threshold-based notifications

Usage:
    python alerts.py --days 7 --steps 8000 --sleep 7
"""

import os
import json
from datetime import datetime, timedelta

try:
    from fitbit_api import FitbitClient
except ImportError:
    from scripts.fitbit_api import FitbitClient


class FitbitAlerts:
    """Alert on threshold breaches"""
    
    DEFAULT_THRESHOLDS = {
        "steps": 8000,
        "calories": 1800,
        "sleep_hours": 7,
        "resting_hr": 80,
        "active_minutes": 30,
        "sedentary_hours": 10
    }
    
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
    
    def check_steps(self, steps_value):
        """Check daily steps"""
        if steps_value < self.thresholds.get("steps", 8000):
            return f"Low steps: {steps_value} (< {self.thresholds['steps']})"
        return None
    
    def check_sleep(self, sleep_minutes):
        """Check sleep duration"""
        sleep_hours = sleep_minutes / 60
        if sleep_hours < self.thresholds.get("sleep_hours", 7):
            return f"Low sleep: {sleep_hours:.1f}h (< {self.thresholds['sleep_hours']}h)"
        return None
    
    def check_resting_hr(self, rhr):
        """Check resting heart rate"""
        if rhr > self.thresholds.get("resting_hr", 80):
            return f"Elevated RHR: {rhr} bpm (> {self.thresholds['resting_hr']})"
        if rhr < 50:
            return f"Low RHR: {rhr} bpm (< 50)"
        return None
    
    def find_low_days(self, steps_data, sleep_data=None, hr_data=None):
        """Find all days below thresholds"""
        alerts = []
        
        # Process steps
        for day in steps_data.get("activities-steps", []):
            date = day.get("dateTime")
            steps = day.get("value", 0)
            step_alert = self.check_steps(steps)
            
            if step_alert:
                alerts.append({"date": date, "type": "steps", "alert": step_alert})
        
        return alerts


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fitbit Alerts")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--steps", type=int, default=8000)
    parser.add_argument("--sleep", type=float, default=7)
    parser.add_argument("--resting-hr", type=int, default=80)
    parser.add_argument("--client-id", help="Fitbit client ID")
    parser.add_argument("--client-secret", help="Fitbit client secret")
    parser.add_argument("--access-token", help="Fitbit access token")
    
    args = parser.parse_args()
    
    client = FitbitClient(
        client_id=args.client_id,
        client_secret=args.client_secret,
        access_token=args.access_token
    )
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    steps = client.get_steps(start_date, end_date)
    sleep = client.get_sleep(start_date, end_date)
    hr = client.get_heartrate(start_date, end_date)
    
    alerts = FitbitAlerts({
        "steps": args.steps,
        "sleep_hours": args.sleep,
        "resting_hr": args.resting_hr
    })
    
    low_days = alerts.find_low_days(steps, sleep, hr)
    
    if low_days:
        print("⚠️  Fitbit Alerts:")
        for day in low_days:
            print(f"  {day['date']}: {day['alert']}")
    else:
        print("✅ All metrics above thresholds")
    
    return low_days


if __name__ == "__main__":
    main()
