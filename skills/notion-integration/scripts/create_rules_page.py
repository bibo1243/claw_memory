#!/usr/bin/env python3
import os
import sys
import json
import urllib.request

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

TOKEN = os.environ.get('NOTION_TOKEN')
KNOWLEDGE_DB = os.environ.get('NOTION_DB_KNOWLEDGE')

BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def create_rules_page(content):
    # 1. Create page in Knowledge Base
    body = {
        'parent': {'database_id': KNOWLEDGE_DB},
        'properties': {
            'Name': {'title': [{'text': {'content': 'Gaa 版規與原則'}}]},
            'Type': {'select': {'name': 'SOP'}},
            'Tags': {'multi_select': [{'name': 'Rules'}, {'name': 'Gaa'}]}
        },
        'children': [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "Gaa 版規與原則"}}]
                }
            },
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
        with urllib.request.urlopen(req) as resp:
            res = json.load(resp)
            print(f"Rule page created: {res['url']}")
    except urllib.error.HTTPError as e:
        print(f"Error creating rule page: {e.read().decode()}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 create_rules.py <content>")
        sys.exit(1)
        
    create_rules_page(sys.argv[1])
