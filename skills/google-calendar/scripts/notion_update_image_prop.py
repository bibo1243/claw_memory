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

def update_page_image_property(page_id, property_name, image_url):
    body = {
        'properties': {
            property_name: {
                'files': [
                    {
                        'name': 'goal_image.jpg',
                        'type': 'external',
                        'external': {'url': image_url}
                    }
                ]
            }
        }
    }
    url = f"{BASE_URL}/pages/{page_id}"
    return request('PATCH', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: notion_update_image_prop.py <page_id> <prop_name> <image_url>")
        sys.exit(1)
        
    page_id = sys.argv[1]
    prop_name = sys.argv[2]
    image_url = sys.argv[3]
    
    update_page_image_property(page_id, prop_name, image_url)
    print(f"Updated image for page {page_id}")
