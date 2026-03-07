#!/usr/bin/env python3
"""Find and delete recently created tasks from Tasks DB that should be inside the planning page."""
import json, urllib.request, sys

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
DB_ID = '30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2'  # Tasks (每日行動)
PLANNING_PAGE_ID = '30d1fbf9-30df-81bb-9dc5-d6a2418dc5f3'  # 近一個月的任務規劃

BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

# Tasks to find and delete (created by mistake in outer list)
TASKS_TO_DELETE = [
    "購買休閒上衣 (補充斷捨離後的空缺)",
    "鞋子補色",
    "研究電子紙螢幕的小型安卓手機 (護眼用)",
    "購買並佈置家裡植栽",
    "預約整脊與溫灸 (需先確認存錢狀況)",
    "預約牙醫修補牙齒",
    "完成蔡小姐捐贈的處理",
    "準備組織發展會議議題 (預先思考)",
    "蓮友慈益基金會兩間房子問題處理",
    "員工旅遊處理",
    "追蹤人資系統進度",
    "發佈年度行事曆",
    "關注勞動檢查結果並因應",
    "查看衛生準備內容 (與淑錡討論前置)",
    "與淑錡討論人資系統進度",
    "建構倉庫整理系統 (授權紀騰執行)",
    "規劃資深團隊行政組培育計畫",
    "安排與有才華夥伴的談話 (培育)",
    "構思機構資訊系統開發 (運用自動化技能)",
]

def api(method, url, data=None):
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        print(f'HTTP error {e.code}: {e.read().decode()}', file=sys.stderr)
        return None

def archive_page(page_id):
    """Archive (soft-delete) a page."""
    body = json.dumps({"archived": True}).encode('utf-8')
    return api('PATCH', f'{BASE_URL}/pages/{page_id}', body)

# Query all recent tasks
body = {
    'sorts': [{'timestamp': 'created_time', 'direction': 'descending'}],
    'page_size': 30
}
data = api('POST', f'{BASE_URL}/databases/{DB_ID}/query', json.dumps(body).encode('utf-8'))

if not data:
    print("Failed to query database")
    sys.exit(1)

deleted = 0
for page in data['results']:
    page_id = page['id']
    # Skip the planning page itself
    if page_id.replace('-', '') == PLANNING_PAGE_ID.replace('-', ''):
        continue
    
    props = page['properties']
    title = ""
    for prop_name, prop_val in props.items():
        if prop_val['type'] == 'title' and prop_val['title']:
            title = prop_val['title'][0]['plain_text']
            break
    
    if title in TASKS_TO_DELETE:
        result = archive_page(page_id)
        if result:
            print(f"✅ Archived: {title}")
            deleted += 1
        else:
            print(f"❌ Failed: {title}")

print(f"\nTotal archived: {deleted}/{len(TASKS_TO_DELETE)}")
