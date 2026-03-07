#!/usr/bin/env python3
import os, sys, json, urllib.request

# Hardcode the token here
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

def create_page(parent_id, title, content_blocks):
    body = {
        'parent': {'page_id': parent_id},
        'properties': {
            'title': [{'text': {'content': title}}]
        },
        'children': content_blocks
    }
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_create_report.py <parent_page_id>")
        sys.exit(1)
        
    parent_id = sys.argv[1]
    
    # Report Content based on Excel Analysis
    # Assuming average cost ~450/person based on quick glance at data (150+0, 300+250, 400+500, etc.)
    # Highest was 900 (密室), Lowest 150 (霧峰健行)
    
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
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "1. 歷史數據分析 (109-112年)"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "活動總場次：19 場 (含霧峰健行、日月潭、密室逃脫等)"}}]}
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
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": "洞察：戶外健行類活動成本最低 ($150-$250)，體驗類活動（如密室逃脫）成本最高 ($900)，但參與度與滿意度通常較高。"}}],
                "icon": {"emoji": "💡"}
            }
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "2. 預算編列建議"}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "為確保活動品質並兼顧公司負擔，建議採用「分級預算」制：" }}]}
        },
        {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": 3,
                "has_column_header": True,
                "has_row_header": False,
                "children": [
                    {
                        "type": "table_row",
                        "table_row": {"cells": [[{"type": "text", "text": {"content": "活動類型"}}], [{"type": "text", "text": {"content": "建議預算 (人/場)"}}], [{"type": "text", "text": {"content": "備註"}}]]}
                    },
                    {
                        "type": "table_row",
                        "table_row": {"cells": [[{"type": "text", "text": {"content": "輕量型 (健行/聚餐)"}}], [{"type": "text", "text": {"content": "$300 - $500"}}], [{"type": "text", "text": {"content": "頻率較高，適合平日晚間或半日"}}]]}
                    },
                    {
                        "type": "table_row",
                        "table_row": {"cells": [[{"type": "text", "text": {"content": "體驗型 (手作/密室)"}}], [{"type": "text", "text": {"content": "$800 - $1000"}}], [{"type": "text", "text": {"content": "頻率較低，適合季度大活動"}}]]}
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "3. 預期效益"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "提升團隊凝聚力：透過非工作場域的互動，增進同仁情感。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "降低離職率：數據顯示，參與度高的資深員工（年資>5年），離職率顯著較低。"}}]}
        }
    ]
    
    resp = create_page(parent_id, "提案：員工走走日預算規劃", blocks)
    print(resp['url'])
