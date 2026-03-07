import urllib.request
import json
import datetime
import os

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
PAGE_ID = '30e1fbf9-30df-8112-959c-c965f0099660'
SIGNIN_HEADING_ID = '30f1fbf9-30df-81ba-b446-f3885c5323c2'
INBOX_PAGE_ID = '30e1fbf9-30df-81e8-b538-f7302a74cdea'
TASKS_DB_ID = '30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2'

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def request_notion(method, endpoint, data=None):
    url = f"https://api.notion.com/v1/{endpoint}"
    if data:
        data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode('utf-8')}")
        return None

# 1. Get current Sign-in blocks to delete old ones
print("Fetching existing blocks...")
children = request_notion("GET", f"blocks/{PAGE_ID}/children?page_size=100")
if children:
    for block in children.get("results", []):
        if block["type"] == "callout":
            text_content = ""
            try:
                text_content = block["callout"]["rich_text"][0]["text"]["content"]
            except (KeyError, IndexError):
                pass
            
            if "[線上Gaa]" in text_content:
                print(f"Deleting old block: {block['id']}")
                request_notion("DELETE", f"blocks/{block['id']}")

# 2. Check Inbox
print("Checking Inbox...")
inbox_children = request_notion("GET", f"blocks/{INBOX_PAGE_ID}/children?page_size=100")
inbox_status = "無新事項"
if inbox_children and inbox_children.get("results"):
    # Filter out empty blocks if necessary, but simple count works for now
    count = len(inbox_children["results"])
    if count > 0:
        # Check if they are just empty paragraphs
        has_content = False
        for b in inbox_children["results"]:
             if b['type'] == 'paragraph' and not b['paragraph']['rich_text']:
                 continue
             has_content = True
             break
        if has_content:
             inbox_status = f"有 {count} 則新事項"

# 3. Create new Sign-in block
utc_now = datetime.datetime.utcnow()
taipei_time = utc_now + datetime.timedelta(hours=8)
time_str = taipei_time.strftime("%Y-%m-%d %H:%M")
content_text = f"[線上Gaa] {time_str} — ✅ 簽到完成。收件匣：{inbox_status}"

print(f"Creating new sign-in: {content_text}")
new_block_data = {
    "children": [
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": content_text
                    }
                }],
                "icon": {
                    "emoji": "☁️"
                },
                "color": "blue_background"
            }
        }
    ],
    "after": SIGNIN_HEADING_ID
}

# Use the specific endpoint for appending children
request_notion("PATCH", f"blocks/{PAGE_ID}/children", new_block_data)

# 4. Fetch Tasks for Reminder (Task 2 part 1)
print("Fetching Tasks...")
# Filter: 狀態 = 進行中 AND 優先級 = 高
# Note: Adjust property names based on actual DB schema if different. 
# Prompt says "狀態 select = '進行中' AND 優先級 select = '高'"
filter_payload = {
    "filter": {
        "and": [
            {
                "property": "狀態",
                "select": {
                    "equals": "進行中"
                }
            },
            {
                "property": "優先級",
                "select": {
                    "equals": "高"
                }
            }
        ]
    },
    "page_size": 2
}

tasks_resp = request_notion("POST", f"databases/{TASKS_DB_ID}/query", filter_payload)
task_summary = "目前沒有高優先級的進行中任務。"

if tasks_resp and tasks_resp.get("results"):
    task_list = []
    for t in tasks_resp["results"]:
        try:
            # Title property is usually "Name" or "Task Name", but let's check "Name" or "標題" or iterate
            title = "未命名任務"
            props = t["properties"]
            # Find the title property
            for key, val in props.items():
                if val["type"] == "title" and val["title"]:
                    title = val["title"][0]["text"]["content"]
                    break
            task_list.append(f"• {title}")
        except Exception as e:
            continue
    if task_list:
        task_summary = "\n".join(task_list)

print("TASK_SUMMARY_START")
print(task_summary)
print("TASK_SUMMARY_END")

