#!/usr/bin/env python3
"""查詢基金會假表 - 修正版"""
import os, json, urllib.request, urllib.parse

SPREADSHEET_ID = '1JnPLKg5HlKWfSymp79Yx66TZVYehBgVjU6ZbKQgaJR0'
SYMBOLS = {'◎': '例假', '〇': '休息日', '●': '特休全天', '△': '上午休', '▽': '下午休', '▲': '上午特休', '▼': '下午特休', '上會': '上午會議', '下會': '下午會議', '上下會': '全天會議', '活動': '活動', '福': '福利假', '公': '公假', '自強': '自強活動'}

def get_token():
    data = urllib.parse.urlencode({'client_id': os.getenv('GOOGLE_CLIENT_ID'), 'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'), 'refresh_token': os.getenv('GOOGLE_REFRESH_TOKEN'), 'grant_type': 'refresh_token'}).encode()
    with urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST'), timeout=10) as r:
        return json.load(r)['access_token']

def query(sheet, token):
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{urllib.parse.quote(sheet)}!A1:AZ50'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r).get('values', [])

def interpret(s):
    s = str(s).strip()
    if not s: return None
    if s in SYMBOLS: return SYMBOLS[s]
    parts = [SYMBOLS[k] for k in SYMBOLS if k in s]
    return ' + '.join(parts) if parts else s

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--name', required=True)
    p.add_argument('--sheet', required=True)
    args = p.parse_args()
    token = get_token()
    rows = query(args.sheet, token)
    dates = rows[0] if rows else []
    weekdays = rows[1] if len(rows) > 1 else []
    
    for row in rows:
        if row and args.name in str(row[0]):
            print(f"\n{row[0]} 排班：\n")
            # 讀取所有日期欄位，不限制數量
            for i in range(1, len(dates)):
                d = str(dates[i]).strip()
                # 跳過統計欄（一例一休、休假日、特休、四週）
                if d in ['一例一休', '休假日', '特休', '四週', ''] or '天數' in d:
                    continue
                wd = weekdays[i] if i < len(weekdays) else ''
                status = row[i] if i < len(row) else ''
                meaning = interpret(status)
                if meaning:
                    print(f"  {d} ({wd}): {status} = {meaning}")
            break
