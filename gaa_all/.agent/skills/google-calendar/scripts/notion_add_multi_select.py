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
        print("Usage: notion_add_multi_select.py <db_id> <prop_name>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    prop_name = sys.argv[2]
    
    body = {
        'properties': {
            prop_name: {'multi_select': {}}
        }
    }
    request('PATCH', f"{BASE_URL}/databases/{db_id}", json.dumps(body).encode('utf-8'))
    print(f"Added '{prop_name}' property.")
