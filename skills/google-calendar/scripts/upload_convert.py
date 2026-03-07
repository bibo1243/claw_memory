#!/usr/bin/env python3
import os, sys, json, urllib.request

BASE_URL = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart'

def get_access_token():
    token = os.getenv('GOOGLE_ACCESS_TOKEN')
    if not token:
        sys.stderr.write('Error: GOOGLE_ACCESS_TOKEN env var not set\n')
        sys.exit(1)
    return token

def upload_and_convert(local_path, parent_id=None):
    filename = os.path.basename(local_path)
    
    metadata = {
        'name': filename,
        'mimeType': 'application/vnd.google-apps.spreadsheet' # Convert to Google Sheet
    }
    if parent_id:
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
        'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n'
    ).encode('utf-8') + file_content + close_delim.encode('utf-8')

    req = urllib.request.Request(BASE_URL, data=body, method='POST')
    req.add_header('Authorization', f'Bearer {get_access_token()}')
    req.add_header('Content-Type', f'multipart/related; boundary="{boundary}"')
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: upload_convert.py <local_path> <parent_id>")
        sys.exit(1)
    
    res = upload_and_convert(sys.argv[1], sys.argv[2])
    print(json.dumps(res, indent=2))
