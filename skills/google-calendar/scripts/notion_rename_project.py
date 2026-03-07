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

def rename_page(db_id, old_title, new_title):
    # Find page
    body = {
        'filter': {
            'property': 'Name',
            'title': {
                'equals': old_title
            }
        }
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    
    if data['results']:
        page_id = data['results'][0]['id']
        update_body = {
            'properties': {
                'Name': {'title': [{'text': {'content': new_title}}]}
            }
        }
        request('PATCH', f"{BASE_URL}/pages/{page_id}", json.dumps(update_body).encode('utf-8'))
        print(f"Renamed '{old_title}' to '{new_title}'.")
    else:
        print(f"Page '{old_title}' not found. Creating new one...")
        # Create new project if not found (Removed Status as it might be missing in schema or wrong type)
        create_body = {
            'parent': {'database_id': db_id},
            'properties': {
                'Name': {'title': [{'text': {'content': new_title}}]},
                'Priority': {'select': {'name': 'High'}}
            }
        }
        request('POST', f"{BASE_URL}/pages", json.dumps(create_body).encode('utf-8'))
        print(f"Created project '{new_title}'.")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: notion_rename_project.py <db_id> <old_title> <new_title>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    old_title = sys.argv[2]
    new_title = sys.argv[3]
    
    rename_page(db_id, old_title, new_title)
