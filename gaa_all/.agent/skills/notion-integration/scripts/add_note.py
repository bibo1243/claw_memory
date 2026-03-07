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
DB_ID = os.environ.get('NOTION_DB_KNOWLEDGE')

BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def create_note(name, content, type="Note", tags=None):
    if not tags: tags = []
    
    body = {
        'parent': {'database_id': DB_ID},
        'properties': {
            'Name': {'title': [{'text': {'content': name}}]},
            'Type': {'select': {'name': type}},
            'Tags': {'multi_select': [{'name': tag} for tag in tags]}
        },
        'children': [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                }
            }
        ]
    }

    try:
        req = urllib.request.Request(f"{BASE_URL}/pages", json.dumps(body).encode('utf-8'), HEADERS, method='POST')
        with urllib.request.urlopen(req) as response:
            res = json.load(response)
            print(f"Note created: {res['url']}")
            return res
    except urllib.error.HTTPError as e:
        print(f"Error creating note: {e.read().decode()}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 add_note.py <title> <content> [type] [tags]")
        sys.exit(1)
        
    title = sys.argv[1]
    content = sys.argv[2]
    type = sys.argv[3] if len(sys.argv) > 3 else "Note"
    tags = sys.argv[4].split(',') if len(sys.argv) > 4 else []
    
    create_note(title, content, type, tags)
