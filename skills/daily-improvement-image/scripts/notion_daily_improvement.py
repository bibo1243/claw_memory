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

def calculate_day_count(base_date_str="2026-02-18", base_count=801):
    base_date = datetime.strptime(base_date_str, "%Y-%m-%d").date()
    today = date.today()
    delta = (today - base_date).days
    return base_count + delta

def add_daily_improvement(database_id, title, content):
    # Calculate Day Count
    day_count = calculate_day_count()
    full_title = f"日精進 Day {day_count}：{title}"
    
    # Body blocks for the article
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": full_title}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
        }
    ]

    body = {
        'parent': {'database_id': database_id},
        'properties': {
            'Name': {'title': [{'text': {'content': full_title}}]},
            'Status': {'select': {'name': 'Done'}},
            'Do Date': {'date': {'start': datetime.now().isoformat()}}, # Current time
            'Context': {'multi_select': [{'name': 'Personal'}]}
        },
        'children': blocks
    }
    
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: notion_daily_improvement.py <db_id> <title> <content>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    title = sys.argv[2]
    content = sys.argv[3]
    
    print(f"Adding Daily Improvement...")
    add_daily_improvement(db_id, title, content)
    print("Done.")
