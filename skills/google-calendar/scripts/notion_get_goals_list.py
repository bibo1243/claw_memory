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

def get_all_goals(db_id):
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps({}).encode('utf-8'))
    goals = []
    for page in data.get('results', []):
        title = page['properties']['Name']['title'][0]['text']['content']
        page_id = page['id']
        goals.append({'id': page_id, 'title': title})
    return goals

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_get_goals_list.py <db_id>")
        sys.exit(1)
        
    goals = get_all_goals(sys.argv[1])
    print(json.dumps(goals))
