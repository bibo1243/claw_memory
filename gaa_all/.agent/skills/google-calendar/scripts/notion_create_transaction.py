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

def add_transaction(database_id, item, amount, date, category, value_analysis, note, receipt_url=None):
    body = {
        'parent': {'database_id': database_id},
        'properties': {
            'Item': {'title': [{'text': {'content': item}}]},
            'Amount': {'number': amount},
            'Date': {'date': {'start': date}},
            'Category': {'select': {'name': category}},
            'Value Analysis': {'select': {'name': value_analysis}},
            'Note': {'rich_text': [{'text': {'content': note}}]}
        }
    }
    
    if receipt_url:
        body['properties']['Receipt'] = {
            'files': [
                {
                    'name': 'receipt.jpg',
                    'type': 'external',
                    'external': {'url': receipt_url}
                }
            ]
        }
        
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 8:
        print("Usage: notion_create_transaction.py <db_id> <item> <amount> <date> <category> <value> <note> [receipt_url]")
        sys.exit(1)
        
    db_id = sys.argv[1]
    item = sys.argv[2]
    amount = float(sys.argv[3])
    date = sys.argv[4]
    category = sys.argv[5]
    value_analysis = sys.argv[6]
    note = sys.argv[7]
    receipt_url = sys.argv[8] if len(sys.argv) > 8 else None
    
    print(f"Adding transaction '{item}' to Notion...")
    add_transaction(db_id, item, amount, date, category, value_analysis, note, receipt_url)
    print("Done.")
