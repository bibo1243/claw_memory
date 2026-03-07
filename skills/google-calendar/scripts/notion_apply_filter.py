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

def apply_privacy_filter(db_id, view_name="Safe View"):
    # Note: Notion API doesn't support creating/modifying Database Views directly yet.
    # It only supports querying with filters.
    # So we can't programmatically set the default view filter in Notion UI.
    # The best we can do is create a new "Page" that acts as a Dashboard, 
    # and embed a Linked Database with a filter. But Linked DBs also can't be fully configured via API.
    
    # Alternative: We can update the 'Status' or a new 'Sensitivity' property for existing records
    # so the user can easily filter them manually in one go.
    # Let's add a 'Sensitivity' select property.
    
    body = {
        'properties': {
            'Sensitivity': {
                'select': {
                    'options': [
                        {'name': 'Safe', 'color': 'green'},
                        {'name': 'Private', 'color': 'red'}
                    ]
                }
            }
        }
    }
    request('PATCH', f"{BASE_URL}/databases/{db_id}", json.dumps(body).encode('utf-8'))
    print("Added Sensitivity property.")
    
    # Scan and tag sensitive items
    query_body = {
        'filter': {
            'or': [
                {'property': 'Name', 'title': {'contains': '戒色'}},
                {'property': 'Name', 'title': {'contains': '絲襪'}},
                {'property': 'Name', 'title': {'contains': '美腿'}}
            ]
        }
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(query_body).encode('utf-8'))
    
    for page in data.get('results', []):
        page_id = page['id']
        update_body = {
            'properties': {
                'Sensitivity': {'select': {'name': 'Private'}}
            }
        }
        request('PATCH', f"{BASE_URL}/pages/{page_id}", json.dumps(update_body).encode('utf-8'))
        print(f"Marked {page['id']} as Private.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_apply_filter.py <db_id>")
        sys.exit(1)
        
    apply_privacy_filter(sys.argv[1])
