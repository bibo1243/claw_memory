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

def migrate_food_transactions(trans_db_id, tasks_db_id, goal_id):
    # 1. Query food transactions
    body = {
        'filter': {
            'property': 'Category',
            'select': {
                'equals': '食 (三餐/飲料)'
            }
        }
    }
    data = request('POST', f"{BASE_URL}/databases/{trans_db_id}/query", json.dumps(body).encode('utf-8'))
    
    count = 0
    for page in data.get('results', []):
        props = page['properties']
        
        # Extract info
        item = props['Item']['title'][0]['text']['content']
        amount = props['Amount']['number']
        date = props['Date']['date']['start']
        note = props['Note']['rich_text'][0]['text']['content'] if props['Note']['rich_text'] else ""
        
        # Check for image
        image_url = None
        if 'Receipt' in props and props['Receipt']['files']:
            file_obj = props['Receipt']['files'][0]
            if file_obj['type'] == 'external':
                image_url = file_obj['external']['url']
            elif file_obj['type'] == 'file':
                image_url = file_obj['file']['url']
        
        # Create Task
        print(f"Migrating '{item}'...")
        
        task_body = {
            'parent': {'database_id': tasks_db_id},
            'properties': {
                'Name': {'title': [{'text': {'content': f"飲食：{item} (${amount})"}}]},
                'Status': {'select': {'name': 'Done'}},
                'Do Date': {'date': {'start': date}},
                'Context': {'multi_select': [{'name': 'Personal'}]},
                'Goal Relation': {'relation': [{'id': goal_id}]},
                # We can try to parse calories from note if available, but for now just move note
            },
            'children': [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": note}}]}
                }
            ]
        }
        
        if image_url:
             task_body['children'].append({
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": image_url
                    }
                }
            })
            
        request('POST', f"{BASE_URL}/pages", json.dumps(task_body).encode('utf-8'))
        
        # Optionally delete original transaction to avoid duplication? 
        # User said "change to", implying migration. Let's archive the original.
        request('PATCH', f"{BASE_URL}/pages/{page['id']}", json.dumps({'archived': True}).encode('utf-8'))
        count += 1
        
    print(f"Migrated {count} food transactions to Tasks.")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: notion_migrate_food.py <trans_db_id> <tasks_db_id> <goal_page_id>")
        sys.exit(1)
        
    migrate_food_transactions(sys.argv[1], sys.argv[2], sys.argv[3])
