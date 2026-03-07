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

def get_latest_daily_improvement(db_id):
    body = {
        'filter': {
            'property': 'Name',
            'title': {
                'contains': '日精進'
            }
        },
        'sorts': [{'timestamp': 'created_time', 'direction': 'descending'}],
        'page_size': 1
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    
    if not data['results']:
        return None
        
    page = data['results'][0]
    page_id = page['id']
    
    # Get title
    title_props = page['properties']['Name']['title']
    title = title_props[0]['text']['content'] if title_props else "Untitled"
    
    # Get page content (blocks)
    blocks_url = f"{BASE_URL}/blocks/{page_id}/children"
    blocks_data = request('GET', blocks_url)
    
    content = ""
    for block in blocks_data['results']:
        if block['type'] == 'paragraph':
            text = block['paragraph']['rich_text']
            if text:
                content += text[0]['text']['content'] + "\n"
        # Add other block types if needed
        
    return page_id, title, content

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_get_latest_diary.py <db_id>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    result = get_latest_daily_improvement(db_id)
    
    if result:
        page_id, title, content = result
        print(f"ID: {page_id}")
        print(f"Title: {title}")
        print(f"Content: {content}")
    else:
        print("No daily improvement found.")
