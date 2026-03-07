#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
from datetime import datetime

# Load env
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    os.environ[parts[0]] = parts[1]

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

TOKEN = os.environ.get('NOTION_TOKEN')
# Use a specific page or DB for "Gaa 承諾表"
# If we don't have a DB ID yet, we can create a page with a simple table block.
TARGET_PAGE_ID = os.environ.get('NOTION_PAGE_ID', '30a1fbf9-30df-80bb-93b2-f0168cc87701')

if not TOKEN:
    print("Error: NOTION_TOKEN not set.")
    sys.exit(1)

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def create_commitment_table(commitments):
    # Create a new page or append to an existing one
    # Let's append a Table block to the target page
    
    rows = []
    # Header row
    rows.append({
        "type": "table_row",
        "table_row": {
            "cells": [
                [{"type": "text", "text": {"content": "來源群組"}}],
                [{"type": "text", "text": {"content": "承諾者"}}],
                [{"type": "text", "text": {"content": "內容"}}],
                [{"type": "text", "text": {"content": "日期"}}],
                [{"type": "text", "text": {"content": "狀態"}}]
            ]
        }
    })
    
    for c in commitments:
        rows.append({
            "type": "table_row",
            "table_row": {
                "cells": [
                    [{"type": "text", "text": {"content": c.get('source', '')}}],
                    [{"type": "text", "text": {"content": c.get('person', '')}}],
                    [{"type": "text", "text": {"content": c.get('content', '')}}],
                    [{"type": "text", "text": {"content": c.get('date', '')}}],
                    [{"type": "text", "text": {"content": "待確認"}}] # Default status
                ]
            }
        })

    # Create Table Block
    table_block = {
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": f"Gaa 承諾挖掘報告 ({datetime.now().strftime('%Y-%m-%d')})"}}]
                }
            },
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 5,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": rows
                }
            }
        ]
    }
    
    url = f"https://api.notion.com/v1/blocks/{TARGET_PAGE_ID}/children"
    try:
        req = urllib.request.Request(url, json.dumps(table_block).encode('utf-8'), HEADERS, method='PATCH')
        with urllib.request.urlopen(req) as response:
            res = json.load(response)
            print("✅ Notion Table Created successfully.")
            # Construct URL to the block/page
            print(f"Check Notion Page: https://www.notion.so/{TARGET_PAGE_ID.replace('-', '')}")
    except urllib.error.HTTPError as e:
        print(f"Error creating table: {e.read().decode()}")

if __name__ == "__main__":
    # Mock data for testing based on previous scan
    mock_data = [
        {"source": "慈光核心主管", "person": "廖慧雯", "content": "後續會進行繳費及...", "date": "2023-10-26"},
        {"source": "少年家園", "person": "鍾宜珮", "content": "明天會當其面前與他和主責社工再次約定", "date": "2020-10-02"},
        {"source": "少年家園", "person": "Gary (User)", "content": "收到，婉勳部份我再跟工讀的夥伴說明", "date": "2020-10-04"}
    ]
    create_commitment_table(mock_data)
