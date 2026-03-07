#!/usr/bin/env python3
import os, sys, json, urllib.request

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
DB_ID = '30c1fbf9-30df-81d6-b8f0-da6540b0e208' # LINE Inbox

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
        return None

def check_line_inbox():
    # Filter for Status (Select property, not Status property)
    body = {
        'filter': {
            'property': 'Status',
            'select': {
                'equals': 'New'
            }
        },
        'sorts': [
            {
                'timestamp': 'created_time',
                'direction': 'descending'
            }
        ],
        'page_size': 20
    }
    
    data = request('POST', f"{BASE_URL}/databases/{DB_ID}/query", json.dumps(body).encode('utf-8'))
    
    # If no data found, try fetching WITHOUT filter to debug property names
    if not data or not data['results']:
        # print("No 'New' status found. Fetching raw schema...")
        body_all = {'page_size': 1}
        data_all = request('POST', f"{BASE_URL}/databases/{DB_ID}/query", json.dumps(body_all).encode('utf-8'))
        if data_all and data_all['results']:
            # print("Raw properties keys:", data_all['results'][0]['properties'].keys())
            pass
        print("無")
        return

    important_msgs = []
    # Broadened keyword list
    keywords = ['Gary', '李冠葦', '冠葦', '急', '重要', '核銷', '@All', '@all', '老師']

    for page in data['results']:
        props = page['properties']
        
        # Extract Sender (Title property)
        sender = "Unknown"
        # The title property might not be named "Sender" (e.g. "Name" or "Page")
        # Let's find the title property dynamically
        for prop_name, prop_val in props.items():
            if prop_val['type'] == 'title' and prop_val['title']:
                 sender = prop_val['title'][0]['plain_text']
                 break
        
        # Extract Message Content (Rich Text)
        message = ""
        # Look for "Message" property specifically, or any rich_text
        if 'Message' in props and props['Message']['rich_text']:
            message = props['Message']['rich_text'][0]['plain_text']
        
        # If message is empty, maybe the Title IS the message? 
        # (Sometimes integrations put content in title)
        if not message: 
             message = sender # Fallback
            
        # Check for keywords
        is_important = False
        for kw in keywords:
            if kw in message:
                is_important = True
                break
        
        if is_important:
            important_msgs.append(f"🔴 [{sender}]: {message[:50]}")
            
    if important_msgs:
        print("\n".join(important_msgs))
    else:
        # If we found messages but no keywords matched, list the latest one anyway for verification
        if data['results']:
             first_page = data['results'][0]
             # props = first_page['properties']
             # ... extraction logic ...
             # print(f"(Debug: Found {len(data['results'])} 'New' messages but no keywords. Latest: {message})")
             pass
        print("無 (未偵測到關鍵字)")

if __name__ == '__main__':
    check_line_inbox()
