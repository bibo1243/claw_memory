#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import datetime
import ssl

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
PAGE_ID = '30e1fbf9-30df-8112-959c-c965f0099660'
SIGNIN_HEADING_ID = '30f1fbf9-30df-81ba-b446-f3885c5323c2'
INBOX_PAGE_ID = '30e1fbf9-30df-81e8-b538-f7302a74cdea'
TASKS_DB_ID = '30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2'

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def api(url, method="GET", data=None):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"HTTP {e.code} {method} {url}: {body[:500]}")
        return None

def taipei_now():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")

# ========== TASK 1: Shared Memory Check-in ==========
print("=== TASK 1: 共享記憶簽到 ===")

# Step 1: Find & delete old 線上Gaa callouts
base = "https://api.notion.com/v1"
children = api(f"{base}/blocks/{PAGE_ID}/children?page_size=100")
deleted = 0
if children:
    for b in children.get("results", []):
        if b.get("type") == "callout":
            rt = b["callout"].get("rich_text", [])
            txt = rt[0].get("text", {}).get("content", "") if rt else ""
            if "[線上Gaa]" in txt:
                api(f"{base}/blocks/{b['id']}", method="DELETE")
                deleted += 1
                print(f"  Deleted old callout: {b['id']}")
print(f"  Deleted {deleted} old callout(s)")

# Step 2: Check Inbox
inbox = api(f"{base}/blocks/{INBOX_PAGE_ID}/children?page_size=100")
inbox_count = 0
if inbox:
    for b in inbox.get("results", []):
        if b.get("type") not in ("child_page", "child_database", None):
            # skip structural blocks, count content
            inbox_count += 1
inbox_status = f"有 {inbox_count} 則內容" if inbox_count > 0 else "無新事項"
print(f"  Inbox: {inbox_status}")

# Step 3: Create new callout after heading
t = taipei_now()
callout_data = {
    "children": [
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"[線上Gaa] {t} — ✅ 簽到完成。收件匣：{inbox_status}"}
                }],
                "icon": {"emoji": "☁️"},
                "color": "blue_background"
            }
        }
    ],
    "after": SIGNIN_HEADING_ID
}
result = api(f"{base}/blocks/{PAGE_ID}/children", method="PATCH", data=callout_data)
if result:
    print("  ✅ Check-in callout created!")
else:
    print("  ❌ Failed to create callout")

# ========== TASK 2: Query high-priority tasks ==========
print("\n=== TASK 2: 查詢高優先級任務 ===")
query_data = {
    "filter": {
        "and": [
            {"property": "狀態", "select": {"equals": "進行中"}},
            {"property": "優先級", "select": {"equals": "高"}}
        ]
    },
    "page_size": 5
}
resp = api(f"{base}/databases/{TASKS_DB_ID}/query", method="POST", data=query_data)
tasks = []
if resp:
    for page in resp.get("results", [])[:2]:
        props = page.get("properties", {})
        # Try common title field names
        name = "未命名"
        for key in ["任務名稱", "Name", "名稱", "title", "Task"]:
            if key in props and props[key].get("type") == "title":
                title_arr = props[key].get("title", [])
                if title_arr:
                    name = title_arr[0].get("text", {}).get("content", "未命名")
                break
        # Value field
        value = "未設定"
        if "價值" in props:
            vp = props["價值"].get("select")
            if vp:
                value = vp.get("name", "未設定")
        tasks.append(f"🔹 {name}（價值：{value}）")
        print(f"  Found task: {name}")

if not tasks:
    print("  No high-priority in-progress tasks found.")

task_summary = "\n".join(tasks) if tasks else "目前沒有「進行中 + 高優先級」的任務。"
print(f"\n---TASK_SUMMARY---\n{task_summary}\n---END---")
