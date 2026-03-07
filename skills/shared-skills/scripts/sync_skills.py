#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
import argparse

# --- Configuration ---
# Target Drive Folder ID for "gaa_all" (from MEMORY.md)
GAA_ALL_ID = "1gEZZ2n78Ee5SGdeoNkcIzl0I1u9KrJj9" 
LOCAL_SKILLS_ROOT = "/home/node/.openclaw/workspace/skills"

# --- Helper: Load Env ---
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    # Only set if not already set (allow override)
                    if parts[0] not in os.environ:
                        os.environ[parts[0]] = parts[1]

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

# --- Helper: HTTP Request ---
def get_access_token(force_refresh=False):
    token = os.environ.get('GOOGLE_ACCESS_TOKEN')
    if token and not force_refresh:
        return token
        
    # Attempt to refresh token using config env vars
    print("🔄 Refreshing access token...")
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("Error: Missing OAuth credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN).")
        # Fallback to existing token if available, even if stale
        if token: return token
        sys.exit(1)

    url = "https://oauth2.googleapis.com/token"
    # data encoded as application/x-www-form-urlencoded
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')
    
    # Headers should NOT be JSON for token endpoint usually, but let's check
    # Google token endpoint expects POST with form data
    
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        # Explicitly set content type
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req) as resp:
            body = json.load(resp)
            new_token = body.get('access_token')
            if new_token:
                print(f"✅ Token refreshed successfully. Expires in {body.get('expires_in')}s")
                os.environ['GOOGLE_ACCESS_TOKEN'] = new_token
                return new_token
    except Exception as e:
        print(f"Token refresh failed: {e}")
        try:
            # Fallback: Read full error
            if hasattr(e, 'read'):
                print(f"Refresh error details: {e.read().decode()}")
        except:
            pass
        
    print("Error: detailed authentication required.")
    # Fallback to existing token if refresh fails
    if token: return token
    sys.exit(1)

def request(method, url, data=None, headers=None, retry_auth=True):
    if headers is None: headers = {}
    headers['Authorization'] = f'Bearer {get_access_token()}'
    
    if data and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry_auth:
            print("⚠️ 401 Unauthorized. Retrying with forced token refresh...")
            # Force refresh
            get_access_token(force_refresh=True)
            # Update header with new token
            headers['Authorization'] = f'Bearer {get_access_token()}'
            # Recreate request
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req) as resp:
                    return json.load(resp)
            except urllib.error.HTTPError as e2:
                if hasattr(e2, 'read'):
                    print(f"HTTP Error {e2.code} after refresh: {e2.read().decode()}")
                else:
                    print(f"HTTP Error {e2.code} after refresh.")
                return None
        
        if hasattr(e, 'read'):
            print(f"HTTP Error {e.code}: {e.read().decode()}")
        else:
            print(f"HTTP Error {e.code}")
        return None

# --- Drive API (urllib version) ---

def find_subfolder(parent_id, name):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    params = {'q': query, 'fields': 'files(id, name)'}
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
            print(f"Creating Drive folder: {folder}")
            found = create_folder(current_id, folder)
        current_id = found
    return current_id

def upload_file(parent_id, local_path):
    filename = os.path.basename(local_path)
    
    # 1. Check if file exists
    query = f"name = '{filename}' and '{parent_id}' in parents and trashed = false"
    params = {'q': query, 'fields': 'files(id)'}
    url_list = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = request('GET', url_list)
    existing_file = data['files'][0] if data and data.get('files') else None

    # 2. Prepare content
    # Simple upload (uploadType=media) for small text files
    # For simplicity in this env, we assume files are small text/code
    with open(local_path, 'rb') as f:
        content = f.read()
        
    if existing_file:
        file_id = existing_file['id']
        url_update = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
        request('PATCH', url_update, data=content, headers={'Content-Type': 'text/plain'}) # Generic type
        print(f"Updated: {filename}")
    else:
        # Create metadata first
        url_create_meta = "https://www.googleapis.com/drive/v3/files"
        meta = {'name': filename, 'parents': [parent_id]}
        file_data = request('POST', url_create_meta, data=json.dumps(meta).encode('utf-8'))
        
        if file_data:
            file_id = file_data['id']
            # Upload content
            url_upload = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
            request('PATCH', url_upload, data=content, headers={'Content-Type': 'text/plain'})
            print(f"Uploaded: {filename}")

# --- Core Logic ---

def push_skill(skill_name):
    print(f"🚀 Pushing skill: {skill_name}...")
    local_skill_path = os.path.join(LOCAL_SKILLS_ROOT, skill_name)
    if not os.path.exists(local_skill_path):
        print(f"Error: Skill '{skill_name}' not found locally.")
        return

    # 1. Ensure remote path: gaa_all/Agent_System/skills/<skill_name>
    skills_root_id = ensure_path(['Agent_System', 'skills'], GAA_ALL_ID)
    skill_folder_id = ensure_path([skill_name], skills_root_id)
    
    # 2. Upload recursively
    for root, dirs, files in os.walk(local_skill_path):
        rel_path = os.path.relpath(root, local_skill_path)
        
        if rel_path == ".":
            current_drive_id = skill_folder_id
        else:
            subfolders = rel_path.split(os.sep)
            current_drive_id = ensure_path(subfolders, skill_folder_id)
            
        for file in files:
            if file.startswith('.') or file == "__pycache__": continue
            full_path = os.path.join(root, file)
            upload_file(current_drive_id, full_path)

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    params = {'q': query, 'fields': 'files(id, name, mimeType)'}
    url = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = request('GET', url)
    return data['files'] if data and data.get('files') else []

def download_file(file_id, local_path):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            with open(local_path, 'wb') as f:
                f.write(content)
            print(f"Downloaded: {os.path.basename(local_path)}")
    except urllib.error.HTTPError as e:
        print(f"Error downloading file {file_id}: {e}")

def pull_skill(skill_name):
    print(f"⬇️ Pulling skill: {skill_name}...")
    skills_root_id = ensure_path(['Agent_System', 'skills'], GAA_ALL_ID)
    
    # 1. Find skill folder
    skill_folder_id = find_subfolder(skills_root_id, skill_name)
    if not skill_folder_id:
        print(f"Error: Skill '{skill_name}' not found on Drive.")
        return

    # 2. Recursive download
    local_skill_root = os.path.join(LOCAL_SKILLS_ROOT, skill_name)
    if not os.path.exists(local_skill_root):
        os.makedirs(local_skill_root)
        
    def download_recursive(folder_id, local_dir):
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
            
        items = list_files_in_folder(folder_id)
        for item in items:
            name = item['name']
            mime = item['mimeType']
            item_id = item['id']
            
            if mime == 'application/vnd.google-apps.folder':
                download_recursive(item_id, os.path.join(local_dir, name))
            else:
                download_file(item_id, os.path.join(local_dir, name))

    download_recursive(skill_folder_id, local_skill_root)
    print(f"✅ Skill '{skill_name}' pulled successfully.")

def list_remote_skills():
    print("☁️ Checking Google Drive for existing skills...")
    skills_root_id = ensure_path(['Agent_System', 'skills'], GAA_ALL_ID)
    query = f"'{skills_root_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    params = {'q': query, 'fields': 'files(name)'}
    url = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = request('GET', url)
    
    if data and data.get('files'):
        for f in data['files']:
            print(f" - {f['name']}")
    else:
        print(" (No skills found on Drive)")

# --- Main ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['push', 'pull', 'list'])
    parser.add_argument('skill', nargs='?', help='Name of the skill')
    args = parser.parse_args()
    
    if args.action == 'push':
        if args.skill == 'all':
            print("🚀 Pushing ALL skills...")
            for item in os.listdir(LOCAL_SKILLS_ROOT):
                item_path = os.path.join(LOCAL_SKILLS_ROOT, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    push_skill(item)
        elif args.skill:
            push_skill(args.skill)
        else:
            print("Please specify a skill name to push (or 'all').")
    elif args.action == 'list':
        list_remote_skills()
    elif args.action == 'pull':
        if args.skill == 'all':
            print("Pulling ALL skills...")
            skills_root_id = ensure_path(['Agent_System', 'skills'], GAA_ALL_ID)
            items = list_files_in_folder(skills_root_id)
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    pull_skill(item['name'])
        elif args.skill:
            pull_skill(args.skill)
        else:
            print("Please specify a skill name to pull (or 'all').")
