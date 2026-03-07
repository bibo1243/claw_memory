#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

# --- Configuration ---
# gaa_all folder ID from MEMORY.md
GAA_ALL_ID = "1gEZZ2n78Ee5SGdeoNkcIzl0I1u9KrJj9" 
MEMORY_ROOT_ID = "1pIFY8B2g2h5AP7HVBG9jJR0gP-tjuhKm" # New ID from Macbook Air

# --- Helper: Load Env ---
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

# --- Helper: HTTP Request & Auth ---
def get_access_token(force_refresh=False):
    token = os.environ.get('GOOGLE_ACCESS_TOKEN')
    if token and not force_refresh:
        return token
        
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        # Fail silently or return None to allow graceful degradation
        return None

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
        return None

def request(method, url, data=None, headers=None, retry=True):
    if headers is None: headers = {}
    token = get_access_token()
    if not token: return None
    
    headers['Authorization'] = f'Bearer {token}'
    
    if data and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204: return None
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            get_access_token(force_refresh=True)
            return request(method, url, data, headers, retry=False)
        return None

# --- Drive Helpers ---

def find_subfolder(parent_id, name):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    params = {'q': query, 'fields': 'files(id)'}
    url = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = request('GET', url)
    if data and data.get('files'):
        return data['files'][0]['id']
    return None

def find_file(parent_id, name):
    query = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
    params = {'q': query, 'fields': 'files(id)'}
    url = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = request('GET', url)
    if data and data.get('files'):
        return data['files'][0]['id']
    return None

def read_file_content(file_id):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode('utf-8')
    except:
        return ""

# --- Logic ---

def get_today_filename():
    # Format: YYYY-MM-DD (WeekDay_Chinese).md
    # Match Macbook Air format: 2026-02-20 (五).md
    # Note: Space before bracket
    now = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday_str = weekdays[now.weekday()]
    return f"{now.strftime('%Y-%m-%d')} ({weekday_str}).md"

def read_memory(lines=30):
    # Try to find memory folder: Use MEMORY_ROOT_ID directly
    # This bypasses the search for "Gaa_Archive/Memory/Daily" and goes straight to "memory"
    
    filename = get_today_filename()
    file_id = find_file(MEMORY_ROOT_ID, filename)
    
    if not file_id:
        return f"No shared memory for today ({filename}) in folder {MEMORY_ROOT_ID}."
    
    if not file_id:
        return f"No shared memory for today ({filename})."
        
    content = read_file_content(file_id)
    if not content:
        return "(Empty memory file)"
        
    # Return last N lines
    all_lines = content.splitlines()
    return '\n'.join(all_lines[-lines:])

if __name__ == "__main__":
    print(read_memory())
