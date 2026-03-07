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

def get_latest_task_id(db_id):
    body = {
        'sorts': [{'timestamp': 'created_time', 'direction': 'descending'}],
        'page_size': 1
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    if data['results']:
        return data['results'][0]['id']
    return None

def append_blocks_to_page(page_id, blocks):
    url = f"{BASE_URL}/blocks/{page_id}/children"
    return request('PATCH', url, json.dumps({'children': blocks}).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: notion_append_report.py <db_id> <excel_file_id>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    excel_file_id = sys.argv[2]
    
    task_id = get_latest_task_id(db_id)
    if not task_id:
        print("No task found.")
        sys.exit(1)
        
    print(f"Appending report to Task ID: {task_id}")
    
    # Report Blocks
    blocks = [
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": "員工走走日：活動成效與預算提案"}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "本報告旨在分析過去 6 年（109-112年）員工走走日之活動數據，並據此提出未來預算編列建議。"}}]}
        },
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": "📄 原始數據檔案已附於下方"}}],
                "icon": {"emoji": "📎"}
            }
        },
        # Google Drive Embed for Excel
        {
            "object": "block",
            "type": "embed",
            "embed": {
                "url": f"https://docs.google.com/spreadsheets/d/{excel_file_id}"
            }
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "1. 歷史數據分析 (109-112年)"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "活動總場次：19 場"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "人均成本區間：$150 ~ $900 元"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "平均單場花費：約 $400 - $500 元/人"}}]}
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "2. 預算編列建議"}}]}
        },
        {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": 2,
                "has_column_header": True,
                "has_row_header": False,
                "children": [
                    {
                        "type": "table_row",
                        "table_row": {"cells": [[{"type": "text", "text": {"content": "活動類型"}}], [{"type": "text", "text": {"content": "建議預算"}}]]}
                    },
                    {
                        "type": "table_row",
                        "table_row": {"cells": [[{"type": "text", "text": {"content": "輕量型"}}], [{"type": "text", "text": {"content": "$300 - $500"}}]]}
                    },
                    {
                        "type": "table_row",
                        "table_row": {"cells": [[{"type": "text", "text": {"content": "體驗型"}}], [{"type": "text", "text": {"content": "$800 - $1000"}}]]}
                    }
                ]
            }
        }
    ]
    
    append_blocks_to_page(task_id, blocks)
    print("Report content added.")
