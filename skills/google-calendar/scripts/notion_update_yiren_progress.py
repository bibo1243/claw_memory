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

def get_task_id_by_name(db_id, name):
    body = {
        'filter': {
            'property': 'Name',
            'title': {
                'equals': name
            }
        }
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    if data['results']:
        return data['results'][0]['id']
    return None

def append_progress_to_page(page_id):
    # Content based on recent interactions about "Yi-Ren Yong-Cheng"
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "今日進度 (2026-02-18)"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "核心概念確認：自主人生複利創造策略。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "代號設定：建立「藝人」代號，代表高維度策略思考模式。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "意圖層 (Intention) 定義："}}], "children": [
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "目標：突破人生最大關卡（戒色/能量轉移）。"}}]}
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "願景：成為有能量、不浪費時間、專注於熱愛事務的人。"}}]}
                }
            ]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "依靠層 (Support) 探索："}}], "children": [
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "既有依靠：半斷食、大誓願、公共環境。"}}]}
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "心流依靠 (新增)：寫作、靈性分享、唱歌、寫程式、成就感紀錄。"}}]}
                }
            ]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "系統化落地："}}], "children": [
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "建立 Notion 「自主人生戰略指揮中心」。"}}]}
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "建立 「Freedom Streak (自由天數)」 追蹤器。"}}]}
                }
            ]}
        }
    ]
    
    url = f"{BASE_URL}/blocks/{page_id}/children"
    return request('PATCH', url, json.dumps({'children': blocks}).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_update_yiren_progress.py <db_id>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    task_name = "易仁永澄工作規劃"
    
    task_id = get_task_id_by_name(db_id, task_name)
    if task_id:
        print(f"Updating task '{task_name}' (ID: {task_id})...")
        append_progress_to_page(task_id)
        print("Progress added.")
    else:
        print(f"Task '{task_name}' not found.")
