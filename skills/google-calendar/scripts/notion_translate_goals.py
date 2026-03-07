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

def update_category_options(db_id):
    # Updating schema to rename options to Chinese
    # Note: Notion API updates options by matching ID or name. 
    # If we provide new names, it might add new ones unless we match existing.
    # But usually, providing the full schema updates it.
    
    body = {
        'properties': {
            'Category': {
                'select': {
                    'options': [
                        {'name': '健康 (Health)', 'color': 'red'},
                        {'name': '工作 (Work)', 'color': 'blue'},
                        {'name': '財務 (Finance)', 'color': 'yellow'},
                        {'name': '家庭 (Family)', 'color': 'pink'},
                        {'name': '社交 (Social)', 'color': 'orange'},
                        {'name': '學習 (Learning)', 'color': 'purple'},
                        {'name': '休閒 (Leisure)', 'color': 'green'},
                        {'name': '挑戰 (Challenge)', 'color': 'gray'}
                    ]
                }
            }
        }
    }
    request('PATCH', f"{BASE_URL}/databases/{db_id}", json.dumps(body).encode('utf-8'))

def update_pages_category(db_id):
    # 1. Query all pages
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps({}).encode('utf-8'))
    
    # Mapping
    mapping = {
        'Health': '健康 (Health)',
        'Work': '工作 (Work)',
        'Finance': '財務 (Finance)',
        'Family': '家庭 (Family)',
        'Social': '社交 (Social)',
        'Learning': '學習 (Learning)',
        'Leisure': '休閒 (Leisure)',
        'Challenge': '挑戰 (Challenge)'
    }
    
    for page in data.get('results', []):
        page_id = page['id']
        current_cat = page['properties']['Category']['select']
        
        if current_cat:
            old_name = current_cat['name']
            if old_name in mapping:
                new_name = mapping[old_name]
                print(f"Updating {page_id}: {old_name} -> {new_name}")
                
                body = {
                    'properties': {
                        'Category': {'select': {'name': new_name}}
                    }
                }
                request('PATCH', f"{BASE_URL}/pages/{page_id}", json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_translate_goals.py <db_id>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    
    # We will update pages first (to use new names), then schema will auto-update or we can force it.
    # Actually, if we just update pages with new values, Notion creates those options.
    update_pages_category(db_id)
    
    # Optionally clean up old options in schema later, but updating pages is enough for visual change.
    print("Done.")
