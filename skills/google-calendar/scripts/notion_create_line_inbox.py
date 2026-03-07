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

def create_line_inbox(parent_page_id):
    body = {
        'parent': {'type': 'page_id', 'page_id': parent_page_id},
        'title': [{'type': 'text', 'text': {'content': 'LINE Inbox'}}],
        'properties': {
            'Sender': {'title': {}}, # Who sent it (e.g., Gary, 淑錡)
            'Message': {'rich_text': {}}, # Content
            'Time': {'date': {}}, # Timestamp
            'Status': {'select': {'options': [{'name': 'New', 'color': 'red'}, {'name': 'Processed', 'color': 'green'}]}}
        },
        'icon': {'emoji': '💬'}
    }
    url = f"{BASE_URL}/databases"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_create_line_inbox.py <page_id>")
        sys.exit(1)
        
    root_page_id = sys.argv[1]
    
    print("Creating 'LINE Inbox' Database...")
    db = create_line_inbox(root_page_id)
    print(f"Created DB ID: {db['id']}")
