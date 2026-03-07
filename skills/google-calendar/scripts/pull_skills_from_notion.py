#!/usr/bin/env python3
import os, sys, json, urllib.request

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
DB_ID = '30b1fbf9-30df-81f1-897c-db2c1cb7fdb2'  # System Skills Database

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

def get_page_content(page_id):
    # Fetch blocks (content) of the page
    url = f"{BASE_URL}/blocks/{page_id}/children"
    data = request('GET', url)
    content = ""
    for block in data['results']:
        if block['type'] == 'code':
            content += block['code']['rich_text'][0]['plain_text']
        # We assume the entire SKILL.md is stored in code blocks. 
        # If it was split, we concatenate.
    return content

def pull_skills(workspace_dir):
    print(f"Fetching skills from Notion DB: {DB_ID}...")
    
    body = {} # No filter, get all
    data = request('POST', f"{BASE_URL}/databases/{DB_ID}/query", json.dumps(body).encode('utf-8'))
    
    for page in data['results']:
        try:
            props = page['properties']
            name = props['Name']['title'][0]['plain_text']
            # path_prop = props.get('Path', {}).get('rich_text', [])
            # path = path_prop[0]['plain_text'] if path_prop else f"skills/{name}/SKILL.md"
            
            # For cloud agent, we enforce standard path
            local_path = os.path.join(workspace_dir, "skills", name, "SKILL.md")
            
            print(f"  - Pulling: {name} -> {local_path}")
            
            content = get_page_content(page['id'])
            
            # Ensure dir exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Error processing page {page['id']}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: pull_skills_from_notion.py <workspace_dir>")
        sys.exit(1)
        
    pull_skills(sys.argv[1])
