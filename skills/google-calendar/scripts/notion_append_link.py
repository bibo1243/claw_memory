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

def append_link_to_page(page_id, text, url):
    blocks = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": text}},
                    {"type": "text", "text": {"content": " (點擊查看)", "link": {"url": url}}}
                ]
            }
        }
    ]
    api_url = f"{BASE_URL}/blocks/{page_id}/children"
    return request('PATCH', api_url, json.dumps({'children': blocks}).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: notion_append_link.py <page_id> <text> <url>")
        sys.exit(1)
        
    page_id = sys.argv[1]
    text = sys.argv[2]
    link_url = sys.argv[3]
    
    append_link_to_page(page_id, text, link_url)
    print("Link appended.")
