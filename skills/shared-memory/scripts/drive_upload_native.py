#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
import mimetypes
import uuid

# Configuration
# Drive folder ID for "gaa_all"
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

API_URL = "https://www.googleapis.com/drive/v3/files"
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"

def request(method, url, headers, data=None):
    req = urllib.request.Request(url, headers=headers, method=method, data=data)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None

def find_file(name, parent_id, mime_type=None):
    q = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
    if mime_type:
        q += f" and mimeType = '{mime_type}'"
    
    params = {'q': q, 'fields': 'files(id, name)'}
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    res = request('GET', url, headers)
    if res and res.get('files'):
        return res['files'][0]['id']
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
    res = request('POST', API_URL, headers, json.dumps(body).encode('utf-8'))
    if res:
        print(f"Created folder: {name}")
        return res['id']
    return None

def upload_file(local_path, parent_id):
    filename = os.path.basename(local_path)
    
    # Check if exists (simple update logic: delete and re-upload or just skip? 
    # For now, let's skip if exists to save time/bandwidth, or overwrite?
    # Let's find existing ID.
    existing_id = find_file(filename, parent_id)
    
    if existing_id:
        # Update is complex with multipart in urllib manually. 
        # Easier to just skip or delete+create. 
        # Let's skip for now unless forced.
        print(f"Skipping {filename} (already exists)")
        return

    boundary = f'-------{uuid.uuid4()}'
    delimiter = f'--{boundary}'
    close_delim = f'--{boundary}--'
    
    mime_type, _ = mimetypes.guess_type(local_path)
    if not mime_type: mime_type = 'application/octet-stream'
    
    metadata = {
        'name': filename,
        'parents': [parent_id]
    }
    
    with open(local_path, 'rb') as f:
        file_content = f.read()
        
    # Construct multipart body
    body = []
    body.append(delimiter.encode('utf-8'))
    body.append(b'Content-Type: application/json; charset=UTF-8\r\n')
    body.append(json.dumps(metadata).encode('utf-8'))
    body.append(b'\r\n')
    
    body.append(delimiter.encode('utf-8'))
    body.append(f'Content-Type: {mime_type}\r\n'.encode('utf-8'))
    body.append(b'\r\n')
    body.append(file_content)
    body.append(b'\r\n')
    
    body.append(close_delim.encode('utf-8'))
    
    payload = b''.join(body)
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': f'multipart/related; boundary={boundary}'
    }
    
    res = request('POST', UPLOAD_URL, headers, payload)
    if res:
        print(f"Uploaded: {filename}")

def main():
    print("Starting sync to Drive...")
    
    # Structure: gaa_all > .agent > skills
    agent_id = create_folder('.agent', ROOT_FOLDER_ID)
    if not agent_id: return
    
    skills_id = create_folder('skills', agent_id)
    if not skills_id: return
    
    # Sync skills
    for item in os.listdir(LOCAL_SKILLS_DIR):
        item_path = os.path.join(LOCAL_SKILLS_DIR, item)
        if os.path.isdir(item_path):
            # Skill folder
            print(f"Processing skill: {item}")
            skill_folder_id = create_folder(item, skills_id)
            
            # Upload contents (recursive would be better, but doing 1 level + scripts for now)
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
