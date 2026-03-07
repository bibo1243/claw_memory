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

def add_knowledge_entry(database_id, name, type_val, content, image_urls=None):
    # Prepare blocks
    blocks = []
    
    # Add text content
    if content:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
        })
    
    # Add images
    if image_urls:
        for url in image_urls:
            blocks.append({
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": url
                    }
                }
            })

    body = {
        'parent': {'database_id': database_id},
        'properties': {
            'Name': {'title': [{'text': {'content': name}}]},
            'Type': {'select': {'name': type_val}},
            'Tags': {'multi_select': [{'name': 'Inbox'}]} 
        },
        'children': blocks
    }
    
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        # print("Usage: notion_add_knowledge.py <db_id> <name> <type> <content> [img_url1] [img_url2]...")
        sys.exit(1)
        
    db_id = sys.argv[1]
    name = sys.argv[2]
    type_val = sys.argv[3]
    content = sys.argv[4]
    img_urls = sys.argv[5:] if len(sys.argv) > 5 else []
    
    print(f"Adding knowledge '{name}' to Notion...")
    res = add_knowledge_entry(db_id, name, type_val, content, img_urls)
    if res:
        print("Done.")
    else:
        print("Failed.")