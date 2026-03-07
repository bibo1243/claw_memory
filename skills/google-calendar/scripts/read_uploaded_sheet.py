#!/usr/bin/env python3
import os, sys, json, urllib.request

# Spreadsheet ID from the previous step
SPREADSHEET_ID = '1aTAcBjqTt1zXDgUC0-lMA656bIWZCcr0VJOr7tzn4AY'
BASE_URL = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/A:Z'

def get_access_token():
    token = os.getenv('GOOGLE_ACCESS_TOKEN')
    if not token:
        sys.stderr.write('Error: GOOGLE_ACCESS_TOKEN env var not set\n')
        sys.exit(1)
    return token

def read_sheet():
    req = urllib.request.Request(BASE_URL, method='GET')
    req.add_header('Authorization', f'Bearer {get_access_token()}')
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

if __name__ == '__main__':
    data = read_sheet()
    values = data.get('values', [])
    
    if not values:
        print("No data found.")
    else:
        print(f"Read {len(values)} rows.")
        for i, row in enumerate(values[:20]): # Show first 20 rows
            print(f"Row {i+1}: {row}")
