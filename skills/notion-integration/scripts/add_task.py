#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
from datetime import datetime

# Load configuration from .env file manually
def load_env(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

TOKEN = os.environ.get('NOTION_TOKEN')
DB_ID = os.environ.get('NOTION_DB_TASKS')

if not TOKEN or not DB_ID:
    print("Error: NOTION_TOKEN or NOTION_DB_TASKS not set in environment.")
    sys.exit(1)

BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def create_task(name, do_date=None, status="Not started", priority="Medium", context="Work"):
    body = {
        'parent': {'database_id': DB_ID},
        'properties': {
            'Name': {'title': [{'text': {'content': name}}]},
            'Status': {'select': {'name': status}},
            'Priority': {'select': {'name': priority}},
            'Context': {'multi_select': [{'name': context}]}
        }
    }
    
    if do_date:
        body['properties']['Do Date'] = {'date': {'start': do_date}}

    try:
        req = urllib.request.Request(f"{BASE_URL}/pages", json.dumps(body).encode('utf-8'), HEADERS, method='POST')
        with urllib.request.urlopen(req) as response:
            res = json.load(response)
            print(f"Task created: {res['url']}")
            return res
    except urllib.error.HTTPError as e:
        print(f"Error creating task: {e.read().decode()}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_task.py <task_name> [date YYYY-MM-DD]")
        sys.exit(1)
        
    name = sys.argv[1]
    date = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime('%Y-%m-%d')
    create_task(name, date)
