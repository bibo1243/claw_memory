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

def deep_scan_and_hide(db_id):
    # Keywords to filter
    keywords = ['戒色', '絲襪', '美腿', '性慾', '腿', '色', '誘惑', '衝動']
    
    # Construct OR filter
    or_conditions = []
    for kw in keywords:
        or_conditions.append({'property': 'Name', 'title': {'contains': kw}})
        
    query_body = {
        'filter': {
            'or': or_conditions
        }
    }
    
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(query_body).encode('utf-8'))
    
    count = 0
    for page in data.get('results', []):
        page_id = page['id']
        title = page['properties']['Name']['title'][0]['text']['content']
        
        # Check current sensitivity
        current_sens = page['properties'].get('Sensitivity', {}).get('select')
        if current_sens and current_sens['name'] == 'Private':
            continue # Already marked
            
        print(f"Hiding: {title}")
        update_body = {
            'properties': {
                'Sensitivity': {'select': {'name': 'Private'}}
            }
        }
        request('PATCH', f"{BASE_URL}/pages/{page_id}", json.dumps(update_body).encode('utf-8'))
        count += 1
        
    print(f"Deep scan complete. Hid {count} new items.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_deep_hide.py <db_id>")
        sys.exit(1)
        
    deep_scan_and_hide(sys.argv[1])
