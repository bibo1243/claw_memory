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

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: notion_update_context_options.py <db_id> <new_option>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    new_option = sys.argv[2]
    
    # We need to get existing options first to append, but Notion API allows patching to add options
    # However, 'multi_select' options are merged if we just add one? No, we need to redefine or just add.
    # Actually, for multi_select, we can't easily "add one" to the schema via API without fetching first or just sending it with a value on a page creation (which auto-adds it).
    # But to be safe, let's try to update the database schema to include it explicitly with a color.
    
    body = {
        'properties': {
            'Context': {
                'multi_select': {
                    'options': [
                        {'name': 'Work', 'color': 'orange'},
                        {'name': 'Personal', 'color': 'blue'},
                        {'name': 'Study', 'color': 'pink'},
                        {'name': new_option, 'color': 'green'} # New option
                    ]
                }
            }
        }
    }
    request('PATCH', f"{BASE_URL}/databases/{db_id}", json.dumps(body).encode('utf-8'))
    print(f"Added '{new_option}' to Context options.")
