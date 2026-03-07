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

def delete_last_row(spreadsheet_id, sheet_name='記帳明細'):
    # 1. Get current data to find the last row index
    range_name = f"{sheet_name}!A:A"
    encoded_range = urllib.parse.quote(range_name)
    url = f"{BASE_URL}/{spreadsheet_id}/values/{encoded_range}"
    resp = request('GET', url)
    values = resp.get('values', [])
    
    if not values:
        print("Sheet is empty.")
        return

    last_row_index = len(values) - 1 # 0-indexed
    
    # Avoid deleting the header row (index 0)
    if last_row_index <= 0:
         print("Only header row exists, nothing to delete.")
         return

    sheet_id = get_sheet_id(spreadsheet_id, sheet_name)
    if sheet_id is None:
        print(f"Sheet '{sheet_name}' not found.")
        return

    # 2. Delete the row
    body = {
        'requests': [
            {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': last_row_index,
                        'endIndex': last_row_index + 1
                    }
                }
            }
        ]
    }
    
    request('POST', f'{BASE_URL}/{spreadsheet_id}:batchUpdate', json.dumps(body).encode('utf-8'))
    print(f"Deleted row {last_row_index + 1}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: google_sheets_delete_last.py <spreadsheet_id>")
        sys.exit(1)
        
    spreadsheet_id = sys.argv[1]
    delete_last_row(spreadsheet_id)
