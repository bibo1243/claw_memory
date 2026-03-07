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

def search_databases():
    # Search for all databases accessible by the integration
    body = {
        'filter': {
            'value': 'database',
            'property': 'object'
        }
    }
    data = request('POST', f"{BASE_URL}/search", json.dumps(body).encode('utf-8'))
    
    print(f"Found {len(data['results'])} databases:")
    for db in data['results']:
        title_list = db.get('title', [])
        title = title_list[0]['text']['content'] if title_list else "Untitled"
        print(f"- {title} (ID: {db['id']})")

if __name__ == '__main__':
    search_databases()
