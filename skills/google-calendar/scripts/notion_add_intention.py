#!/usr/bin/env python3
import os, sys, json, urllib.request

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

def add_intention(db_id, title, description, type_val):
    body = {
        'parent': {'database_id': db_id},
        'properties': {
            'Name': {'title': [{'text': {'content': title}}]},
            'Description': {'rich_text': [{'text': {'content': description}}]},
            'Type': {'select': {'name': type_val}},
            'Status': {'select': {'name': 'Active'}}
        },
        'icon': {'emoji': '🌟'}
    }
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: notion_add_intention.py <db_id> <title> <description> <type>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    title = sys.argv[2]
    desc = sys.argv[3]
    type_val = sys.argv[4] # Vision or Mission
    
    add_intention(db_id, title, desc, type_val)
    print(f"Added Intention: {title}")
