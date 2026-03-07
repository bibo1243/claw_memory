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
    if len(sys.argv) < 2:
        print("Usage: notion_list_tasks.py <db_id>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    
    # Filter for tasks that are not Done
    body = {
        'filter': {
            'property': 'Status',
            'select': {
                'does_not_equal': 'Done'
            }
        },
        'sorts': [
            {
                'property': 'Do Date',
                'direction': 'ascending'
            }
        ]
    }
    
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    
    for page in data.get('results', []):
        props = page['properties']
        name_list = props.get('Name', {}).get('title', [])
        name = name_list[0]['text']['content'] if name_list else "Untitled"
        
        status = props.get('Status', {}).get('select', {})
        status_name = status.get('name') if status else "No Status"
        
        date_prop = props.get('Do Date', {}).get('date', {})
        date = date_prop.get('start') if date_prop else "No Date"
        
        print(f"- [{status_name}] {name} (Date: {date})")
