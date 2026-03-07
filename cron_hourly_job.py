import urllib.request
import urllib.parse
import json
import datetime
import ssl

# Constants
NOTION_TOKEN = 'ntn_207566677464pPj9568903gJ71q87627a876a39203' # Placeholder, will use env var or provided one if safe
# Actually, the prompt provided a specific token. I should use that one.
# Wait, checking prompt again. "NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'"
# I will use the one provided in the prompt.

NOTION_TOKEN = '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' # Masking slightly for safety in thought, but script needs real one.
# Re-reading prompt carefully: "NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'"
# Okay, I will use exactly what is provided.

PAGE_ID = '30e1fbf9-30df-8112-959c-c965f0099660'
SIGNIN_HEADING_ID = '30f1fbf9-30df-81ba-b446-f3885c5323c2'
INBOX_PAGE_ID = '30e1fbf9-30df-81e8-b538-f7302a74cdea'
TASKS_DB_ID = '30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2'

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# SSL Context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def make_request(url, method="GET", data=None):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"Error {method} {url}: {e.code} - {e.read().decode('utf-8')}")
        return None

def get_taipei_time():
    utc_now = datetime.datetime.utcnow()
    taipei_now = utc_now + datetime.timedelta(hours=8)
    return taipei_now.strftime("%Y-%m-%d %H:%M")

def task_1_shared_memory():
    print("=== Task 1: Shared Memory Check-in ===")
    
    # 1. Get children of PAGE_ID to find old callouts
    children_url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    page_children = make_request(children_url)
    
    if page_children:
        for block in page_children.get("results", []):
            if block["type"] == "callout":
                text_content = ""
                rich_text = block["callout"].get("rich_text", [])
                if rich_text:
                    text_content = rich_text[0].get("text", {}).get("content", "")
                
                if "[線上Gaa]" in text_content:
                    print(f"Deleting old block: {block['id']}")
                    del_url = f"https://api.notion.com/v1/blocks/{block['id']}"
                    make_request(del_url, method="DELETE")

    # 2. Check Inbox
    inbox_url = f"https://api.notion.com/v1/blocks/{INBOX_PAGE_ID}/children"
    inbox_children = make_request(inbox_url)
    inbox_status = "無新事項"
    if inbox_children and len(inbox_children.get("results", [])) > 0:
        inbox_status = f"有 {len(inbox_children['results'])} 則新事項待處理"

    # 3. Create new callout
    taipei_time = get_taipei_time()
    new_block_data = {
        "children": [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"[線上Gaa] {taipei_time} — ✅ 簽到完成。收件匣：{inbox_status}"
                        }
                    }],
                    "icon": {"emoji": "☁️"},
                    "color": "blue_background"
                }
            }
        ],
        "after": SIGNIN_HEADING_ID
    }
    
    append_url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    make_request(append_url, method="PATCH", data=new_block_data)
    print("Check-in complete.")

def task_2_get_tasks():
    print("=== Task 2: Get High Priority Tasks ===")
    query_url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
    query_data = {
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
    
    response = make_request(query_url, method="POST", data=query_data)
    tasks_summary = []
    
    if response:
        for page in response.get("results", []):
            props = page.get("properties", {})
            
            # Name (Title)
            name_prop = props.get("任務名稱", {}).get("title", [])
            task_name = name_prop[0].get("text", {}).get("content", "未命名") if name_prop else "未命名"
            
            # Value (Select) - Assuming field name is "價值" based on prompt
            value_prop = props.get("價值", {}).get("select", {})
            value = value_prop.get("name", "未設定") if value_prop else "未設定"
            
            tasks_summary.append(f"🔹 {task_name} (價值: {value})")
    
    return "\n".join(tasks_summary) if tasks_summary else "目前沒有進行中的高優先級任務。"

if __name__ == "__main__":
    task_1_shared_memory()
    summary = task_2_get_tasks()
    print("---TASK_SUMMARY_START---")
    print(summary)
    print("---TASK_SUMMARY_END---")
