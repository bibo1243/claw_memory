#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

# --- Configuration ---
GAA_ALL_ID = "1gEZZ2n78Ee5SGdeoNkcIzl0I1u9KrJj9" 

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
        print("Error: Missing OAuth credentials.")
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
    except Exception as e:
        print(f"Token refresh failed: {e}")
        sys.exit(1)

def request(method, url, data=None, headers=None, retry=True):
    if headers is None: headers = {}
    headers['Authorization'] = f'Bearer {get_access_token()}'
    
    if data and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            get_access_token(force_refresh=True)
            return request(method, url, data, headers, retry=False)
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None

# --- Drive API ---

def find_subfolder(parent_id, name):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    params = {'q': query, 'fields': 'files(id)'}
    url = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = request('GET', url)
    if data and data.get('files'):
        return data['files'][0]['id']
    return None

def create_folder(parent_id, name):
    url = "https://www.googleapis.com/drive/v3/files"
    body = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    data = request('POST', url, data=json.dumps(body).encode('utf-8'))
    return data['id'] if data else None

def ensure_path(path_list, root_id):
    current_id = root_id
    for folder in path_list:
        found = find_subfolder(current_id, folder)
        if not found:
            found = create_folder(current_id, folder)
        current_id = found
    return current_id

def create_file(parent_id, name, content):
    # Metadata
    url_meta = "https://www.googleapis.com/drive/v3/files"
    meta = {'name': name, 'parents': [parent_id], 'mimeType': 'text/plain'}
    file_data = request('POST', url_meta, data=json.dumps(meta).encode('utf-8'))
    
    if file_data:
        file_id = file_data['id']
        # Content
        url_upload = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
        request('PATCH', url_upload, data=content.encode('utf-8'), headers={'Content-Type': 'text/plain'})
        return file_id
    return None

# --- Main Test ---

def test_upload():
    print("Testing direct upload to Drive...")
    
    # Target: gaa_all/Agent_System/skills/
    skills_root_id = ensure_path(['Agent_System', 'skills'], GAA_ALL_ID)
    
    # File: gaa1243_bot.txt
    filename = "gaa1243_bot.txt"
    content = f"Identity: gaa1243_bot (Cloud)\nTimestamp: {datetime.now().isoformat()}\nStatus: Online & Synced"
    
    file_id = create_file(skills_root_id, filename, content)
    
    if file_id:
        print(f"✅ Success! Created file '{filename}' in 'gaa_all/Agent_System/skills/'")
        print(f"File ID: {file_id}")
    else:
        print("❌ Upload failed.")

if __name__ == "__main__":
    test_upload()
