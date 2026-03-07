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

def append_blocks_to_page(page_id, blocks):
    url = f"{BASE_URL}/blocks/{page_id}/children"
    return request('PATCH', url, json.dumps({'children': blocks}).encode('utf-8'))

if __name__ == '__main__':
    # No args needed, hardcoded specific logic for this report
    if len(sys.argv) < 2:
        print("Usage: notion_append_analysis.py <page_id>")
        sys.exit(1)
        
    page_id = sys.argv[1]
    
    # Analysis Report Blocks
    blocks = [
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": "本報告依據 Gary 2026 年度核心意圖：「能量轉移 (Energy Shift)」與「藝人模組 (Artist Model)」進行優先級評估。"}}],
                "icon": {"emoji": "💡"}
            }
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "核心高價值活動 (High Leverage)"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "3/17, 3/10 組織督導會議 (張貴傑老師) - ⭐⭐⭐⭐⭐ (5.0)\n組織頂層設計與核心幹部培育，關鍵戰場。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "2/24, 3/3, 3/24, 3/31 瑜珈課 - ⭐⭐⭐⭐⭐ (5.0)\n身心能量覺察與累積，直接支援年度戒色與能量目標。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "3/30 慈馨念佛班會 - ⭐⭐⭐⭐⭐ (5.0)\n穩定心性與能量轉移的關鍵儀式。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "2/23 組織發展會議 - ⭐⭐⭐⭐⭐ (5.0)\n機構未來方向定調。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "2/18 和家人一起運動 - ⭐⭐⭐⭐⭐ (5.0)\n家庭關係與健康，藝人模組基石。"}}]}
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "必要營運與重要儀式 (Must Have)"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "2/26, 3/26 慈光核心主管會議 - ⭐⭐⭐⭐ (4.0)\n重要佈達與整合，需出席但偏向執行層面。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "2/23 溫灸（第二次） - ⭐⭐⭐⭐ (4.0)\n身體修復，維持高能量狀態的必要保養。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "3/20-22 深圳之旅 - ⭐⭐⭐⭐ (4.0)\n充電與視野拓展。"}}]}
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "需警覺區：行政與瑣事 (Low Leverage)"}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "⚠️ 建議授權給副組長淑錡或相關股長處理，避免佔用「創造性時間」。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "3/6 庶務股倉庫整理 - ⭐⭐ (2.0)\n純行政執行事務，應授權。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "3/1, 3/19 兩棟設施社被財產盤點 - ⭐⭐ (2.0)\n耗時且低產值，建議只看結果報告。"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "2/12 地籍圖重測作業宣導會 - ⭐⭐ (2.5)\n了解結果即可，無需親自出席宣導會。"}}]}
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "下一步行動 (Next Steps)"}}]}
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [{"type": "text", "text": {"content": "確認「行政瑣事」類別是否可全權交辦淑錡？"}}]}
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [{"type": "text", "text": {"content": "預留 3/17 督導會議前後的「空白時間」進行準備與反思。"}}]}
        }
    ]
    
    append_blocks_to_page(page_id, blocks)
    print("Report content appended.")
