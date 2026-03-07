#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}
SHEETS_BASE_URL = 'https://sheets.googleapis.com/v4/spreadsheets'

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

def get_google_access_token():
    token = os.getenv('GOOGLE_ACCESS_TOKEN')
    if not token:
        sys.stderr.write('Error: GOOGLE_ACCESS_TOKEN env var not set\n')
        sys.exit(1)
    return token

def google_request(method, url, data=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {get_google_access_token()}')
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

# Notion Update
def update_notion_note(db_id, item_name, new_note):
    # Find page
    body = {
        'filter': {
            'property': 'Item',
            'title': {
                'equals': item_name
            }
        },
        'sorts': [{'timestamp': 'created_time', 'direction': 'descending'}],
        'page_size': 1
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    if data['results']:
        page_id = data['results'][0]['id']
        update_body = {
            'properties': {
                'Note': {'rich_text': [{'text': {'content': new_note}}]}
            }
        }
        request('PATCH', f"{BASE_URL}/pages/{page_id}", json.dumps(update_body).encode('utf-8'))
        print("Notion updated.")
    else:
        print("Notion transaction not found.")

# Google Sheet Update
def update_sheet_note(spreadsheet_id, sheet_name, item_name, new_note):
    # Find row index
    range_name = f"{sheet_name}!B:B"
    encoded_range = urllib.parse.quote(range_name)
    url = f"{SHEETS_BASE_URL}/{spreadsheet_id}/values/{encoded_range}"
    resp = google_request('GET', url)
    values = resp.get('values', [])
    
    row_index = -1
    for i, row in enumerate(values):
        # Searching from end to find latest
        idx = len(values) - 1 - i
        if values[idx] and values[idx][0] == item_name:
            row_index = idx # 0-indexed
            break
            
    if row_index != -1:
        # Update Column E (Note) -> Index 4 (A=0, B=1, C=2, D=3, E=4) -> E is 5th col
        # Row number is index + 1
        update_range = f"{sheet_name}!E{row_index + 1}"
        encoded_update_range = urllib.parse.quote(update_range)
        body = {'values': [[new_note]]}
        url = f"{SHEETS_BASE_URL}/{spreadsheet_id}/values/{encoded_update_range}?valueInputOption=USER_ENTERED"
        google_request('PUT', url, json.dumps(body).encode('utf-8'))
        print("Google Sheet updated.")
    else:
        print("Sheet row not found.")

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: update_transaction_note.py <notion_db_id> <sheet_id> <item_name> <new_note>")
        sys.exit(1)
        
    notion_db_id = sys.argv[1]
    sheet_id = sys.argv[2]
    item_name = sys.argv[3]
    new_note = sys.argv[4]
    
    update_notion_note(notion_db_id, item_name, new_note)
    update_sheet_note(sheet_id, '記帳明細', item_name, new_note)
