import urllib.request, json
from datetime import datetime, timezone, timedelta

token = "ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR"
headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}

# Fetch Inbox
inbox_items = []
inbox_id = "30e1fbf9-30df-81e8-b538-f7302a74cdea"
req = urllib.request.Request(f"https://api.notion.com/v1/blocks/{inbox_id}/children", headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        for block in data.get("results", []):
            b_type = block["type"]
            if b_type in ["paragraph", "to_do", "bulleted_list_item", "numbered_list_item", "toggle"]:
                text_content = "".join([t["plain_text"] for t in block[b_type].get("rich_text", [])])
                if text_content and "在此頁 append 建議" not in text_content and text_content.strip() != "":
                    inbox_items.append(text_content)
except Exception as e:
    pass

# Fetch Tasks
tasks = []
db_id = "30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2"
query = {
    "filter": {
        "and": [
            {"property": "狀態", "select": {"does_not_equal": "Done"}},
            {"property": "狀態", "select": {"does_not_equal": "已完成"}},
            {"property": "狀態", "select": {"does_not_equal": "完成"}},
            {"property": "狀態", "select": {"does_not_equal": "已封存"}}
        ]
    },
    "sorts": [{"property": "建立時間", "direction": "descending"}],
    "page_size": 15
}
req = urllib.request.Request(f"https://api.notion.com/v1/databases/{db_id}/query", data=json.dumps(query).encode("utf-8"), headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        for page in data.get("results", []):
            props = page.get("properties", {})
            title = "未命名任務"
            status = "無狀態"
            
            title_prop = props.get("名稱", {})
            if "title" in title_prop and len(title_prop["title"]) > 0:
                title = title_prop["title"][0]["plain_text"]
                
            status_prop = props.get("狀態", {})
            if "select" in status_prop and status_prop.get("select"):
                status = status_prop["select"]["name"]
                
            tasks.append(f"- [ ] {title} ({status})")
except Exception as e:
    tasks.append(f"讀取任務失敗: {e}")

tz_taipei = timezone(timedelta(hours=8))
taipei_time = datetime.now(tz_taipei).strftime('%Y-%m-%d %H:%M')

report = f"🔔 **【整點任務追蹤與統整報告 {taipei_time}】**\n\n"
report += "**📥 記憶收件匣 (待審核建議):**\n"
if inbox_items:
    report += "\n".join([f"- {item}" for item in inbox_items]) + "\n"
else:
    report += "- 目前無新建議待審核\n"

report += "\n**📋 進行中/近期任務追蹤:**\n"
if tasks:
    report += "\n".join(tasks) + "\n"
else:
    report += "- 無進行中任務\n"

report += "\n**🏃 下一步行動提醒:**\n"
report += "- 請確認今日高優先級任務是否已推進。\n"
report += "- 提醒：每次任務執行後，可思考「這件事服務哪個價值？」並標記於任務上。\n"

print(report)
