#!/usr/bin/env python3
import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# Configuration
FOLDER_ID = "1gEZZ2n78Ee5SGdeoNkcIzl0I1u9KrJj9"  # gaa_all folder ID from memory
SHARED_SKILLS_PATH = "/home/node/.openclaw/workspace/gaa_all/.agent/skills"

# Load creds from env manually
def get_service():
    token = os.environ.get('GOOGLE_ACCESS_TOKEN')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if not token:
        print("No token found")
        sys.exit(1)
        
    creds = Credentials(
        token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    return build('drive', 'v3', credentials=creds)

def find_or_create_folder(service, name, parent_id):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        return files[0]['id']
    else:
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        file = service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

def upload_file(service, file_path, parent_id):
    file_name = os.path.basename(file_path)
    # Check if exists to update or create
    query = f"name = '{file_name}' and '{parent_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])
    
    media = MediaFileUpload(file_path, resumable=True)
    
    if files:
        # Update
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Updated {file_name}")
    else:
        # Create
        file_metadata = {'name': file_name, 'parents': [parent_id]}
        service.files().create(body=file_metadata, media_body=media).execute()
        print(f"Uploaded {file_name}")

def sync_skills_to_drive():
    service = get_service()
    
    # 1. Find/Create .agent inside gaa_all
    agent_id = find_or_create_folder(service, '.agent', FOLDER_ID)
    
    # 2. Find/Create skills inside .agent
    skills_id = find_or_create_folder(service, 'skills', agent_id)
    
    # 3. Walk through local skills and upload
    # Note: This simple version uploads files but doesn't recursively creating deep nested folders yet for simplicity,
    # or we iterate top-level skills.
    # Let's iterate top-level skill directories in workspace/skills
    
    local_skills_root = "/home/node/.openclaw/workspace/skills"
    
    for skill_name in os.listdir(local_skills_root):
        skill_path = os.path.join(local_skills_root, skill_name)
        if os.path.isdir(skill_path):
            # Create skill folder in Drive
            drive_skill_id = find_or_create_folder(service, skill_name, skills_id)
            
            # Upload files inside (SKILL.md, scripts, etc.)
            # Just doing one level deep for now + scripts folder
            for item in os.listdir(skill_path):
                item_path = os.path.join(skill_path, item)
                if os.path.isfile(item_path):
                    upload_file(service, item_path, drive_skill_id)
                elif os.path.isdir(item_path) and item == "scripts":
                    scripts_id = find_or_create_folder(service, 'scripts', drive_skill_id)
                    for script in os.listdir(item_path):
                        script_path = os.path.join(item_path, script)
                        if os.path.isfile(script_path):
                            upload_file(service, script_path, scripts_id)

if __name__ == "__main__":
    # Ensure env is loaded
    sys.path.append(os.path.dirname(__file__)) # Allow importing if needed
    # We rely on env vars being set by the caller or previously loaded in session
    # Let's manually load env again to be safe
    def load_env(file_path):
        if not os.path.exists(file_path): return
        with open(file_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        os.environ[parts[0]] = parts[1]
    
    load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))
    
    try:
        sync_skills_to_drive()
        print("Sync complete.")
    except Exception as e:
        print(f"Sync failed: {e}")
