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

def add_relation_to_goals(tasks_db_id, goals_db_id):
    body = {
        'properties': {
            'Goal Relation': {
                'relation': {
                    'database_id': goals_db_id,
                    'type': 'dual_property',
                    'dual_property': {}
                }
            },
            'Calories': {
                'number': {'format': 'number'}
            }
        }
    }
    request('PATCH', f"{BASE_URL}/databases/{tasks_db_id}", json.dumps(body).encode('utf-8'))
    print("Added 'Goal Relation' and 'Calories' properties to Tasks DB.")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: notion_link_tasks_to_goals.py <tasks_db_id> <goals_db_id>")
        sys.exit(1)
        
    tasks_id = sys.argv[1]
    goals_id = sys.argv[2]
    
    add_relation_to_goals(tasks_id, goals_id)
