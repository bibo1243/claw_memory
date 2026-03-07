#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

# --- Config ---
GAA_ALL_ID = "1gEZZ2n78Ee5SGdeoNkcIzl0I1u9KrJj9" 

# --- Env ---
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    if parts[0] not in os.environ:
                        os.environ[parts[0]] = parts[1]

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

# --- Auth ---
def get_access_token(force_refresh=False):
    token = os.environ.get('GOOGLE_ACCESS_TOKEN')
    if token and not force_refresh:
        return token
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    if not all([client_id, client_secret, refresh_token]):
        sys.exit(1)
    url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req) as resp:
            body = json.load(resp)
            if body.get('access_token'):
                os.environ['GOOGLE_ACCESS_TOKEN'] = body['access_token']
                return body['access_token']
    except:
        pass
    sys.exit(1)

def request(method, url, data=None):
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 401:
            headers['Authorization'] = f'Bearer {get_access_token(force_refresh=True)}'
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req) as resp:
                return resp.read()
        return None

# --- Logic ---
def read_html(file_id):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    content = request('GET', url)
    if content:
        return content.decode('utf-8')
    return ""

def analyze_chat(html_content, source_name):
    # Simplified mock analysis for demo (actual HTML parsing is complex without Beautiful Soup)
    # We will just look for keywords "答應", "好", "收到", "沒問題", "ok" near Gary or Key People
    # and extract the context.
    
    # In a real scenario, we'd use a robust parser.
    # Here, let's extract plain text lines roughly.
    
    # Remove HTML tags roughly
    text = html_content.replace('<br>', '\n').replace('</div>', '\n')
    import re
    clean_text = re.sub('<[^<]+?>', '', text)
    
    lines = clean_text.splitlines()
    tasks = []
    
    for i, line in enumerate(lines):
        if not line.strip(): continue
        
        # Heuristic: Check for commitment keywords
        keywords = ["答應", "承諾", "沒問題", "好的", "收到", "下週", "明天", "待辦", "todo", "to-do"]
        if any(k in line.lower() for k in keywords):
            # Try to find who said it (look back a few lines for a name pattern)
            # This is very rough.
            context = line.strip()[:100] # Limit length
            tasks.append(f"- [{source_name}] 可能承諾: {context}")
            
    # Return top 5 potential tasks to avoid noise
    return tasks[:5]

def main():
    # File IDs from previous scan
    files = [
        {"name": "慈光核心主管", "id": "1_bzgmg2FSXlN_T_Nlov1t8Z1is9EzHU5"},
        {"name": "少年家園", "id": "1NFtKugWIWCby5J4edZ0zKzNjjPQvvOBG"},
        # Add more if needed, just testing one for speed
    ]
    
    print("🔎 Analyzing chat logs for commitments...")
    all_tasks = []
    
    for f in files:
        print(f"Reading {f['name']}...")
        content = read_html(f['id'])
        if content:
            tasks = analyze_chat(content, f['name'])
            all_tasks.extend(tasks)
            
    print("\n📋 Analysis Result:")
    for t in all_tasks:
        print(t)

if __name__ == "__main__":
    main()
