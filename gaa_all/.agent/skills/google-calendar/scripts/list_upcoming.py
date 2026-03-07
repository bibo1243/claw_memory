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
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    os.environ[parts[0]] = parts[1]

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

# Set API endpoint and headers
API_URL = "https://www.googleapis.com/calendar/v3"
ACCESS_TOKEN = os.environ.get('GOOGLE_ACCESS_TOKEN')
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def list_events(calendar_id, time_min=None, time_max=None, max_results=10):
    url = f"{API_URL}/calendars/{calendar_id}/events?maxResults={max_results}&orderBy=startTime&singleEvents=true"
    if time_min:
        url += f"&timeMin={time_min}"
    if time_max:
        url += f"&timeMax={time_max}"
        
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            return data.get('items', [])
    except urllib.error.HTTPError as e:
        print(f"Error listing events for {calendar_id}: {e}")
        return []

if __name__ == "__main__":
    import datetime
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    
    # 1. Main Calendar (Gary / bibo1243)
    print("--- 冠葦行程 (bibo1243) ---")
    events = list_events('bibo1243@gmail.com', time_min=now, max_results=5)
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start} - {event.get('summary', 'No Title')}")
        
    # 2. CiGuang Calendar (1383...)
    print("\n--- 慈光暨附設機構 ---")
    events_cg = list_events('1383fae5b7204ef46d5fd09f338244740bff7449da5f137ea9fdb9a9f0a1d4de@group.calendar.google.com', time_min=now, max_results=5)
    for event in events_cg:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start} - {event.get('summary', 'No Title')}")
