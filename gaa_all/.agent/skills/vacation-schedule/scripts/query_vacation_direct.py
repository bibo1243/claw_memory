#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse, argparse

SPREADSHEET_ID = '1JnPLKg5HlKWfSymp79Yx66TZVYehBgVjU6ZbKQgaJR0'

# 使用新的 Access Token (從上一步的 refresh_token.py 輸出獲取)
# 注意：這個 token 有效期只有 1 小時，如果失效請重新執行 refresh_token.py
ACCESS_TOKEN = 'ya29.[MASKED_ACCESS_TOKEN]'

def request(method, url):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {ACCESS_TOKEN}')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

def get_sheet_values(sheet_name):
    # URL Encode sheet name
    encoded_name = urllib.parse.quote(sheet_name)
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{encoded_name}!A1:Z50"
    return request('GET', url)

def find_schedule(name, sheet_name):
    data = get_sheet_values(sheet_name)
    values = data.get('values', [])
    
    if not values:
        print("Sheet is empty.")
        return

    # Row 1: Dates (Day of month)
    dates = values[0]
    # Row 2: Weekdays
    weekdays = values[1]
    
    # Find employee row
    target_row = None
    for row in values:
        if row and name in row[0]: # Partial match for name (e.g. "B李冠葦")
            target_row = row
            break
            
    if not target_row:
        print(f"Employee '{name}' not found in sheet '{sheet_name}'.")
        return

    print(f"### {sheet_name} - {target_row[0]}")
    
    # Iterate through dates (skip col 0 which is name)
    # Be careful with index out of bounds if rows have different lengths
    for i in range(1, len(dates)):
        date_str = dates[i]
        
        # Stop if we hit stats columns
        if date_str in ['一例一休', '休假日', '特休', '四週']:
            break
            
        weekday = weekdays[i] if i < len(weekdays) else ""
        
        # Get schedule symbol, handle empty or missing
        symbol = target_row[i] if i < len(target_row) else ""
        
        # If symbol is empty, it means "上班" (Work)
        if not symbol:
            symbol = "上班"
            
        print(f"{date_str}({weekday}): {symbol}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--sheet', required=True)
    args = parser.parse_args()
    
    find_schedule(args.name, args.sheet)
