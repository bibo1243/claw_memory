#!/usr/bin/env python3
import os, sys, json, urllib.request

# Hardcode the token here
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

def create_database(parent_page_id, title, properties):
    body = {
        'parent': {'type': 'page_id', 'page_id': parent_page_id},
        'title': [{'type': 'text', 'text': {'content': title}}],
        'properties': properties
    }
    url = f"{BASE_URL}/databases"
    return request('POST', url, json.dumps(body).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_setup.py <page_id>")
        sys.exit(1)
        
    root_page_id = sys.argv[1]
    
    # --- 1. Intentions ---
    print("1. Creating 'Intentions' Database...")
    INTENTIONS_PROPS = {
        'Name': {'title': {}},
        'Description': {'rich_text': {}},
        'Status': {'select': {'options': [{'name': 'Active', 'color': 'green'}, {'name': 'Draft', 'color': 'gray'}]}},
        'Type': {'select': {'options': [{'name': 'Vision', 'color': 'blue'}, {'name': 'Mission', 'color': 'purple'}]}}
    }
    intentions_db = create_database(root_page_id, "Intentions (意圖)", INTENTIONS_PROPS)
    intentions_id = intentions_db['id']
    print(f"   Created: {intentions_id}")
    
    # --- 2. Goals ---
    print("2. Creating 'Goals' Database...")
    GOALS_PROPS = {
        'Name': {'title': {}},
        'Status': {'status': {}},
        'Timeline': {'date': {}},
        'Intention': {'relation': {'database_id': intentions_id, 'single_property': {}}}, 
        'Progress': {'number': {'format': 'percent'}}
    }
    goals_db = create_database(root_page_id, "Goals (目標)", GOALS_PROPS)
    goals_id = goals_db['id']
    print(f"   Created: {goals_id}")
    
    # --- 3. Projects ---
    print("3. Creating 'Projects' Database...")
    PROJECTS_PROPS = {
        'Name': {'title': {}},
        'Status': {'status': {}},
        'Timeline': {'date': {}},
        'Goal': {'relation': {'database_id': goals_id, 'single_property': {}}},
        'Priority': {'select': {'options': [{'name': 'High', 'color': 'red'}, {'name': 'Medium', 'color': 'yellow'}, {'name': 'Low', 'color': 'blue'}]}}
    }
    projects_db = create_database(root_page_id, "Projects (專案)", PROJECTS_PROPS)
    projects_id = projects_db['id']
    print(f"   Created: {projects_id}")
    
    # --- 4. Tasks ---
    print("4. Creating 'Tasks' Database...")
    TASKS_PROPS = {
        'Name': {'title': {}},
        'Status': {'status': {}},
        'Do Date': {'date': {}},
        'Project': {'relation': {'database_id': projects_id, 'single_property': {}}},
        'Context': {'multi_select': {'options': [{'name': 'Work', 'color': 'orange'}, {'name': 'Personal', 'color': 'blue'}, {'name': 'Study', 'color': 'pink'}]}},
        'Priority': {'select': {'options': [{'name': 'High', 'color': 'red'}, {'name': 'Medium', 'color': 'yellow'}, {'name': 'Low', 'color': 'blue'}]}}
    }
    tasks_db = create_database(root_page_id, "Tasks (每日行動)", TASKS_PROPS)
    tasks_id = tasks_db['id']
    print(f"   Created: {tasks_id}")
    
    # --- 5. Knowledge Base ---
    print("5. Creating 'Knowledge Base' Database...")
    KNOWLEDGE_PROPS = {
        'Name': {'title': {}},
        'Tags': {'multi_select': {}},
        'Type': {'select': {'options': [{'name': 'Note', 'color': 'gray'}, {'name': 'SOP', 'color': 'blue'}, {'name': 'Course', 'color': 'purple'}]}},
        'URL': {'url': {}}
    }
    kb_db = create_database(root_page_id, "Knowledge Base (知識庫)", KNOWLEDGE_PROPS)
    kb_id = kb_db['id']
    print(f"   Created: {kb_id}")
    
    # --- 6. Finance ---
    print("6. Creating 'Finance' Database...")
    FINANCE_PROPS = {
        'Name': {'title': {}},
        'Month': {'date': {}},
        'Total Expense': {'number': {'format': 'dollar'}},
        'Sheet Link': {'url': {}}
    }
    fin_db = create_database(root_page_id, "Finance (財務)", FINANCE_PROPS)
    fin_id = fin_db['id']
    print(f"   Created: {fin_id}")

    print("\n--- Setup Complete ---")
