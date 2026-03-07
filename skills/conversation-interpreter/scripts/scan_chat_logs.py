#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime, timedelta

# Config
GAA_ALL_ID = "1gEZZ2n78Ee5SGdeoNkcIzl0I1u9KrJj9" 

# Target Keywords / People
TARGETS = [
    "組織發展會議", "總行政～核心組", "廖慧雯", "詹前柏", 
    "少年家園共創合作群組", "王姿斐", "【社資組】四角", 
    "Elizabeth梅芳", "慈光核心主管", "兒少之家共創合作群組", 
    "行政組資深GoGoGo", "慈馨總教資深團隊", "（行政）"
]

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
            new_token = body.get('access_token')
            if new_token:
                os.environ['GOOGLE_ACCESS_TOKEN'] = new_token
                return new_token
    except:
        sys.exit(1)

def request(method, url, data=None):
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            headers['Authorization'] = f'Bearer {get_access_token(force_refresh=True)}'
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        return None

def find_folder(parent_id, name):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}"
    data = request('GET', url)
    return data['files'][0]['id'] if data and data.get('files') else None

def list_html_files(folder_id):
    # Find files modified in last 6 months? 
    # Or just list all HTMLs and filter by name if they contain target names
    # Drive search is powerful. Let's search for name contains target AND mimeType html
    
    # We need to find the "聊天記錄" folder first
    chat_log_id = find_folder(GAA_ALL_ID, '聊天記錄')
    if not chat_log_id:
        print("Error: '聊天記錄' folder not found in gaa_all.")
        return []

    print(f"Found '聊天記錄' folder: {chat_log_id}")
    
    # Since we have many targets, we might need to iterate or construct a complex query.
    # Complex query limit is strict.
    # Strategy: List all HTML files in '聊天記錄' (recursive is hard with simple query, usually need to walk)
    # But if structure is flat inside '聊天記錄', it's easy.
    # If it's nested (Person Name -> chat.html), we need to walk.
    
    # Let's assume folder structure: 聊天記錄/Name/chat.html OR 聊天記錄/Name.html
    # Let's list immediate children of 聊天記錄
    
    query = f"'{chat_log_id}' in parents and trashed = false"
    params = {'q': query, 'fields': 'files(id, name, mimeType, modifiedTime)', 'pageSize': 1000}
    url = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = request('GET', url)
    
    files = data.get('files', [])
    matched_files = []
    
    print(f"Scanning {len(files)} items in 聊天記錄...")
    
    for f in files:
        name = f['name']
        # Check if name matches any target
        is_match = any(t in name for t in TARGETS)
        
        if is_match:
            # If it's a folder, we assume the chat log is inside (e.g. LINE backup format)
            if f['mimeType'] == 'application/vnd.google-apps.folder':
                # Look for .txt or .html inside
                sub_query = f"'{f['id']}' in parents and (mimeType = 'text/html' or mimeType = 'text/plain') and trashed = false"
                sub_url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(sub_query)}&fields=files(id, name)"
                sub_data = request('GET', sub_url)
                if sub_data and sub_data.get('files'):
                    for sub_f in sub_data['files']:
                        matched_files.append({
                            'source': name,
                            'file_name': sub_f['name'],
                            'id': sub_f['id']
                        })
            # If it's a file directly
            elif 'html' in f['mimeType'] or 'text' in f['mimeType'] or name.endswith('.html') or name.endswith('.txt'):
                matched_files.append({
                    'source': name,
                    'file_name': name,
                    'id': f['id']
                })
                
    return matched_files

def main():
    files = list_html_files(None)
    print(f"Found {len(files)} matching chat logs.")
    for f in files:
        print(f" - {f['source']} / {f['file_name']} (ID: {f['id']})")

if __name__ == "__main__":
    main()
