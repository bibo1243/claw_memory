import urllib.request, json, os

token = "ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR"
headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}

print("--- INBOX ITEMS ---")
inbox_id = "30e1fbf9-30df-81e8-b538-f7302a74cdea"
req = urllib.request.Request(f"https://api.notion.com/v1/blocks/{inbox_id}/children", headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        for block in data.get("results", []):
            if "paragraph" in block:
                text = "".join([t["plain_text"] for t in block["paragraph"].get("rich_text", [])])
                if text: print(f"- {text}")
            elif "to_do" in block:
                text = "".join([t["plain_text"] for t in block["to_do"].get("rich_text", [])])
                if text: print(f"- [ ] {text}")
except Exception as e:
    print(f"Error fetching inbox: {e}")

print("--- RECENT TASKS ---")
db_id = "30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2"
query = {"filter": {"property": "Status", "status": {"equals": "Not started"}}}
req = urllib.request.Request(f"https://api.notion.com/v1/databases/{db_id}/query", data=json.dumps(query).encode("utf-8"), headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        for page in data.get("results", [])[:10]:
            props = page.get("properties", {})
            title_prop = props.get("Name", props.get("Task name", props.get("title", {})))
            if "title" in title_prop:
                title = "".join([t["plain_text"] for t in title_prop["title"]])
                print(f"- {title}")
except Exception as e:
    print(f"Error fetching tasks: {e}")
