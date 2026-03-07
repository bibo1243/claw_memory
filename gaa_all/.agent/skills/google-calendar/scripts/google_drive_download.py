#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

BASE_URL = 'https://www.googleapis.com/drive/v3'

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
            return resp.read()
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

def download_file(file_id):
    url = f"{BASE_URL}/files/{file_id}?alt=media"
    return request('GET', url)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: google_drive_download.py <file_id>")
        sys.exit(1)
    
    file_id = sys.argv[1]
    content = download_file(file_id)
    print(content.decode('utf-8'))
