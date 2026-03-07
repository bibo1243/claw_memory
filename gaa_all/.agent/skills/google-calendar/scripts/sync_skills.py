#!/usr/bin/env python3
import os, sys, json, urllib.request, glob
from datetime import datetime

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
DB_ID = '30b1fbf9-30df-81f1-897c-db2c1cb7fdb2'

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

def find_page_by_name(db_id, name):
    body = {
        'filter': {
            'property': 'Name',
            'title': {
                'equals': name
            }
        }
    }
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    if data and data['results']:
        return data['results'][0]['id']
    return None

def split_text(text, limit=2000):
    """Splits text into chunks of max `limit` characters."""
    return [text[i:i+limit] for i in range(0, len(text), limit)]

def update_skill_page(page_id, description, content, path):
    # Update properties
    props_body = {
        'properties': {
            'Description': {'rich_text': [{'text': {'content': description[:2000]}}]},
            'Last Updated': {'date': {'start': datetime.now().isoformat()}},
            'Path': {'rich_text': [{'text': {'content': path}}]}
        }
    }
    request('PATCH', f"{BASE_URL}/pages/{page_id}", json.dumps(props_body).encode('utf-8'))
    
    # Update content
    # 1. Get children
    children = request('GET', f"{BASE_URL}/blocks/{page_id}/children")
    if children:
        for block in children['results']:
            request('DELETE', f"{BASE_URL}/blocks/{block['id']}")
            
    # 2. Add new content
    chunks = split_text(content, 2000)
    children_blocks = []
    for chunk in chunks:
        children_blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}],
                "language": "markdown"
            }
        })
        
    # Append blocks in batches (Notion limit is 100 blocks, we are fine, but good practice)
    request('PATCH', f"{BASE_URL}/blocks/{page_id}/children", json.dumps({'children': children_blocks}).encode('utf-8'))

def create_skill_page(db_id, name, description, content, path):
    chunks = split_text(content, 2000)
    children_blocks = []
    for chunk in chunks:
        children_blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}],
                "language": "markdown"
            }
        })

    body = {
        'parent': {'database_id': db_id},
        'properties': {
            'Name': {'title': [{'text': {'content': name}}]},
            'Description': {'rich_text': [{'text': {'content': description[:2000]}}]},
            'Last Updated': {'date': {'start': datetime.now().isoformat()}},
            'Path': {'rich_text': [{'text': {'content': path}}]}
        },
        'children': children_blocks
    }
    request('POST', f"{BASE_URL}/pages", json.dumps(body).encode('utf-8'))

def parse_skill_md(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    name = os.path.basename(os.path.dirname(file_path)) 
    description = ""
    
    lines = content.split('\n')
    in_frontmatter = False
    for line in lines:
        if line.strip() == '---':
            if in_frontmatter: break 
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.startswith('name:'):
                name = line.split(':', 1)[1].strip()
            elif line.startswith('description:'):
                description = line.split(':', 1)[1].strip()
                
    return name, description, content

def sync_skills(db_id, workspace_dir):
    skill_files = glob.glob(os.path.join(workspace_dir, "skills/*/SKILL.md"))
    print(f"Found {len(skill_files)} skills.")
    
    for file_path in skill_files:
        try:
            name, desc, content = parse_skill_md(file_path)
            print(f"Syncing: {name}")
            
            page_id = find_page_by_name(db_id, name)
            if page_id:
                print(f"  Updating page {page_id}...")
                update_skill_page(page_id, desc, content, file_path)
            else:
                print(f"  Creating new page...")
                create_skill_page(db_id, name, desc, content, file_path)
        except Exception as e:
            print(f"Error syncing {file_path}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: sync_skills.py <db_id> <workspace_dir>")
        sys.exit(1)
        
    sync_skills(sys.argv[1], sys.argv[2])
