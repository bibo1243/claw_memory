#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

BASE_URL = 'https://www.googleapis.com/drive/v3'
UPLOAD_URL = 'https://www.googleapis.com/upload/drive/v3'

def get_access_token():
    token = os.getenv('GOOGLE_ACCESS_TOKEN')
    if not token:
        sys.stderr.write('Error: GOOGLE_ACCESS_TOKEN env var not set\n')
        sys.exit(1)
    return token

def request(method, url, data=None, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {get_access_token()}')
    for k, v in headers.items():
        req.add_header(k, v)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

def create_folder(name, parent_id=None):
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]
    
    return request(
        'POST',
        f'{BASE_URL}/files',
        data=json.dumps(metadata).encode(),
        headers={'Content-Type': 'application/json'}
    )

def list_files(query):
    params = {'q': query}
    return request('GET', f'{BASE_URL}/files?{urllib.parse.urlencode(params)}')

def ensure_folder(name, parent_id=None):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
        
    results = list_files(query)
    files = results.get('files', [])
    
    if files:
        print(f"Folder '{name}' already exists with ID: {files[0]['id']}")
        return files[0]['id']
    else:
        print(f"Creating folder '{name}'...")
        folder = create_folder(name, parent_id)
        print(f"Created folder '{name}' with ID: {folder['id']}")
        return folder['id']

def upload_file(local_path, parent_id=None, mime_type='application/octet-stream'):
    filename = os.path.basename(local_path)
    
    # Check if file exists to update instead of create duplicate
    query = f"name='{filename}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    existing_files = list_files(query).get('files', [])
    
    if existing_files:
        file_id = existing_files[0]['id']
        print(f"Updating existing file '{filename}' (ID: {file_id})...")
        method = 'PATCH'
        url = f"{UPLOAD_URL}/files/{file_id}?uploadType=multipart"
    else:
        print(f"Uploading new file '{filename}'...")
        method = 'POST'
        url = f"{UPLOAD_URL}/files?uploadType=multipart"

    metadata = {'name': filename}
    if parent_id and not existing_files:
        metadata['parents'] = [parent_id]
    
    boundary = '-------314159265358979323846'
    delimiter = f"\r\n--{boundary}\r\n"
    close_delim = f"\r\n--{boundary}--"
    
    with open(local_path, 'rb') as f:
        file_content = f.read()
        
    body = (
        delimiter +
        'Content-Type: application/json\r\n\r\n' +
        json.dumps(metadata) +
        delimiter +
        f'Content-Type: {mime_type}\r\n\r\n'
    ).encode('utf-8') + file_content + close_delim.encode('utf-8')

    req = urllib.request.Request(url, data=body, method=method)
    req.add_header('Authorization', f'Bearer {get_access_token()}')
    req.add_header('Content-Type', f'multipart/related; boundary="{boundary}"')
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            print(f"Successfully uploaded '{filename}' (ID: {result['id']})")
            return result
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: google_drive.py <command> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'ensure_folder':
        if len(sys.argv) < 3:
            print("Usage: google_drive.py ensure_folder <folder_name> [parent_id]")
            sys.exit(1)
        ensure_folder(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == 'list_files':
        if len(sys.argv) < 3:
            print("Usage: google_drive.py list_files <query>")
            sys.exit(1)
        results = list_files(sys.argv[2])
        print(json.dumps(results, indent=2))
    elif cmd == 'upload_file':
        if len(sys.argv) < 3:
            print("Usage: google_drive.py upload_file <local_path> [parent_id] [mime_type]")
            sys.exit(1)
        upload_file(
            sys.argv[2], 
            sys.argv[3] if len(sys.argv) > 3 else None,
            sys.argv[4] if len(sys.argv) > 4 else 'application/octet-stream'
        )
    else:
        print(f"Unknown command: {cmd}")
