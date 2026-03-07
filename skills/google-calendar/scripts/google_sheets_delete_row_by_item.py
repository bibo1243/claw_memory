#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

BASE_URL = 'https://sheets.googleapis.com/v4/spreadsheets'

def get_access_token():
    token = os.getenv('GOOGLE_ACCESS_TOKEN')
    if not token:
        sys.stderr.write('Error: GOOGLE_ACCESS_TOKEN env var not set\n')
        sys.exit(1)
    return token

def request(method, url, data=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {get_access_token()}')
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

def get_sheet_id(spreadsheet_id, sheet_name):
    metadata = request('GET', f'{BASE_URL}/{spreadsheet_id}')
    for sheet in metadata.get('sheets', []):
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None

def find_row_index_by_item(spreadsheet_id, sheet_name, item_name):
    range_name = f"{sheet_name}!B:B" # Column B is Item
    encoded_range = urllib.parse.quote(range_name)
    url = f"{BASE_URL}/{spreadsheet_id}/values/{encoded_range}"
    resp = request('GET', url)
    values = resp.get('values', [])
    
    for i, row in enumerate(values):
        if row and row[0] == item_name:
            return i # 0-indexed
    return None

def delete_row(spreadsheet_id, sheet_name, row_index):
    sheet_id = get_sheet_id(spreadsheet_id, sheet_name)
    if sheet_id is None:
        print(f"Sheet '{sheet_name}' not found.")
        return

    body = {
        'requests': [
            {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': row_index,
                        'endIndex': row_index + 1
                    }
                }
            }
        ]
    }
    
    request('POST', f'{BASE_URL}/{spreadsheet_id}:batchUpdate', json.dumps(body).encode('utf-8'))
    print(f"Deleted row {row_index + 1}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: google_sheets_delete_row_by_item.py <spreadsheet_id> <item_name>")
        sys.exit(1)
        
    spreadsheet_id = sys.argv[1]
    item_name = sys.argv[2]
    
    row_index = find_row_index_by_item(spreadsheet_id, '記帳明細', item_name)
    if row_index is not None:
        delete_row(spreadsheet_id, '記帳明細', row_index)
    else:
        print(f"Item '{item_name}' not found in sheet.")
