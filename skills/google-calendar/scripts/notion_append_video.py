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

def append_video_description(page_id, description):
    blocks = [
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "📹 影片紀錄"}}]}
        },
        {
            "object": "block",
            "type": "quote",
            "quote": {"rich_text": [{"type": "text", "text": {"content": description}}]}
        }
    ]
    
    url = f"{BASE_URL}/blocks/{page_id}/children"
    return request('PATCH', url, json.dumps({'children': blocks}).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: notion_append_video.py <db_id> <task_name>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    name = sys.argv[2]
    # Hardcoded description for this specific video since we can't upload video files directly to Notion API (easily) without hosting first.
    # We will just log the description for now as requested.
    description = "影片紀錄：Gary 戴著黑框眼鏡，穿著深色外套，在看似賣場或倉庫的空間。起初低頭，隨後抬頭對著鏡頭露出自信且放鬆的微笑。象徵告別舊習慣後的踏實與新開始。"
    
    task_id = get_task_id_by_name(db_id, name)
    if task_id:
        print(f"Appending video info to task '{name}'...")
        append_video_description(task_id, description)
        print("Done.")
    else:
        print("Task not found.")
