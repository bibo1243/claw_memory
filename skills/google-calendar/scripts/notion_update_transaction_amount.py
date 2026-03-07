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

def get_transaction_id_by_item(db_id, item_name):
    # Find the latest transaction with this name
    body = {
        'filter': {
            'property': 'Item',
            'title': {
                'equals': item_name
            }
        },
        'sorts': [
            {
                'timestamp': 'created_time',
                'direction': 'descending'
            }
        ],
        'page_size': 1
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    if data['results']:
        return data['results'][0]['id']
    return None

def update_transaction_amount(page_id, amount):
    body = {
        'properties': {
            'Amount': {'number': amount}
        }
    }
    url = f"{BASE_URL}/pages/{page_id}"
    return request('PATCH', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: notion_update_transaction_amount.py <db_id> <item_name> <new_amount>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    item_name = sys.argv[2]
    new_amount = float(sys.argv[3])
    
    page_id = get_transaction_id_by_item(db_id, item_name)
    if page_id:
        print(f"Updating transaction '{item_name}' (ID: {page_id}) to ${new_amount}...")
        update_transaction_amount(page_id, new_amount)
        print("Done.")
    else:
        print(f"Transaction '{item_name}' not found.")
