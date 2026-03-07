#!/usr/bin/env python3
import os, sys, json, urllib.request
from datetime import datetime, date

# Hardcode the token here
NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def request(method, url, data=None):
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

def create_streak_database(parent_page_id):
    title = "Freedom Streak (自由天數)"
    properties = {
        'Name': {'title': {}},
        'Start Date': {'date': {}},
        'Current Streak': {'formula': {'expression': "dateBetween(now(), prop(\"Start Date\"), \"days\")"}}
    }
    
    body = {
        'parent': {'type': 'page_id', 'page_id': parent_page_id},
        'title': [{'type': 'text', 'text': {'content': title}}],
        'properties': properties,
        'icon': {'emoji': '🔥'}
    }
    url = f"{BASE_URL}/databases"
    return request('POST', url, json.dumps(body).encode('utf-8'))

def init_streak(database_id, start_date):
    body = {
        'parent': {'database_id': database_id},
        'properties': {
            'Name': {'title': [{'text': {'content': 'Current Streak'}}]},
            'Start Date': {'date': {'start': start_date}}
        }
    }
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_add_streak.py <page_id>")
        sys.exit(1)
        
    root_page_id = sys.argv[1]
    
    print("Creating 'Freedom Streak' Database...")
    db = create_streak_database(root_page_id)
    db_id = db['id']
    print(f"   Created DB: {db_id}")
    
    # Initialize with today as start date (Day 0)
    today = date.today().isoformat()
    print(f"Initializing streak starting from {today}...")
    init_streak(db_id, today)
    
    print("Done.")
