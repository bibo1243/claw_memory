#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
import mimetypes

# Configuration
ROOT_FOLDER_ID = "1gEZZ2n78Ee5SGdeoNkcIzl0I1u9KrJj9" 
LOCAL_SKILLS_DIR = "/home/node/.openclaw/workspace/skills"

# Load Env
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    os.environ[parts[0]] = parts[1]

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))
TOKEN = os.environ.get('GOOGLE_ACCESS_TOKEN')

if not TOKEN:
    print("No GOOGLE_ACCESS_TOKEN")
    sys.exit(1)

FILES_API_URL = "https://www.googleapis.com/drive/v3/files"
UPLOAD_API_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable"

def request(method, url, headers, data=None):
    req = urllib.request.Request(url, headers=headers, method=method, data=data)
    try:
        resp = urllib.request.urlopen(req)
        return resp
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None

def get_json_response(resp):
    if resp:
        # Check if response has content
        content = resp.read().decode('utf-8')
        if content:
            return json.loads(content)
    return None

def find_file(name, parent_id, mime_type=None):
    q = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
    if mime_type:
        q += f" and mimeType = '{mime_type}'"
    
    params = {'q': q, 'fields': 'files(id, name)'}
    url = f"{FILES_API_URL}?{urllib.parse.urlencode(params)}"
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    resp = request('GET', url, headers)
    data = get_json_response(resp)
    if data and data.get('files'):
        return data['files'][0]['id']
    return None

def create_folder(name, parent_id):
    existing = find_file(name, parent_id, 'application/vnd.google-apps.folder')
    if existing:
        return existing
        
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    body = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    resp = request('POST', FILES_API_URL, headers, json.dumps(body).encode('utf-8'))
    data = get_json_response(resp)
    if data:
        print(f"Created folder: {name}")
        return data['id']
    return None

def upload_file(local_path, parent_id):
    filename = os.path.basename(local_path)
    # Simple check: skip if exists
    if find_file(filename, parent_id):
        print(f"Skipping {filename} (exists)")
        return

    file_size = os.path.getsize(local_path)
    mime_type, _ = mimetypes.guess_type(local_path)
    if not mime_type: mime_type = 'application/octet-stream'
    
    # 1. Init Session
    metadata = {
        'name': filename,
        'parents': [parent_id]
    }
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
        'X-Upload-Content-Type': mime_type,
        'X-Upload-Content-Length': str(file_size)
    }
    
    resp = request('POST', UPLOAD_API_URL, headers, json.dumps(metadata).encode('utf-8'))
    if not resp: return
    
    upload_url = resp.headers.get('Location')
    if not upload_url:
        print("Failed to get upload URL")
        return
        
    # 2. Upload File
    with open(local_path, 'rb') as f:
        file_data = f.read()
        
    put_headers = {
        'Content-Type': mime_type,
        'Content-Length': str(file_size)
    }
    
    resp_put = request('PUT', upload_url, put_headers, file_data)
    if resp_put and resp_put.code in [200, 201]:
        print(f"Uploaded: {filename}")
    else:
        print(f"Failed to upload {filename}")

def main():
    print("Starting sync (Resumable)...")
    
    agent_id = create_folder('.agent', ROOT_FOLDER_ID)
    if not agent_id: return
    
    skills_id = create_folder('skills', agent_id)
    if not skills_id: return
    
    for item in os.listdir(LOCAL_SKILLS_DIR):
        item_path = os.path.join(LOCAL_SKILLS_DIR, item)
        if os.path.isdir(item_path):
            print(f"Processing: {item}")
            skill_folder_id = create_folder(item, skills_id)
            
            for sub in os.listdir(item_path):
                sub_path = os.path.join(item_path, sub)
                if os.path.isfile(sub_path):
                    upload_file(sub_path, skill_folder_id)
                elif os.path.isdir(sub_path) and sub == 'scripts':
                    scripts_id = create_folder('scripts', skill_folder_id)
                    for script in os.listdir(sub_path):
                        script_path = os.path.join(sub_path, script)
                        if os.path.isfile(script_path):
                            upload_file(script_path, scripts_id)

if __name__ == "__main__":
    main()
