#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse
from datetime import datetime

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

def append_row(spreadsheet_id, date, item, amount, category, note, value_analysis):
    range_name = '記帳明細!A:F'
    # URL encode range name
    encoded_range = urllib.parse.quote(range_name)
    
    body = {
        'values': [[date, item, amount, category, note, value_analysis]]
    }
    url = f"{BASE_URL}/{spreadsheet_id}/values/{encoded_range}:append?valueInputOption=USER_ENTERED"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 7:
        print("Usage: google_sheets_append.py <spreadsheet_id> <date> <item> <amount> <category> <note> <value_analysis>")
        sys.exit(1)
        
    spreadsheet_id = sys.argv[1]
    date = sys.argv[2]
    item = sys.argv[3]
    amount = sys.argv[4]
    category = sys.argv[5]
    note = sys.argv[6]
    value_analysis = sys.argv[7]
    
    append_row(spreadsheet_id, date, item, amount, category, note, value_analysis)
