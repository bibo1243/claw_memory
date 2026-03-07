#!/usr/bin/env python3
import os, sys, json, urllib.request
from datetime import datetime

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
DB_ID = '30b1fbf9-30df-81f1-897c-db2c1cb7fdb2'
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
        return None

def find_page_by_name(db_id, name):
    body = {
        'filter': {
            'property': 'Name',
            'title': {
                'equals': name
            }
        }
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    if data and data['results']:
        return data['results'][0]['id']
    return None

def split_text(text, limit=2000):
    return [text[i:i+limit] for i in range(0, len(text), limit)]

def update_page_content(page_id, content):
    # 1. Clear content
    children = request('GET', f"{BASE_URL}/blocks/{page_id}/children")
    if children:
        for block in children['results']:
            request('DELETE', f"{BASE_URL}/blocks/{block['id']}")
            
    # 2. Add new content
    chunks = split_text(content, 2000)
    children_blocks = []
    for chunk in chunks:
        children_blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}],
                "language": "markdown"
            }
        })
    request('PATCH', f"{BASE_URL}/blocks/{page_id}/children", json.dumps({'children': children_blocks}).encode('utf-8'))

def create_page(db_id, name, content):
    chunks = split_text(content, 2000)
    children_blocks = []
    for chunk in chunks:
        children_blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}],
                "language": "markdown"
            }
        })

    body = {
        'parent': {'database_id': db_id},
        'properties': {
            'Name': {'title': [{'text': {'content': name}}]},
            'Description': {'rich_text': [{'text': {'content': 'Project Specification & Discovery'}}]},
            'Last Updated': {'date': {'start': datetime.now().isoformat()}}
        },
        'children': children_blocks
    }
    request('POST', f"{BASE_URL}/pages", json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_sync_discovery.py <file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    name = "discovery.md (GAA 規格書)"
    
    with open(file_path, 'r') as f:
        content = f.read()
        
    page_id = find_page_by_name(DB_ID, name)
    if page_id:
        print(f"Updating '{name}' in Notion...")
        update_page_content(page_id, content)
    else:
        print(f"Creating '{name}' in Notion...")
        create_page(DB_ID, name, content)
    
    print("Sync complete.")
