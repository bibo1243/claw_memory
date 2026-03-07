#!/usr/bin/env python3
import os, sys, json, urllib.request

# Hardcode the token here for immediate use
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

def update_page_cover(page_id, cover_url):
    body = {
        'cover': {
            'type': 'external',
            'external': {
                'url': cover_url
            }
        }
    }
    url = f"{BASE_URL}/pages/{page_id}"
    return request('PATCH', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: notion_update_cover.py <page_id> <cover_url>")
        sys.exit(1)
        
    page_id = sys.argv[1]
    cover_url = sys.argv[2]
    
    print(f"Updating cover for page {page_id}...")
    update_page_cover(page_id, cover_url)
    print("Done.")
