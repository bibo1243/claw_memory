import os
import urllib.request
import json

def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    os.environ[k.strip()] = v.strip().strip("'\"")
    except FileNotFoundError:
        pass

load_env()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_blocks(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print("Error getting blocks:", getattr(e, 'read', lambda: b'')().decode())
        return {}

inbox_data = get_blocks("30e1fbf9-30df-81e8-b538-f7302a74cdea")
print("=== 收件匣 (Inbox) ===")
if "results" in inbox_data:
    for b in inbox_data["results"]:
        type = b.get("type")
        if type in b:
            text_arr = b[type].get("rich_text", [])
            text = "".join([t.get("plain_text", "") for t in text_arr])
            if text:
                print(f"- {text}")

def query_db_no_filter(db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    req = urllib.request.Request(url, headers=HEADERS, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print("Error querying db:", getattr(e, 'read', lambda: b'')().decode())
        return {}

print("\n=== 目前待辦事項 (Tasks Properties) ===")
task_data = query_db_no_filter("30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2")
if "results" in task_data and task_data["results"]:
    first = task_data["results"][0]
    for k, v in first.get("properties", {}).items():
        print(f"Property: {k}, Type: {v.get('type')}")
    
    print("\n--- Recent Tasks ---")
    for r in task_data["results"][:15]:
        props = r.get("properties", {})
        name = "Unknown"
        status = "Unknown"
        for k, v in props.items():
            if v.get("type") == "title" and v.get("title"):
                name = v["title"][0].get("plain_text", "")
            elif v.get("type") == "status" and v.get("status"):
                status = v["status"].get("name", "")
            elif v.get("type") == "checkbox" and k == "Done":
                if v.get("checkbox"):
                    status = "Done"
                else:
                    status = "Not Done"
        print(f"- [{status}] {name}")