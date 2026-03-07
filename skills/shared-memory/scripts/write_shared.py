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
            if resp.status == 204: return None
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            get_access_token(force_refresh=True)
            return request(method, url, data, headers, retry=False)
        # 404 is not always an error (e.g. file not found search)
        if e.code == 404: return None
        print(f"HTTP Error {e.code}: {e.read().decode()}")
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
    except Exception as e:
        print(f"Read error: {e}")
        return ""

def append_to_file(file_id, new_content):
    # Drive API doesn't support append directly for media.
    # We must read, append, and update.
    # For efficiency in "short term memory", files are daily, so size is manageable.
    current_content = read_file_content(file_id)
    updated_content = current_content + new_content
    
    url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
    request('PATCH', url, data=updated_content.encode('utf-8'), headers={'Content-Type': 'text/plain'})

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

# --- Logic ---

def get_today_filename():
    # Format: YYYY-MM-DD (WeekDay_Chinese).md
    # Match Macbook Air format: 2026-02-20 (五).md
    # Note: Space before bracket
    now = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday_str = weekdays[now.weekday()]
    return f"{now.strftime('%Y-%m-%d')} ({weekday_str}).md"

def get_individual_memory_path(bot_name):
    # Base memory folder
    memory_root_id = MEMORY_ROOT_ID
    
    # Create/Find individual folder
    # Folder name: GaaClaw_Memory or MacbookAir_Memory
    individual_folder_name = f"{bot_name}_Memory"
    folder_id = find_subfolder(memory_root_id, individual_folder_name)
    
    if not folder_id:
        print(f"Creating individual memory folder: {individual_folder_name}")
        folder_id = create_folder(memory_root_id, individual_folder_name)
        
    return folder_id

def write_memory(bot_name, message, role="Assistant"):
    # ... (Shared memory logic remains same) ...
        
    # 2. Write to Individual Daily Log (Private to this bot)
    individual_folder_id = get_individual_memory_path(bot_name)
    individual_filename = get_today_filename()
    individual_file_id = find_file(individual_folder_id, individual_filename)
    
    # Rename roles per Gary's request
    display_role = role
    if role == "User":
        display_role = "Gary本尊"
    elif role == "Assistant":
        if "GaaClaw" in bot_name or "gaa1243" in bot_name:
            display_role = "線上Gaa"
        elif "Macbook" in bot_name or "air" in bot_name.lower():
            display_role = "macbook air Gaa"
        else:
            display_role = bot_name # Fallback
            
    # Format: Clean, single line (or block) prepended to top (Reverse Chronological)
    # Using timestamped block format for readability
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry_line = f"**[{timestamp}] {display_role}:** {message}\n\n---\n\n"
    
    if individual_file_id:
        current_content = read_file_content(individual_file_id)
        # Prepend new entry to make it "Recent at Top" (倒敘)
        new_content = entry_line + current_content
        
        # Update file (overwrite with new content)
        url = f"https://www.googleapis.com/upload/drive/v3/files/{individual_file_id}?uploadType=media"
        request('PATCH', url, data=new_content.encode('utf-8'), headers={'Content-Type': 'text/plain'})
        print(f"✅ Prepend to Individual Memory: {individual_filename}")
    else:
        header = f"# {bot_name} Log: {individual_filename}\n\n"
        create_file(individual_folder_id, individual_filename, header + entry_line)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 write_shared.py <bot_name> <message> [role]")
        sys.exit(1)
        
    bot_name = sys.argv[1]
    message = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "Assistant"
    
    write_memory(bot_name, message, role)
