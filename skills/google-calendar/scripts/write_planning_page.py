#!/usr/bin/env python3
"""Append structured GTD tasks as to-do blocks inside the planning page."""
import json, urllib.request, sys

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
PAGE_ID = '30d1fbf9-30df-81bb-9dc5-d6a2418dc5f3'
BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

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

def heading(text, level=2):
    return {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def todo(text, checked=False):
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "checked": checked
        }
    }

def paragraph(text):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

# First, delete existing child blocks to avoid duplication
existing = api('GET', f'{BASE_URL}/blocks/{PAGE_ID}/children?page_size=100')
if existing and existing.get('results'):
    for block in existing['results']:
        api('DELETE', f'{BASE_URL}/blocks/{block["id"]}')
    print(f"Cleared {len(existing['results'])} existing blocks.")

blocks = [
    heading("🧠 GTD 大腦掃除 — 近一個月任務規劃", 1),
    paragraph("收集日期：2026-02-20 | 狀態：收集中 (Capture Phase)"),
    divider(),

    heading("🛒 第一層：個人與健康 (Personal & Health)"),
    heading("購物清單 (Shopping)", 3),
    todo("購買休閒上衣 (補充斷捨離後的空缺)"),
    todo("鞋子補色"),
    todo("研究電子紙螢幕的小型安卓手機 (護眼用)"),
    todo("購買並佈置家裡植栽"),

    heading("身體修復 (Health)", 3),
    todo("預約整脊與溫灸 (需先確認存錢狀況)"),
    todo("預約牙醫修補牙齒 (優先級高，避免惡化)"),
    todo("剪頭髮 (過年後行程)"),

    heading("運動打卡 (Habit)", 3),
    todo("每日晨間運動 06:30-07:30 (建立打卡機制)"),

    divider(),

    heading("💼 第二層：工作與專案 (Work & Projects)"),
    heading("急迫死線 (Deadlines)", 3),
    todo("完成蔡小姐捐贈的處理"),
    todo("準備組織發展會議議題 — 下週一，週六日要先跑完，最好今天開始思考"),
    todo("蓮友慈益基金會兩間房子問題處理"),
    todo("員工旅遊處理"),
    todo("追蹤人資系統進度"),
    todo("發佈年度行事曆"),
    todo("關注勞動檢查結果並因應"),

    heading("團隊與人 (People)", 3),
    todo("查看衛生準備內容 (與淑錡討論前置) — 今天要先看"),
    todo("與淑錡討論人資系統進度"),
    todo("建構倉庫整理系統 (授權紀騰執行，需先建系統)"),

    heading("會議與培育 (Meetings & Development)", 3),
    todo("規劃資深團隊行政組培育計畫"),
    todo("安排與有才華夥伴的談話 (培育)"),

    heading("組織發展 (Big Picture)", 3),
    todo("構思機構資訊系統開發 (運用自動化技能)"),
    todo("設計組織例行事項管理系統"),
    todo("建立各單位工作狀態掌控機制 — 後退一個高度檢視組織"),

    divider(),

    heading("🔄 第三層：待收集 (To Be Captured)"),
    paragraph("以下面向尚未梳理，待 Gary 繼續倒出："),
    todo("💰 財務與存錢計畫"),
    todo("📚 學習與成長 (藝人模組、自動化技能)"),
    todo("🏠 家庭與生活環境"),
    todo("🤝 人際關係"),
    todo("🎯 年度核心意圖 (戒色 / 能量轉移)"),
]

# Notion API limits to 100 blocks per call
batch_size = 100
for i in range(0, len(blocks), batch_size):
    batch = blocks[i:i+batch_size]
    body = json.dumps({"children": batch}).encode('utf-8')
    result = api('PATCH', f'{BASE_URL}/blocks/{PAGE_ID}/children', body)
    if result:
        print(f"Appended batch {i//batch_size + 1}: {len(batch)} blocks")
    else:
        print(f"Failed batch {i//batch_size + 1}")

print("Done!")
