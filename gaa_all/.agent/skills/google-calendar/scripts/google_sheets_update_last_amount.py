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

def update_last_row_amount(spreadsheet_id, sheet_name, amount):
    # 1. Get current data to find the last row index
    range_name = f"{sheet_name}!A:A"
    encoded_range = urllib.parse.quote(range_name)
    url = f"{BASE_URL}/{spreadsheet_id}/values/{encoded_range}"
    resp = request('GET', url)
    values = resp.get('values', [])
    
    if not values:
        print("Sheet is empty.")
        return

    last_row_index = len(values) # 1-based row number for A1 notation
    
    # Update Column C (Amount) of the last row
    update_range = f"{sheet_name}!C{last_row_index}"
    encoded_update_range = urllib.parse.quote(update_range)
    
    body = {
        'values': [[amount]]
    }
    
    url = f"{BASE_URL}/{spreadsheet_id}/values/{encoded_update_range}?valueInputOption=USER_ENTERED"
    request('PUT', url, json.dumps(body).encode('utf-8'))
    print(f"Updated amount in row {last_row_index}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: google_sheets_update_last_amount.py <spreadsheet_id> <amount>")
        sys.exit(1)
        
    spreadsheet_id = sys.argv[1]
    amount = sys.argv[2]
    
    update_last_row_amount(spreadsheet_id, '記帳明細', amount)
