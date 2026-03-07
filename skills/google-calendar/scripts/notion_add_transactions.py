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

def create_database(parent_page_id, title, properties):
    body = {
        'parent': {'type': 'page_id', 'page_id': parent_page_id},
        'title': [{'type': 'text', 'text': {'content': title}}],
        'properties': properties
    }
    url = f"{BASE_URL}/databases"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_add_transactions.py <page_id>")
        sys.exit(1)
        
    root_page_id = sys.argv[1]
    
    # --- Transactions Schema ---
    print("Creating 'Transactions' Database...")
    TRANSACTIONS_PROPS = {
        'Item': {'title': {}},
        'Amount': {'number': {'format': 'dollar'}},
        'Date': {'date': {}},
        'Category': {'select': {'options': [
            {'name': '食 (三餐/飲料)', 'color': 'orange'},
            {'name': '衣 (服飾)', 'color': 'pink'},
            {'name': '住 (水電/日用/3C)', 'color': 'blue'},
            {'name': '行 (個人交通/加油/洗車)', 'color': 'green'},
            {'name': '育 (書籍/課程)', 'color': 'purple'},
            {'name': '樂 (娛樂/旅遊)', 'color': 'yellow'},
            {'name': '公務餐飲', 'color': 'gray'},
            {'name': '差旅交通', 'color': 'brown'},
            {'name': '交際應酬', 'color': 'red'},
            {'name': '辦公雜支', 'color': 'default'}
        ]}},
        'Value Analysis': {'select': {'options': [
            {'name': '高價值', 'color': 'green'},
            {'name': '低價值', 'color': 'red'}
        ]}},
        'Note': {'rich_text': {}},
        'Receipt': {'files': {}}  # For uploading compressed images
    }
    
    trans_db = create_database(root_page_id, "Transactions (記帳明細)", TRANSACTIONS_PROPS)
    trans_id = trans_db['id']
    print(f"   Created: {trans_id}")

    print("\n--- Transactions Database Added ---")
