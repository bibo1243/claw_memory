#!/usr/bin/env python3
"""Read all entries from Goals database."""
import json, urllib.request, sys

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
DB_ID = '30a1fbf9-30df-811f-ae48-df0df29ad7f9'  # Goals (目標)
BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def api(method, url, data=None):
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        print(f'HTTP error {e.code}: {e.read().decode()}', file=sys.stderr)
        return None

# Query all goals
body = {'page_size': 50}
data = api('POST', f'{BASE_URL}/databases/{DB_ID}/query', json.dumps(body).encode('utf-8'))

if not data or not data['results']:
    print("No goals found.")
    sys.exit(0)

for page in data['results']:
    props = page['properties']
    page_id = page['id']
    
    # Extract title
    title = ""
    for prop_name, prop_val in props.items():
        if prop_val['type'] == 'title' and prop_val['title']:
            title = prop_val['title'][0]['plain_text']
            break
    
    # Extract all other properties
    details = []
    for prop_name, prop_val in props.items():
        ptype = prop_val['type']
        if ptype == 'title':
            continue
        elif ptype == 'rich_text' and prop_val['rich_text']:
            details.append(f"  {prop_name}: {prop_val['rich_text'][0]['plain_text']}")
        elif ptype == 'select' and prop_val['select']:
            details.append(f"  {prop_name}: {prop_val['select']['name']}")
        elif ptype == 'multi_select' and prop_val['multi_select']:
            vals = [v['name'] for v in prop_val['multi_select']]
            details.append(f"  {prop_name}: {', '.join(vals)}")
        elif ptype == 'number' and prop_val['number'] is not None:
            details.append(f"  {prop_name}: {prop_val['number']}")
        elif ptype == 'date' and prop_val['date']:
            details.append(f"  {prop_name}: {prop_val['date']['start']}")
        elif ptype == 'checkbox':
            details.append(f"  {prop_name}: {'✅' if prop_val['checkbox'] else '❌'}")
        elif ptype == 'status' and prop_val.get('status'):
            details.append(f"  {prop_name}: {prop_val['status']['name']}")
    
    print(f"\n📌 {title} (ID: {page_id})")
    for d in details:
        print(d)
    
    # Also read page content (children blocks)
    children = api('GET', f'{BASE_URL}/blocks/{page_id}/children?page_size=20')
    if children and children.get('results'):
        print("  --- Content ---")
        for block in children['results']:
            btype = block['type']
            if btype in ('paragraph', 'heading_1', 'heading_2', 'heading_3', 'bulleted_list_item', 'numbered_list_item', 'to_do'):
                rt = block[btype].get('rich_text', [])
                text = ''.join([r['plain_text'] for r in rt]) if rt else ''
                if btype == 'to_do':
                    checked = '✅' if block[btype].get('checked') else '☐'
                    print(f"  {checked} {text}")
                else:
                    print(f"  {text}")
