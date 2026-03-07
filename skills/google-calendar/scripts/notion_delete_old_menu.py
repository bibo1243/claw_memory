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

def delete_blocks_by_type(page_id, block_types_to_delete):
    # 1. List children of the page
    url = f"{BASE_URL}/blocks/{page_id}/children"
    data = request('GET', url)
    
    # 2. Identify blocks to delete
    # In this case, we want to delete the Heading 2 "⚡ 能量急救菜單" and the Callout/ColumnList following it.
    # Logic: Find the heading, and delete it + following blocks until we hit something else?
    # Or just delete specific blocks we know we added.
    # Since we just added them at the end, let's look for blocks that match our structure.
    
    blocks_to_delete = []
    found_start = False
    
    for block in data['results']:
        b_type = block['type']
        
        # Check for the Heading
        if b_type == 'heading_2':
            text_content = ""
            if 'rich_text' in block['heading_2'] and block['heading_2']['rich_text']:
                text_content = block['heading_2']['rich_text'][0]['text']['content']
            
            if "能量急救菜單" in text_content:
                found_start = True
                blocks_to_delete.append(block['id'])
                continue
        
        if found_start:
            # Delete subsequent blocks that are part of this section
            # (Callout and 2 Column Lists)
            if b_type in ['callout', 'column_list']:
                blocks_to_delete.append(block['id'])
            else:
                # Stop if we hit a different block type (or maybe we assume it's at the end)
                # For safety, let's just delete the known structure: Heading -> Callout -> ColList -> ColList
                if len(blocks_to_delete) >= 4: 
                    break
    
    # 3. Delete them
    for block_id in blocks_to_delete:
        print(f"Deleting block {block_id}...")
        request('DELETE', f"{BASE_URL}/blocks/{block_id}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_delete_old_menu.py <page_id>")
        sys.exit(1)
        
    page_id = sys.argv[1]
    delete_blocks_by_type(page_id, [])
