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

def add_goal(db_id, title, category, description):
    body = {
        'parent': {'database_id': db_id},
        'properties': {
            'Name': {'title': [{'text': {'content': title}}]},
            'Category': {'select': {'name': category}}, 
        },
        'children': [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": description}}]}
            }
        ]
    }
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_add_single_goal.py <goals_db_id> <title> <category> <description>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    title = sys.argv[2]
    cat = sys.argv[3]
    desc = sys.argv[4]
    
    print(f"Adding goal: {title}...")
    add_goal(db_id, title, cat, desc)
    print("Goal added.")
