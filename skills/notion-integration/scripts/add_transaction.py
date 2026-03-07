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
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

TOKEN = os.environ.get('NOTION_TOKEN')
DB_ID = os.environ.get('NOTION_DB_TRANSACTIONS')

BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def create_transaction(item, amount, category="食 (三餐/飲料)", date=None):
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
        
    body = {
        'parent': {'database_id': DB_ID},
        'properties': {
            'Item': {'title': [{'text': {'content': item}}]},
            'Amount': {'number': float(amount)},
            'Category': {'select': {'name': category}},
            'Date': {'date': {'start': date}}
        }
    }

    try:
        req = urllib.request.Request(f"{BASE_URL}/pages", json.dumps(body).encode('utf-8'), HEADERS, method='POST')
        with urllib.request.urlopen(req) as response:
            res = json.load(response)
            print(f"Transaction recorded: {res['url']}")
            return res
    except urllib.error.HTTPError as e:
        print(f"Error creating transaction: {e.read().decode()}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 add_transaction.py <item> <amount> [category] [date]")
        sys.exit(1)
        
    item = sys.argv[1]
    amount = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "食 (三餐/飲料)"
    date = sys.argv[4] if len(sys.argv) > 4 else None
    
    create_transaction(item, amount, category, date)
