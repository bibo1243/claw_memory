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

def get_task_id_by_name(db_id, name):
    body = {
        'filter': {
            'property': 'Name',
            'title': {
                'equals': name
            }
        },
        'sorts': [{'timestamp': 'created_time', 'direction': 'descending'}],
        'page_size': 1
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    if data['results']:
        return data['results'][0]['id']
    return None

def append_comment_only(page_id, comment):
    blocks = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": comment}}]}
        }
    ]
    
    url = f"{BASE_URL}/blocks/{page_id}/children"
    return request('PATCH', url, json.dumps({'children': blocks}).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: notion_append_comment.py <db_id> <task_name> <comment>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    name = sys.argv[2]
    comment = sys.argv[3]
    
    task_id = get_task_id_by_name(db_id, name)
    if task_id:
        print(f"Appending to task '{name}'...")
        append_comment_only(task_id, comment)
        print("Done.")
    else:
        print("Task not found.")
