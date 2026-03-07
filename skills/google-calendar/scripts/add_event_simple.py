#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
from datetime import datetime

# Load .env
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    os.environ[parts[0]] = parts[1]

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

# Set API endpoint and headers
API_URL = "https://www.googleapis.com/calendar/v3"
ACCESS_TOKEN = os.environ.get('GOOGLE_ACCESS_TOKEN')
CALENDAR_ID = 'bibo1243@gmail.com' 

def add_event(summary, start_time, end_time=None):
    if not end_time:
        # Default 1 hour
        dt = datetime.fromisoformat(start_time)
        end_time = dt.replace(hour=dt.hour + 1).isoformat()
    
    body = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Taipei'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Taipei'}
    }
    
    req = urllib.request.Request(
        f"{API_URL}/calendars/{CALENDAR_ID}/events",
        data=json.dumps(body).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            print(f"Event created: {data.get('htmlLink')}")
            return data
    except urllib.error.HTTPError as e:
        print(f"Error adding event: {e.read().decode()}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 add_event.py <summary> <start_iso> [end_iso]")
        sys.exit(1)
        
    summary = sys.argv[1]
    start = sys.argv[2]
    end = sys.argv[3] if len(sys.argv) > 3 else None
    
    add_event(summary, start, end)
