import os, urllib.request, json

def load_env():
    try:
        with open('.env') as f:
            for l in f:
                if '=' in l and not l.startswith('#'):
                    k,v=l.strip().split('=',1)
                    os.environ[k.strip()]=v.strip().strip("'\"")
    except: pass

load_env()
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

db_id = "30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2"

search_req = urllib.request.Request(
    f"https://api.notion.com/v1/databases/{db_id}/query",
    headers=HEADERS,
    method='POST',
    data=json.dumps({
        "filter": {
            "property": "名稱",
            "title": {
                "contains": "鳳翎與吳小姐"
            }
        }
    }).encode('utf-8')
)

try:
    res = json.loads(urllib.request.urlopen(search_req).read().decode('utf-8'))
    results = res.get("results", [])
    if not results:
        print("Task not found.")
    else:
        for task in results:
            task_id = task["id"]
            name = task["properties"]["名稱"]["title"][0]["plain_text"]
            
            update_req = urllib.request.Request(
                f"https://api.notion.com/v1/pages/{task_id}",
                headers=HEADERS,
                method='PATCH',
                data=json.dumps({
                    "properties": {
                        "狀態": {
                            "select": {
                                "name": "✅ 完成"
                            }
                        }
                    }
                }).encode('utf-8')
            )
            update_res = urllib.request.urlopen(update_req)
            print(f"Successfully updated task: {name} to Done.")
except Exception as e:
    err_msg = getattr(e, 'read', lambda: str(e))()
    if isinstance(err_msg, bytes):
        err_msg = err_msg.decode()
    print("Error:", err_msg)
