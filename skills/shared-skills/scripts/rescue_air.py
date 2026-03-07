#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse

# Config
GAA_ALL_ID = "1gEZZ2n78Ee5SGdeoNkcIzl0I1u9KrJj9" 

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

def find_file_recursive(parent_id, target_name):
    query = f"'{parent_id}' in parents and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}&fields=files(id,name,mimeType)"
    data = request('GET', url)
    
    if not data or not data.get('files'): return None
    
    for f in data['files']:
        if f['name'] == target_name:
            return f['id']
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            # Search inside folder
            found = find_file_recursive(f['id'], target_name)
            if found: return found
    return None

def main():
    target_files = ['sync_skills.py', 'list_memories.py']
    print("🔎 Searching for rescue files...")
    
    # Start search from gaa_all root
    skills_root = find_file_recursive(GAA_ALL_ID, 'Agent_System') # Find Agent_System first for speed
    if not skills_root: skills_root = GAA_ALL_ID
    
    for filename in target_files:
        fid = find_file_recursive(skills_root, filename)
        if fid:
            print(f"📄 Found {filename}: {fid}")
        else:
            print(f"❌ Could not find {filename}")

if __name__ == "__main__":
    main()
