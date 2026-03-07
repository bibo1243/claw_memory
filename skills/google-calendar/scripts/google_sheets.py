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

def create_spreadsheet(title):
    body = {
        'properties': {'title': title},
        'sheets': [
            {'properties': {'title': '記帳明細', 'gridProperties': {'frozenRowCount': 1}}},
            {'properties': {'title': '統計儀表板'}}
        ]
    }
    return request('POST', BASE_URL, json.dumps(body).encode('utf-8'))

def setup_transactions_sheet(spreadsheet_id, sheet_id):
    # Categories from spec
    categories = [
        "食 (三餐/飲料)", "衣 (服飾)", "住 (水電/日用/3C)", "行 (個人交通/加油/洗車)", 
        "育 (書籍/課程)", "樂 (娛樂/旅遊)",
        "公務餐飲", "差旅交通", "交際應酬", "辦公雜支"
    ]
    
    requests = [
        # Set Headers
        {
            'updateCells': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 6},
                'rows': [{
                    'values': [
                        {'userEnteredValue': {'stringValue': '日期'}},
                        {'userEnteredValue': {'stringValue': '項目 (品名)'}},
                        {'userEnteredValue': {'stringValue': '金額'}},
                        {'userEnteredValue': {'stringValue': '分類'}},
                        {'userEnteredValue': {'stringValue': '備註'}},
                        {'userEnteredValue': {'stringValue': '價值分析 (高/低)'}}
                    ]
                }],
                'fields': 'userEnteredValue'
            }
        },
        # Format Headers (Bold, Colored background)
        {
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                        'textFormat': {'bold': True}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        },
        # Data Validation for Category (Dropdown)
        {
            'setDataValidation': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'startColumnIndex': 3, 'endColumnIndex': 4},
                'rule': {
                    'condition': {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': c} for c in categories]},
                    'showCustomUi': True
                }
            }
        },
         # Data Validation for Value Analysis (Dropdown)
        {
            'setDataValidation': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'startColumnIndex': 5, 'endColumnIndex': 6},
                'rule': {
                    'condition': {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': '高價值'}, {'userEnteredValue': '低價值'}]},
                    'showCustomUi': True
                }
            }
        },
        # Set Date Format for Column A
        {
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 1},
                'cell': {'userEnteredFormat': {'numberFormat': {'type': 'DATE', 'pattern': 'yyyy-mm-dd'}}},
                'fields': 'userEnteredFormat.numberFormat'
            }
        },
         # Set Currency Format for Column C
        {
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'startColumnIndex': 2, 'endColumnIndex': 3},
                'cell': {'userEnteredFormat': {'numberFormat': {'type': 'CURRENCY', 'pattern': '$#,##0'}}},
                'fields': 'userEnteredFormat.numberFormat'
            }
        }
    ]
    
    body = {'requests': requests}
    request('POST', f'{BASE_URL}/{spreadsheet_id}:batchUpdate', json.dumps(body).encode('utf-8'))

def setup_dashboard_sheet(spreadsheet_id, dashboard_sheet_id, trans_sheet_name):
    requests = [
        # Total Expense Formula
        {
            'updateCells': {
                'range': {'sheetId': dashboard_sheet_id, 'startRowIndex': 0, 'endRowIndex': 2, 'startColumnIndex': 0, 'endColumnIndex': 2},
                'rows': [
                    {'values': [{'userEnteredValue': {'stringValue': '本月總支出'}}]},
                    {'values': [{'userEnteredValue': {'formulaValue': f'=SUM({trans_sheet_name}!C:C)'}}]} # Simple Sum for MVP
                ],
                'fields': 'userEnteredValue'
            }
        },
        # Pivot Table for Categories (Simplified as Query/Unique for MVP Chart)
        # Actually, adding a Pie Chart requires a data source. 
        # For this MVP script, let's just add headers for where the pivot would go, 
        # or use a QUERY function to generate the summary table for the chart.
        {
             'updateCells': {
                'range': {'sheetId': dashboard_sheet_id, 'startRowIndex': 3, 'endRowIndex': 4, 'startColumnIndex': 0, 'endColumnIndex': 1},
                'rows': [{'values': [{'userEnteredValue': {'stringValue': '分類統計 (自動計算)'}}]}],
                'fields': 'userEnteredValue'
            }
        },
        {
            'updateCells': {
                'range': {'sheetId': dashboard_sheet_id, 'startRowIndex': 4, 'endRowIndex': 5, 'startColumnIndex': 0, 'endColumnIndex': 1},
                 'rows': [{'values': [{'userEnteredValue': {'formulaValue': f'=QUERY(\'{trans_sheet_name}\'!A:F, "Select D, Sum(C) where D is not null Group by D label Sum(C) \'金額\'", 1)'}}]}],
                 'fields': 'userEnteredValue'
            }
        }
    ]
    body = {'requests': requests}
    request('POST', f'{BASE_URL}/{spreadsheet_id}:batchUpdate', json.dumps(body).encode('utf-8'))
    
    # Separate request to add chart (needs data source present, but we can try adding it linking to the query result)
    # Range for chart: A5:B20 (approx) on Dashboard
    chart_request = {
        'requests': [{
            'addChart': {
                'chart': {
                    'spec': {
                        'title': '支出分類佔比',
                        'pieChart': {
                            'legendPosition': 'RIGHT_LEGEND',
                            'domain': {'sourceRange': {'sources': [{'sheetId': dashboard_sheet_id, 'startRowIndex': 5, 'endRowIndex': 20, 'startColumnIndex': 0, 'endColumnIndex': 1}]}},
                            'series': {'sourceRange': {'sources': [{'sheetId': dashboard_sheet_id, 'startRowIndex': 5, 'endRowIndex': 20, 'startColumnIndex': 1, 'endColumnIndex': 2}]}}
                        }
                    },
                    'position': {
                        'overlayPosition': {
                            'anchorCell': {'sheetId': dashboard_sheet_id, 'rowIndex': 0, 'columnIndex': 3},
                             'widthPixels': 400,
                             'heightPixels': 300
                        }
                    }
                }
            }
        }]
    }
    request('POST', f'{BASE_URL}/{spreadsheet_id}:batchUpdate', json.dumps(chart_request).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: google_sheets.py <title>")
        sys.exit(1)
        
    title = sys.argv[1]
    print(f"Creating spreadsheet '{title}'...")
    ss = create_spreadsheet(title)
    ss_id = ss['spreadsheetId']
    print(f"Spreadsheet created: {ss['spreadsheetUrl']}")
    
    sheets = ss['sheets']
    trans_sheet_id = next(s['properties']['sheetId'] for s in sheets if s['properties']['title'] == '記帳明細')
    dash_sheet_id = next(s['properties']['sheetId'] for s in sheets if s['properties']['title'] == '統計儀表板')
    
    print("Setting up Transactions sheet...")
    setup_transactions_sheet(ss_id, trans_sheet_id)
    
    print("Setting up Dashboard sheet...")
    setup_dashboard_sheet(ss_id, dash_sheet_id, '記帳明細')
    
    print("Done.")
