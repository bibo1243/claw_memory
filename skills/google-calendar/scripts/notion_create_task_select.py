#!/usr/bin/env python3
import os, sys, json, urllib.request
from datetime import datetime, timezone, timedelta

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

def add_task(database_id, name, status, do_date, context, image_url=None):
    # POLICY ENFORCEMENT: Ensure date includes time
    # If do_date is YYYY-MM-DD, append current time or default
    if len(do_date) == 10: # Just date
        now = datetime.now(timezone(timedelta(hours=8))) # Taiwan time
        current_time = now.strftime("T%H:%M:00+08:00")
        do_date = f"{do_date}{current_time}"
        print(f"Policy: Auto-appended current time to date -> {do_date}")

    body = {
        'parent': {'database_id': database_id},
        'properties': {
            'Name': {'title': [{'text': {'content': name}}]},
            'Status': {'select': {'name': status}},
            'Do Date': {'date': {'start': do_date}},
            'Context': {'multi_select': [{'name': context}]}
        }
    }
    
    if image_url:
        body['children'] = [
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": image_url
                    }
                }
            }
        ]
        
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: notion_create_task_select.py <db_id> <name> <status> <date> <context> [image_url]")
        sys.exit(1)
        
    db_id = sys.argv[1]
    name = sys.argv[2]
    status = sys.argv[3]
    date = sys.argv[4]
    context = sys.argv[5]
    image_url = sys.argv[6] if len(sys.argv) > 6 else None
    
    print(f"Adding task '{name}' to Notion...")
    add_task(db_id, name, status, date, context, image_url)
    print("Done.")
