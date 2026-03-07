#!/usr/bin/env python3
import os, sys, json, urllib.request

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
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
        sys.exit(1)

def get_page_blocks(page_id):
    url = f"{BASE_URL}/blocks/{page_id}/children"
    return request('GET', url)

def reformat_diary_content(page_id, title, content_raw):
    # 1. Clear existing content blocks
    blocks = get_page_blocks(page_id)
    if blocks and 'results' in blocks:
        for block in blocks['results']:
            request('DELETE', f"{BASE_URL}/blocks/{block['id']}")

    # 2. Parse and Structure Content
    # Assuming content_raw is a single string with \n. We want to make it structured.
    # Structure:
    # Heading 2: 今日收穫
    # Bulleted List: for points
    # Heading 3: 結論
    # Quote: for conclusion
    
    # Simple parsing logic
    lines = content_raw.split('\\n') # The input might have escaped newlines if passed raw
    if len(lines) == 1:
        lines = content_raw.split('\n')

    new_blocks = []
    
    # Intro
    new_blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": "💡 今日收穫"}}], "color": "blue"}
    })
    
    list_mode = False
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if "關鍵字：" in line:
            # Handle keywords as callout or distinct block
            new_blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": line}}],
                    "icon": {"emoji": "🏷️"},
                    "color": "gray_background"
                }
            })
            continue
            
        if "結論：" in line:
            new_blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": "🚀 結論"}}], "color": "orange"}
            })
            continue

        # Check for list items (1. , 2. , - )
        if line[0].isdigit() and line[1] in ['.', '、'] or line.startswith('- '):
            # Clean up numbering
            text = line.split('.', 1)[-1].strip() if line[0].isdigit() else line[2:].strip()
            new_blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}
            })
        else:
            # Normal paragraph or Quote if it looks like conclusion body
            new_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
            })

    # 3. Write new blocks
    request('PATCH', f"{BASE_URL}/blocks/{page_id}/children", json.dumps({'children': new_blocks}).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: notion_reformat_diary.py <page_id> <title> <raw_content>")
        sys.exit(1)
        
    page_id = sys.argv[1]
    title = sys.argv[2]
    raw = sys.argv[3]
    
    reformat_diary_content(page_id, title, raw)
    print("Reformatted.")
